"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import os
import re
import warnings

# Third Party Libraries
import pandas as pd
from loguru import logger

# Local Libraries
from . import airac, builder, functions, lists

# This is needed to supress 'xml as html' warnings with bs4
warnings.filterwarnings("ignore", category=UserWarning)

# Define a few decorators
def parse_table(section:str, match:str=".+") -> None:
    """A decorator to parse the given section"""
    def decorator_func(func):
        def wrapper(self, *args, **kwargs):
            logger.info(f"Parsing {section} data...")
            tables = self.get_table(section, match)
            if tables:
                dataframe = func(self, tables, *args, **kwargs)
                if isinstance(dataframe, pd.DataFrame):
                    # If a single dataframe is passed
                    dataframe.to_csv(f"{functions.work_dir}\\DataFrames\\{section}.csv")
                elif isinstance(dataframe, list):
                    # If a list of dataframes are passed
                    for idx, dfl in enumerate(dataframe):
                        dfl.to_csv(f"{functions.work_dir}\\DataFrames\\{section}_{idx}.csv")
                else:
                    raise TypeError("No pandas dataframe or list was found")
            else:
                raise functions.NoUrlDataFoundError(section)
        return wrapper
    return decorator_func

class Webscrape:
    """Class to scrape data from the given AIRAC eAIP URL"""

    def __init__(
            self,
            next_cycle:bool=True,
            country_code:str="EG",
            date_in=0,
            debug:bool=False
            ) -> None:
        airac_cycle = airac.Airac()
        self.cycle_url = airac_cycle.url(next_cycle=next_cycle, date_in=date_in)
        self.debug = debug

        # Validate the entry for country_code
        if re.match(r"^[A-Z]{2}$", country_code.upper()):
            self.country = country_code.upper()
            self.language = lists.country_codes[self.country]
        else:
            raise ValueError("Expected a two character country code such as 'EG'")

        # Setup the builder
        self.build = builder.KiloJuliett()
        # Use default settings
        self.build.settings()
        # Set the data
        self.date_in = date_in
        # Setup Tacan to VOR/ILS conversion
        self.tacan_vor = functions.TacanVor()
        # Prepare regex searches
        self.regex = lists.Regex()
        # Define at which FL an airway should be marked as 'uppper'
        self.airway_split = 245

    def run(self, download_first:bool=True, no_build:bool=False) -> None:
        """Runs the full webscrape"""

        self.parse_ad_1_3()
        self.process_enr_2(download_first=download_first, no_build=no_build)
        self.process_enr_3(download_first=download_first, no_build=no_build)
        self.process_enr_4(download_first=download_first, no_build=no_build)

    def url_suffix(self, section:str) -> str:
        """Returns a url suffix formatted for the European eAIP standard"""
        return str(f"{self.country}-{section}-{self.language}.html")

    def get_table(self, section:str, match:str=".+") -> list:
        """Gets a table from the given url as a list of dataframes"""

        # Combine the airac cycle url with the page being scraped
        address = self.cycle_url + self.url_suffix(section=section)
        logger.debug(address)

        try:
            # Read the full address into a list of dataframes
            tables = pd.read_html(address, flavor="bs4", match=match)

            # Debug functions
            if self.debug:
                # Outputs any found tables to csv files
                for index, table in enumerate(tables):
                    table.to_csv(f"{functions.work_dir}\\Debug\\{section}_{index}.csv")

            # If there is a least one table
            if len(tables) > 0:
                return tables
            else:
                raise functions.NoUrlDataFoundError(address)
        except ValueError as error:
            logger.warning(f"{error} for {address}")

    @staticmethod
    def generate_file_names(file_start:str, file_type:str="csv") -> list:
        """Generates an incremental list of filenames"""

        path = f"{functions.work_dir}\\DataFrames\\"
        enr_files = ([file for file in os.listdir(path) if
                      file.startswith(file_start) and file.endswith(file_type)])
        return enr_files

    @parse_table("AD-1.3")
    def parse_ad_1_3(self, tables:list=None) -> pd.DataFrame:
        """Process data from AD 1.3 - INDEX TO AERODROMES AND HELIPORTS"""

        tdf = tables[0]

        # Modify header row
        column_headers = [
            "location",
            "icao_designator",
            "d1",
            "d2",
            "d3",
            "d4"
        ]
        tdf.columns = column_headers

        # Name the columns to keep
        tdf = tdf[["location", "icao_designator"]]

        # Drop any rows where the word 'Aerodrome' or 'Heliport' are the icao_designator
        tdf = tdf[~tdf["icao_designator"].isin(['Aerodrome', 'Heliport'])]
        tdf = tdf[~tdf["location"].str.startswith('Aerodrome')]

        # Reset the index
        tdf.reset_index(drop=True, inplace=True)

        return tdf

    @parse_table("ENR-2.1")
    def parse_enr_2_1(self, tables:list=None) -> list:
        """Pull data from ENR 2.1 - AIR TRAFFIC SERVICES AIRSPACE"""

        # The data object table[0] is for FIR, UIR, TMA and CTA
        fir_uir_tma_cta = tables[0]
        # The data object table[1] is for CTR
        ctr = tables[1]
        # Modify header row
        fir_uir_tma_cta.columns = lists.column_headers_airspace
        ctr.columns = lists.column_headers_airspace

        return [fir_uir_tma_cta, ctr]

    @parse_table("ENR-2.2")
    def parse_enr_2_2(self, tables:list=None) -> list:
        """Pull data from ENR 2.2 - OTHER REGULATED AIRSPACE"""

        # The data object table[0] is for ATZ
        atz = tables[0]
        # The data object table[27] is for FRA
        fra = tables[27]
        # The data object table[28] is for Channel Islands Airspace
        cia = tables[28]

        # Modify header rows
        column_headers = [
            "lateral_limits",
            "vertical_limits",
            "remarks"
        ]

        atz.columns = lists.column_headers_airspace
        fra.columns = column_headers
        cia.columns = column_headers

        return [atz, fra, cia]

    @parse_table("ENR-3.2", "Route Designator")
    def parse_enr_3_2(self, tables:list=None) -> list:
        """Pull data from ENR 3.2 - AREA NAVIGATION ROUTES"""

        logger.debug(f"Found {len(tables)} ENR-3.2 tables")
        table_out = []

        for table in tables:
            table.columns = lists.column_headers_route
            table.drop(["del1","del2","del3"], axis=1)
            table_out.append(table)

        return table_out

    @parse_table("ENR-3.3", "Route Designator")
    def parse_enr_3_3(self, tables:list=None) -> list:
        """Pull data from ENR 3.3 - OTHER ROUTES"""

        logger.debug(f"Found {len(tables)} ENR-3.3 tables")
        table_out = []

        for table in tables:
            table.columns = lists.column_headers_route
            table.drop(["del1","del2","del3"], axis=1)
            table_out.append(table)

        return table_out

    @parse_table("ENR-4.1")
    def parse_enr_4_1(self, tables:list=None) -> pd.DataFrame:
        """Process data from ENR 4.1 - RADIO NAVIGATION AIDS - EN-ROUTE"""

        tdf = tables[0]

        # Modify header row
        column_headers = [
            "name",
            "id",
            "frequency",
            "hrs",
            "coordinates",
            "elev",
            "fra",
            "remarks"
        ]
        tdf.columns = column_headers

        # Name the columns to keep
        tdf = tdf[["name", "id", "frequency", "coordinates"]]

        # Reset the index
        tdf.reset_index(drop=True, inplace=True)

        return tdf

    @parse_table("ENR-4.4")
    def parse_enr_4_4(self, tables:list=None) -> pd.DataFrame:
        """Process data from ENR 4.1 - RADIO NAVIGATION AIDS - EN-ROUTE"""

        tdf = tables[0]

        # Modify header row
        column_headers = [
            "name",
            "coordinates",
            "route",
            "fra",
            "remarks",
        ]
        tdf.columns = column_headers

        # Name the columns to keep
        tdf = tdf[["name", "coordinates"]]

        # Reset the index
        tdf.reset_index(drop=True, inplace=True)

        return tdf

    def search_enr_2_x(self, df_enr_2:pd.DataFrame, file_name:str, no_build:bool=False):
        """Generic ENR 2 search actions"""

        # Start the iterator
        areas = {}
        limits_class = {}
        for index, row in df_enr_2.iterrows():
            if file_name == "ENR-2.2_1":
                # Special case for UK Free Route Airspace
                lat_lim = self.regex.lateral_limits(row["lateral_limits"])
                logger.debug(str(lat_lim[2]).lstrip())
                areas[lat_lim[1]] = str(lat_lim[2]).lstrip()

                ver_lim = self.regex.flight_level(row["vertical_limits"])
                limit_text = f"UK Free Route Airspace from {ver_lim[0]} to {ver_lim[1]}"
                logger.debug(limit_text)
                limits_class[lat_lim[1]] = limit_text
            elif file_name == "ENR-2.2_2":
                # Special case for Channel Islands Airspace
                if re.search(r"\d{6}(\.\d{2})?[NS]{1}", row["lateral_limits"]):
                    title = f"CHANNEL ISLANDS {index}"
                    areas[title] = row["lateral_limits"]
                    logger.debug(row["vertical_limits"])
                    limits_class[title] = row["vertical_limits"]
            else:
                # Check to see if this row contains an area name
                title = re.match(
                    r"^([A-Z\s\-]+(\bFIR\b|\bUIR\b|\bTMA\b|\bCTA\b|\bCTR\b|\bATZ\b|\bFRA\b\s"
                    r"\([A-Z\s]+\))(\s\d{1,2})?)(?:\s\s)",
                    str(row["data"])
                    )
                if title:
                    logger.debug(title[1])
                    # Find the boundary of the area
                    coords = re.search(
                        r"(?<=\s\s)((\d{6}[NS]{1}\s\d{7}[EW]{1}.*)|(\bA\scircle\b.*))"
                        r"(?=\s+\bUpper\b)", row["data"]
                        )
                    if coords:
                        logger.debug(coords[1])
                        areas[title[1]] = coords[1]

                    # Find the lateral limits
                    limits = re.search(
                        r"(?:\s+\bUpper\slimit\:\s\b)(\S+(\s\bFT\b\s\b(ALT|AGL)\b)?)"
                        r"(?:\s+\bLower\slimit\:\s\b)(\S+(\s\bFT\b\s\b(ALT|AGL)\b)?)"
                        r"(?:\s+\bClass\b\:\s)([A-G]{1})", str(row["data"])
                    )
                    # Cleanup the callsign
                    callsign = re.match(r"^([A-Z\s]+)(?:\s+[A-Z]{1}[a-z]+)", str(row['callsign']))
                    # Cleanup the frequency
                    frequency = self.regex.frequency(row["frequency"])
                    if frequency:
                        check_25khz = functions.is_25khz(frequency[1])
                        if check_25khz:
                            logger.warning(f"{frequency[1]} is not a 25KHz frequency!")

                    if limits and coords and callsign and frequency:
                        limit_text = (f"Class {limits[7]} airspace from {limits[4]} to {limits[1]}"
                                    f" - {row['unit']} ({callsign[1].rstrip()}), {frequency[1]}MHz")
                        logger.debug(limit_text)
                        limits_class[title[1]] = limit_text

        output = ""
        last_title = None
        with open(f"{functions.work_dir}\\DataFrames\\{file_name}_AIRSPACE.sct",
            "w", encoding="utf-8") as file:
            for idx, loc in areas.items():
                # Request data
                if no_build:
                    sct_data = f"The 'no build' option has been selected...\n{loc}"
                else:
                    sct_data = self.build.request_output(loc)

                # Add comments into the sct output
                this_title = re.match(r"^([A-Z\s\/]+)", str(idx))
                if this_title[1] != last_title:
                    file.write(output)
                    output = ""
                    output = f"{output}\n; {this_title[1]}"

                try:
                    lco = limits_class[idx]
                except KeyError as error:
                    logger.warning(f"Unable to locate limits and class for {error}")
                    lco = "WARNING! Unable to locate limits and class"

                output = f"{output}\n; {idx} - {lco}\n{sct_data}\n"
                last_title = this_title[1]
            file.write(output)

    def search_enr_3_x(self, df_enr_3:pd.DataFrame) -> list:
        """Generic ENR 3 search actions"""

        def write_to_file(route:str, is_upper:bool):
            split_route = route.split(" ")
            route_len = len(split_route)
            logger.debug(f"{is_upper} {split_route}")
            start = 1
            if len(split_route) > 2:
                if split_route[2] == "NCS!":
                    start = 3

            if is_upper:
                uorl = "UPPER"
            else:
                uorl = "LOWER"

            with open(f"{functions.work_dir}\\DataFrames\\ENR-3.2-{uorl}-{split_route[0]}.txt",
                "w", encoding="utf-8") as file:
                for idx in range(start, route_len-1, 1):
                    if (idx + 1) < route_len:
                        # If the point is only 3 characters, it needs padding with 2 extra spaces
                        if len(split_route[idx]) == 3:
                            point = f"{split_route[idx]}  "
                        else:
                            point = split_route[idx]
                        if len(split_route[idx+1]) == 3:
                            point_plus = f"{split_route[idx+1]}  "
                        else:
                            point_plus = split_route[idx+1]

                        # Deal with any non-continuous sections of an airway
                        if point == "NCS!":
                            file.write(";non continuous section\n")
                        elif point_plus == "NCS!":
                            pass
                        else:
                            line_to_write = f"{point} {point} {point_plus} {point_plus.rstrip()}"
                            if idx + 1 == route_len - 1:
                                file.write(line_to_write)
                            else:
                                file.write(f"{line_to_write}\n")

        route_name = None
        vor_dme = {}
        nav_point = {}
        route_upper = None
        route_lower = None
        last_point = None
        uplo = None
        point = None
        upper_counter = 0
        lower_counter = 0
        point_counter = 0
        for index, row in df_enr_3.iterrows():
            # Only look at rows which have something in the 3rd column
            # This will filter out all the short rows which are of little value
            if pd.notna(row["coordinates_bearing"]):
                if row["route"] == row["name"] and re.match(r"^[A-Z]{1,2}\d{1,3}$", row["name"]):
                    # Check to see if this is a route name
                    logger.debug(f'{row["name"]} (Index: {index})')
                    route_name = row["name"]
                    route_upper = route_name
                    route_lower = route_name
                elif row["route"] == "∆" or (not pd.notna(row["route"]) and row["route"]):
                    # Check to see if this is a significant point
                    coordinates = self.regex.coordinates(row["coordinates_bearing"])
                    if coordinates:
                        coord_group = f"{coordinates[1]} {coordinates[3]}"
                        vordmendb = re.match(
                            r"^([A-Z\s]+)\s\s([VORDMENB]{3}(\/[VORDMENB]{3})?)"
                            r"\s+\(\s+([A-Z]{3})\s+\)$",
                            row["name"]
                            )
                        if vordmendb:
                            # Check to see if this is a VOR/DME/NDB point
                            vor_dme[vordmendb.group(4)] = coord_group
                            point = vordmendb.group(4)
                        else:
                            # If it isn't VOR/DME/NDB then is must be a nav point
                            nav_point[row["name"]] = coord_group
                            point = row['name']

                        if uplo == 0:
                            # If the last route segment was flagged as an upper airway then...
                            if upper_counter == point_counter:
                                route_upper = f"{route_upper} {point}"
                            else:
                                route_upper = f"{route_upper} NCS! {last_point} {point}"
                                upper_counter = point_counter
                            upper_counter += 1
                        elif uplo == 1:
                            # If the last route segment was flagged as an lower airway then...
                            logger.debug(f"Counters: {lower_counter} {point_counter}")
                            if lower_counter == point_counter:
                                route_lower = f"{route_lower} {point}"
                            else:
                                route_lower = f"{route_lower} NCS! {last_point} {point}"
                                lower_counter = point_counter
                            lower_counter += 1
                        elif uplo == 2 or uplo is None:
                            # If the last route segment was flagged as both airway types then...
                            if upper_counter == point_counter:
                                route_upper = f"{route_upper} {point}"
                            else:
                                route_upper = f"{route_upper} NCS! {last_point} {point}"
                                upper_counter = point_counter

                            if lower_counter == point_counter:
                                route_lower = f"{route_lower} {point}"
                            else:
                                route_lower = f"{route_lower} NCS! {last_point} {point}"
                                lower_counter = point_counter
                            upper_counter += 1
                            lower_counter += 1

                        logger.debug(f"{route_name} - {row['name']} - {coord_group}")
                        point_counter += 1
                        last_point = point
                    else:
                        raise ValueError(f"No coordinates match for {row['coordinates_bearing']}")
                elif row["route"] == row["name"] and re.match(r"^\(.*\)$", row["name"]):
                    vert_limits = self.regex.flight_level(row["vertical_limits"])
                    if len(vert_limits) in [1,2]:
                        upper_fl = str(vert_limits[0]).split(" ")[1]
                        if len(vert_limits) == 2:
                            lower_fl = str(vert_limits[1]).split(" ")[1]
                        else:
                            lower_fl = 0
                        if (int(upper_fl) >= self.airway_split and
                            int(lower_fl) >= self.airway_split):
                            # Upper airway only
                            logger.debug("Upper airway only")
                            uplo = 0
                        elif (int(upper_fl) < self.airway_split and
                              int(lower_fl) < self.airway_split):
                            # Lower airway only
                            logger.debug("Lower airway only")
                            uplo = 1
                        else:
                            # Must be both upper and lower
                            logger.debug("Both airways")
                            uplo = 2
                    else:
                        ve_text = f"Can't find upper and lower levels from {row['vertical_limits']}"
                        raise ValueError(ve_text)

        # Write the output to a file
        if len(route_upper) > 1:
            write_to_file(route_upper, True)
        if len(route_lower) > 1:
            write_to_file(route_lower, False)

        return [vor_dme, nav_point]

    def search_enr_4_1(self, df_enr_4:pd.DataFrame, no_build:bool=False) -> list:
        """ENR 4.1 search actions"""

        # Start the iterator
        output = []
        for index, row in df_enr_4.iterrows():
            logger.trace(index)
            name = self.regex.vor_dme_ndb(row["name"])
            rid = re.match(r"^([A-Z]{3})$", row["id"])
            freq = self.regex.frequency(row["frequency"])
            tacan = self.regex.tacan_channel(row["frequency"])
            coords = self.regex.coordinates(row["coordinates"])

            # If there is match for everything on this record
            if name and rid and (freq or tacan) and coords:
                if no_build:
                    coord_out = row["coordinates"]
                else:
                    # Needs to be sent as double coords due to 3rd party limitations
                    coord_xform = self.build.request_output(
                        f'{row["coordinates"]} {row["coordinates"]}')
                    xform_split = coord_xform.split(" ")
                    coord_out = f"{xform_split[0]} {xform_split[1]}"

                if name[2] == "DME":
                    dme = "(DME)"
                else:
                    dme = ""

                if freq and tacan:
                    freq_out = freq[1]
                    # Quick sanity check that the given TACAN ch == the given frequency
                    if freq_out != self.tacan_vor.tacan_to_vor_ils(tacan[1]):
                        raise ValueError(
                            f"The given TACAN channel {tacan[1]} doesn't match"
                            f"the given frequency {freq_out}")
                elif tacan:
                    freq_out = self.tacan_vor.tacan_to_vor_ils(tacan[1])
                elif freq:
                    freq_out = freq[1]

                # Applying formatting to the returned frequency
                freq_format = format(float(freq_out), '.3f')

                # Output format is ID FREQ LAT LON ; Name
                # Ignore any NDB fixes for now
                if name[2] != "NDB":
                    line = f"{rid[1]} {freq_format} {coord_out} ; {name[1].title()} {dme}"
                    output.append(line)
                    logger.debug(line.rstrip())

        return output

    def search_enr_4_4(self, df_enr_4:pd.DataFrame, no_build:bool=False) -> list:
        """ENR 4.4 search actions"""

        # Start the iterator
        output = []
        for index, row in df_enr_4.iterrows():
            logger.trace(index)
            name = re.match(r"^([A-Z]{5})$", row["name"])
            coords = self.regex.coordinates(row["coordinates"])

            # If there is match for everything on this record
            if name and coords:
                if no_build:
                    coord_out = row["coordinates"]
                else:
                    # Needs to be sent as double coords due to 3rd party limitations
                    coord_xform = self.build.request_output(
                        f'{row["coordinates"]} {row["coordinates"]}')
                    xform_split = coord_xform.split(" ")
                    coord_out = f"{xform_split[0]} {xform_split[1]}"

                # Output format is ID FREQ LAT LON ; Name
                line = f"{name[1]} {coord_out}"
                output.append(line)
                logger.debug(line.rstrip())

        return output

    def process_enr_2(self, download_first:bool=True, no_build:bool=False) -> None:
        """Process ENR 2 data"""

        if download_first:
            self.parse_enr_2_1()
            self.parse_enr_2_2()

        def run_process(file_name:str) -> None:
            df_out = pd.read_csv(f"{functions.work_dir}\\DataFrames\\{file_name}.csv")
            self.search_enr_2_x(df_out, file_name, no_build=no_build)

        file_names = ["ENR-2.1_0","ENR-2.1_1","ENR-2.2_0","ENR-2.2_1","ENR-2.2_2"]
        for proc in file_names:
            run_process(proc)

    def process_enr_3(self, download_first:bool=True, no_build:bool=False) -> None:
        """Process ENR 2 data"""

        if download_first:
            self.parse_enr_3_2()
            self.parse_enr_3_3()

        def run_process(file_name:str) -> list:
            df_out = pd.read_csv(f"{functions.work_dir}\\DataFrames\\{file_name}")
            search_results = self.search_enr_3_x(df_out)
            return search_results

        def convert_coords_dump_df(coord_in:dict, name:str) -> str:
            for coord in coord_in.items():
                # The coordinates need passing twice to work with the builder
                # This is a 3rd party api limitation
                xform = self.build.request_output(f"{coord[1]} {coord[1]}")
                split_xform = xform.split(" ")
                # Then we only need to return the first 2/4 results as they're duplicated
                # This is an artifact from the api limitation already mentioned
                coord_in[coord[0]] = f"{split_xform[0]} {split_xform[1]}"
                logger.debug(f"{coord[0]} - {coord[1]} to {split_xform[0]} {split_xform[1]}")
            # Save as a csv df
            df_cc = pd.DataFrame.from_dict(coord_in, orient="index", columns=["lat/lon"])
            df_cc = df_cc.reset_index()
            df_cc.to_csv(f"{functions.work_dir}\\DataFrames\\{name}.csv")

        vor_dme = {}
        nav_aid = {}
        file_names = self.generate_file_names("ENR-3")
        for proc in file_names:
            rpp = run_process(proc)
            vor_dme.update(rpp[0])
            nav_aid.update(rpp[1])

        if no_build:
            logger.warning("The 'no build' option has been set!")
            print(vor_dme)
            print(nav_aid)
        else:
            convert_coords_dump_df(vor_dme, "VOR_DME")
            convert_coords_dump_df(nav_aid, "NAV_AID")

    def process_enr_4(self, download_first:bool=True, no_build:bool=False) -> None:
        """Process ENR 2 data"""

        if download_first:
            self.parse_enr_4_1()
            self.parse_enr_4_4()

        file_names = [
            ("ENR-4.1.csv", "VOR_UK.txt", "1"),
            ("ENR-4.4.csv", "FIXES_UK.txt", "4"),
        ]
        for file_in, file_out, sub_section in file_names:
            df_out = pd.read_csv(f"{functions.work_dir}\\DataFrames\\{file_in}")
            if sub_section == "1":
                output = self.search_enr_4_1(df_out, no_build=no_build)
            elif sub_section == "4":
                output = self.search_enr_4_4(df_out, no_build=no_build)

            with open(f"{functions.work_dir}\\DataFrames\\{file_out}", "w", encoding="utf-8") as file:
                for line in output:
                    file.write(f"{line}\n")
