"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import os
import re
import shutil
import urllib.error
import warnings

# Third Party Libraries
import pandas as pd
from loguru import logger

# Local Libraries
from . import airac, builder, functions, lists, process

# This is needed to supress 'xml as html' warnings with bs4
warnings.filterwarnings("ignore", category=UserWarning)

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
                    df_path = os.path.join(functions.work_dir, "DataFrames", f"{section}.csv")
                    dataframe.to_csv(df_path)
                elif isinstance(dataframe, list):
                    # If a list of dataframes are passed
                    for idx, dfl in enumerate(dataframe):
                        dfl_path = os.path.join(
                            functions.work_dir,
                            "DataFrames",
                            f"{section}_{idx}.csv"
                            )
                        dfl.to_csv(dfl_path)
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
            ) -> None:
        airac_cycle = airac.Airac()
        self.cycle_url = airac_cycle.url(next_cycle=next_cycle, date_in=date_in)

        # Validate the entry for country_code
        if re.match(r"^[A-Z]{2}$", country_code.upper()):
            self.country = country_code.upper()
            self.language = lists.country_codes[self.country]
        else:
            raise ValueError("Expected a two character country code such as 'EG'")

        # Set the date
        self.date_in = date_in
        # Setup the processors
        self.proc = ProcessData()
        self.proc_a = process.ProcessAerodromes()

    def run(self, download_first:bool=True, no_build:bool=False, clean_start:bool=True) -> None:
        """Runs the full webscrape"""

        if clean_start:
            self.clean_start()
        if download_first:
            self.parse_ad_2()
            self.parse_enr_2_1()
            self.parse_enr_2_2()
            self.parse_enr_3_2()
            self.parse_enr_3_3()
            self.parse_enr_4_1()
            self.parse_enr_4_4()
            self.parse_enr_5_1()
            self.parse_enr_5_2()
            self.parse_enr_5_3()
        self.proc.process_enr_2(no_build=no_build)
        self.proc.process_enr_3(no_build=no_build)
        self.proc.process_enr_4(no_build=no_build)
        self.proc.process_enr_5(no_build=no_build)
        self.proc_a.run()

    @staticmethod
    def clean_start():
        """Delete all temporary files"""

        # Check to see if temp directory already exists
        temp_dir = os.path.join(functions.work_dir, "DataFrames")
        if os.path.exists(temp_dir):
            # Delete the temp directory
            shutil.rmtree(temp_dir)
            logger.info(f"Deleted temporary directory - {temp_dir}")
        # Create the temp directory
        os.makedirs(temp_dir)

    def url_suffix(self, section:str) -> str:
        """Returns a url suffix formatted for the European eAIP standard"""
        if (re.match(r"^(AD|ENR|GEN)\-[0-6]{1}\.\d{1,2}$", section) or
            re.match(r"^AD\-[23]{1}\.[A-Z]{4}$", section)):
            return str(f"{self.country}-{section}-{self.language}.html")
        raise ValueError(f"{section} is in an unexpected format!")

    def get_table(self, section:str, match:str=".+") -> list:
        """Gets a table from the given url as a list of dataframes"""

        # Combine the airac cycle url with the page being scraped
        address = self.cycle_url + self.url_suffix(section=section)
        logger.debug(address)

        try:
            # Read the full address into a list of dataframes
            tables = pd.read_html(address, flavor="bs4", match=match)

            # If there is a least one table
            if len(tables) > 0:
                return tables
            raise functions.NoUrlDataFoundError(address)
        except ValueError as error:
            logger.warning(f"{error} for {address}")
        except urllib.error.HTTPError as error:
            logger.warning(f"{error} for {address}")
        return None

    @parse_table("AD-1.3")
    def parse_ad_1_3(self, tables:list=None) -> pd.DataFrame:
        """Process data from AD 1.3 - INDEX TO AERODROMES AND HELIPORTS"""

        logger.debug(f"{self.date_in} - AD1.3")
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

        logger.debug(f"{self.date_in} - ENR2.1")
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

        logger.debug(f"{self.date_in} - ENR2.2")
        # The data object table[0] is for ATZ
        atz = tables[0]
        # The data object table[27] is for FRA
        fra = tables[26]
        # The data object table[28] is for Channel Islands Airspace
        cia = tables[27]

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

        logger.debug(f"{self.date_in} - ENR3.2")
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

        logger.debug(f"{self.date_in} - ENR3.3")
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

        logger.debug(f"{self.date_in} - ENR4.1")
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

        logger.debug(f"{self.date_in} - ENR4.4")
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

    @parse_table("ENR-5.1")
    def parse_enr_5_1(self, tables:list=None) -> pd.DataFrame:
        """Pull data from ENR 5.1 - PROHIBITED, RESTRICTED AND DANGER AREAS"""

        logger.debug(f"{self.date_in} - ENR5.1")
        # The data object is table[0]
        nwt = tables[0]

        # Modify header row
        nwt.columns = lists.column_headers_nav_warn

        # Name the columns to keep
        nwt = nwt[["area"]]

        return nwt

    @parse_table("ENR-5.2")
    def parse_enr_5_2(self, tables:list=None) -> pd.DataFrame:
        """Pull data from ENR 5.1 - PROHIBITED, RESTRICTED AND DANGER AREAS"""

        logger.debug(f"{self.date_in} - ENR5.2")
        # The data object is table[0]
        nwt = tables[0]

        # Modify header row
        nwt.columns = lists.column_headers_nav_warn

        # Name the columns to keep
        nwt = nwt[["area"]]

        return nwt

    @parse_table("ENR-5.3")
    def parse_enr_5_3(self, tables:list=None) -> pd.DataFrame:
        """Pull data from ENR 5.1 - PROHIBITED, RESTRICTED AND DANGER AREAS"""

        logger.debug(f"{self.date_in} - ENR5.3")
        # The data object is table[1] - table[0] relates exclusively to small arms ranges with an
        # upper limit of 500ft
        nwt = tables[1]

        # Modify header row
        nwt.columns = [
            "area",
            "vert_limits",
            "advisory",
            "authority",
            "remarks",
        ]

        # Name the columns to keep
        nwt = nwt[["area"]]

        return nwt

    def parse_ad_2(self) -> None:
        """Pull data from AD 2 - AERODROMES"""

        # Get a list of aerodromes which exist in the AIP
        self.parse_ad_1_3()
        # Load the list of aerodromes
        df_to_load = os.path.join(functions.work_dir, "DataFrames", "AD-1.3.csv")
        df_ad_1_3 = pd.read_csv(df_to_load)

        for index, row in df_ad_1_3.iterrows():
            logger.trace(index)
            logger.info(f"Parsing AD-2.{row['icao_designator']} ({row['location']})")
            df_list = self.get_table(f"AD-2.{row['icao_designator']}")

            if df_list is not None:
                for idx, dfl in enumerate(df_list):
                    dfl_path = os.path.join(
                        functions.work_dir,
                        "DataFrames",
                        f"{row['icao_designator']}_{idx}.csv"
                        )
                    dfl.to_csv(dfl_path)


class ProcessData:
    """Process the scraped data"""

    def __init__(self) -> None:
        # Setup the builder
        self.build = builder.KiloJuliett()
        # Use default settings
        self.build.settings()
        # Define at which FL an airway should be marked as 'upper'
        self.airway_split = 245

    def search_enr_2_x(self, df_enr_2:pd.DataFrame, file_name:str, no_build:bool=False):
        """Generic ENR 2 search actions"""

        # Start the iterator
        areas = {}
        limits_class = {}
        for index, row in df_enr_2.iterrows():
            if file_name == "ENR-2.2_1":
                # Special case for UK Free Route Airspace
                lat_lim = lists.Regex.lateral_limits(row["lateral_limits"])
                v_lim = lists.Regex.flight_level(row["vertical_limits"])

                areas[lat_lim[1]] = str(lat_lim[2]).lstrip()
                limits_class[lat_lim[1]] = f"UK Free Route Airspace from {v_lim[0]} to {v_lim[1]}"

                logger.debug(areas[lat_lim[1]])
                logger.debug(limits_class[lat_lim[1]])
            elif file_name == "ENR-2.2_2":
                # Special case for Channel Islands Airspace
                if re.search(r"\d{6}(\.\d{2})?[NS]{1}", row["lateral_limits"]):
                    title = f"CHANNEL ISLANDS {index}"
                    areas[title] = row["lateral_limits"]
                    limits_class[title] = row["vertical_limits"]

                    logger.debug(row["vertical_limits"])
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
                        areas[title[1]] = coords[1]
                        logger.debug(areas[title[1]])

                    # Find the lateral limits
                    limits = re.search(
                        r"(?:\s+\bUpper\slimit\:\s\b)(\S+(\s\bFT\b\s\b(ALT|AGL)\b)?)"
                        r"(?:\s+\bLower\slimit\:\s\b)(\S+(\s\bFT\b\s\b(ALT|AGL)\b)?)"
                        r"(?:\s+\bClass\b\:\s)([A-G]{1})", str(row["data"])
                    )
                    # Cleanup the callsign
                    callsign = re.match(r"^([A-Z\s]+)(?:\s+[A-Z]{1}[a-z]+)", str(row['callsign']))
                    # Cleanup the frequency
                    frequency = lists.Regex.frequency(row["frequency"])

                    if limits and coords and callsign and frequency:
                        limits_class[title[1]] = (f"Class {limits[7]} airspace from {limits[4]} "
                                                  f"to {limits[1]} - {row['unit']} "
                                                  f"({callsign[1].rstrip()}), {frequency[1]}MHz")
                        logger.debug(limits_class[title[1]])

        # Write the scraped data to file
        self.write_enr_2(areas, file_name, no_build, limits_class)

    def search_enr_3_x(self, df_enr_3:pd.DataFrame) -> list:
        """Generic ENR 3 search actions"""

        route_name = None
        vor_dme = {}
        nav_point = {}
        scraped_data = {}
        scraped_data["u_count"] = 0
        scraped_data["l_count"] = 0
        scraped_data["p_count"] = 0
        scraped_data["last_point"] = None
        scraped_data["uplo"] = None
        scraped_data["point"] = None
        for index, row in df_enr_3.iterrows():
            # Only look at rows which have something in the 3rd column
            # This will filter out all the short rows which are of little value
            if pd.notna(row["coordinates_bearing"]):
                if row["route"] == row["name"] and re.match(r"^[A-Z]{1,2}\d{1,3}$", row["name"]):
                    # Check to see if this is a route name
                    route_name = row["name"]
                    scraped_data["upper"] = route_name
                    scraped_data["lower"] = route_name

                    logger.debug(f'{row["name"]} (Index: {index})')
                elif row["route"] == "∆" or (not pd.notna(row["route"]) and row["route"]):
                    # Check for route data
                    rtn = self.route_check_enr_3(row, scraped_data, vor_dme, nav_point)
                    scraped_data.update(rtn["scraped"])
                    vor_dme.update(rtn["vordme"])
                    nav_point.update(rtn["nav"])

                    logger.debug(f"{route_name} - {row['name']} - {scraped_data['coord_grp']}")
                    scraped_data["p_count"] += 1
                    scraped_data["last_point"] = scraped_data["point"]
                elif row["route"] == row["name"] and re.match(r"^\(.*\)$", row["name"]):
                    # Check vertical limts
                    scraped_data.update(self.vertical_limits_enr_3(scraped_data, row))
            elif re.match(r"^\(RNAV\)", row["route"]):
                if scraped_data["uplo"] == 0:
                    scraped_data["upper"] = f"{scraped_data['upper']} NCS!"
                elif scraped_data["uplo"] == 1:
                    scraped_data["lower"] = f"{scraped_data['lower']} NCS!"
                elif scraped_data["uplo"] == 2:
                    scraped_data["upper"] = f"{scraped_data['upper']} NCS!"
                    scraped_data["lower"] = f"{scraped_data['lower']} NCS!"
        # Write the output to a file
        if len(scraped_data["upper"]) > 1:
            self.write_enr_3(scraped_data["upper"], True)
        if len(scraped_data["lower"]) > 1:
            self.write_enr_3(scraped_data["lower"], False)

        return [vor_dme, nav_point]

    def search_enr_4_1(self, df_enr_4:pd.DataFrame, no_build:bool=False) -> list:
        """ENR 4.1 search actions"""

        # Start the iterator
        tacan_vor = functions.TacanVor()
        output = []
        scraped_data = {}
        for index, row in df_enr_4.iterrows():
            logger.trace(index)
            scraped_data["name"] = lists.Regex.vor_dme_ndb(row["name"])
            scraped_data["rid"] = re.match(r"^([A-Z]{3})$", row["id"])
            scraped_data["freq"] = lists.Regex.frequency(row["frequency"])
            scraped_data["tacan"] = lists.Regex.tacan_channel(row["frequency"])
            scraped_data["coords"] = lists.Regex.coordinates(row["coordinates"])

            # If there is match for everything on this record
            if (scraped_data["name"] and
                scraped_data["rid"] and
                (scraped_data["freq"] or scraped_data["tacan"])
                and scraped_data["coords"]):
                if no_build:
                    coord_out = row["coordinates"]
                else:
                    # Needs to be sent as double coords due to 3rd party limitations
                    coord_xform = self.build.request_output(
                        f'{row["coordinates"]} {row["coordinates"]}')
                    xform_split = coord_xform.split(" ")
                    coord_out = f"{xform_split[0]} {xform_split[1]}"

                if scraped_data["name"][2] == "DME":
                    dme = "(DME)"
                else:
                    dme = ""

                if scraped_data["freq"] and scraped_data["tacan"]:
                    freq_out = scraped_data["freq"][1]
                    # Quick sanity check that the given TACAN ch == the given frequency
                    if freq_out != tacan_vor.tacan_to_vor_ils(scraped_data["tacan"][1]):
                        raise ValueError(
                            f"The given TACAN channel {scraped_data['tacan'][1]} doesn't match"
                            f"the given frequency {freq_out}")
                elif scraped_data["tacan"]:
                    freq_out = tacan_vor.tacan_to_vor_ils(scraped_data["tacan"][1])
                elif scraped_data["freq"]:
                    freq_out = scraped_data["freq"][1]

                # Applying formatting to the returned frequency
                freq_format = format(float(freq_out), '.3f')

                # Output format is ID FREQ LAT LON ; Name
                # Ignore any NDB fixes for now
                if scraped_data["name"][2] != "NDB":
                    line = (f"{scraped_data['rid'][1]} {freq_format} {coord_out} ; "
                            f"{str(scraped_data['name'][1]).title()} {dme}")
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
            coords = lists.Regex.coordinates(row["coordinates"])

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

    def search_enr_5_x(self, df_enr_5:pd.DataFrame, file_name:str, no_build:bool=False) -> list:
        """ENR 5.1 search actions"""

        # Start the iterator
        data_store = {}
        data_store["file_name"] = file_name
        data_store["no_build"] = no_build
        for index, row in df_enr_5.iterrows():
            logger.trace(index)
            # Search for relevant data
            if file_name == "ENR-5.1":
                data_store["data"] = re.match(
                    r"(EG\s[DPR]{1}\d{1,4}([A-Z]{1})?)(.*)(?<=\s\s)"
                    r"((\d{6}[NS]{1}\s\d{7}[EW]{1}.*)|(\bA\scircle\b.*))", row["area"])
                if data_store["data"]:
                    data_store["eid"] = data_store["data"][1]
                    data_store["name"] = str(data_store["eid"][3]).strip()
                    data_store["coords"] = data_store["data"][4]
            elif file_name == "ENR-5.2":
                data_store["data"] = re.match(
                    r"(.*)(?<=\s\s)((\d{6}[NS]{1}\s\d{7}[EW]{1}.*)|(\bA\scircle\b.*))", row["area"])
                if data_store["data"]:
                    data_store["eid"] = f"META {str(index).zfill(3)}"
                    data_store["name"] = str(data_store["data"][1]).strip()
                    data_store["coords"] = data_store["data"][2]
            elif file_name == "ENR-5.3":
                data_store["data"] = re.match(
                    r"(.*)(?<=\s\s)((\d{6}[NS]{1}\s\d{7}[EW]{1}.*)|(\bA\scircle\b.*))", row["area"])
                if data_store["data"]:
                    data_store["eid"] = f"OADN {str(index).zfill(3)}"
                    data_store["name"] = str(data_store["data"][1]).strip()
                    data_store["coords"] = data_store["data"][2]

                    # If a single coordinate is returned, the row can be filtered out as it is of
                    # no use in the context of an sct file.
                    if lists.Regex.coordinates(data_store["coords"]):
                        continue
                    # If a radius less than or equal to 1NM is returned then this can also be
                    # filtered for the same reason.
                    radius_check = re.match(
                        r"(\d{1,2}(\.\d{1,3})?)(?=\sNM\sradius)", data_store["coords"])
                    if radius_check:
                        if float(radius_check[1]) <= 1:
                            continue
            self.write_enr_5(data_store)

    def process_enr_2(self, no_build:bool=False) -> None:
        """Process ENR 2 data"""

        logger.info("Processing ENR 2 data...")

        def run_process(file_name:str) -> None:
            df_out_path = os.path.join(functions.work_dir, "DataFrames", f"{file_name}.csv")
            df_out = pd.read_csv(df_out_path)
            self.search_enr_2_x(df_out, file_name, no_build=no_build)

        file_names = ["ENR-2.1_0","ENR-2.1_1","ENR-2.2_0","ENR-2.2_1","ENR-2.2_2"]
        for proc in file_names:
            run_process(proc)

    def process_enr_3(self, no_build:bool=False) -> None:
        """Process ENR 3 data"""

        logger.info("Processing ENR 3 data...")

        def run_process(file_name:str) -> list:
            df_out_path = os.path.join(functions.work_dir, "DataFrames", f"{file_name}")
            df_out = pd.read_csv(df_out_path)
            search_results = self.search_enr_3_x(df_out)
            return search_results

        def convert_coords_dump_df(coord_in:dict, name:str) -> None:
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
            df_out_path = os.path.join(functions.work_dir, "DataFrames", f"{name}.csv")
            df_cc.to_csv(df_out_path)

        vor_dme = {}
        nav_aid = {}
        file_names = functions.generate_file_names("ENR-3")
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

    def process_enr_4(self, no_build:bool=False) -> None:
        """Process ENR 4 data"""

        logger.info("Processing ENR 4 data...")

        file_names = [
            ("ENR-4.1.csv", "VOR_UK.txt", "1"),
            ("ENR-4.4.csv", "FIXES_UK.txt", "4"),
        ]
        for file_in, file_out, sub_section in file_names:
            df_out_path = os.path.join(functions.work_dir, "DataFrames", f"{file_in}")
            df_out = pd.read_csv(df_out_path)
            if sub_section == "1":
                output = self.search_enr_4_1(df_out, no_build=no_build)
            elif sub_section == "4":
                output = self.search_enr_4_4(df_out, no_build=no_build)

            file_path = os.path.join(functions.work_dir, "DataFrames", file_out)
            logger.debug(file_path)
            with open(file_path, "w", encoding="utf-8") as file:
                for line in output:
                    file.write(f"{str(line).rstrip()}\n")

    def process_enr_5(self, no_build:bool=False) -> None:
        """Process ENR 5 data"""

        logger.info("Processing ENR 5 data...")

        def run_process(file_name:str) -> None:
            df_out_path = os.path.join(functions.work_dir, "DataFrames", f"{file_name}.csv")
            df_out = pd.read_csv(df_out_path)
            self.search_enr_5_x(df_out, file_name, no_build=no_build)

        file_names = ["ENR-5.1", "ENR-5.2", "ENR-5.3"]
        for proc in file_names:
            run_process(proc)

    def write_enr_2(self, areas:dict, file_name:str, no_build:bool, limits_class:dict) -> None:
        """Write ENR 2 files"""

        output = ""
        last_title = None
        file_path = os.path.join(functions.work_dir, "DataFrames", f"{file_name}_AIRSPACE.sct")
        with open(file_path, "w", encoding="utf-8") as file:
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

    @staticmethod
    def write_enr_3(route:str, is_upper:bool) -> None:
        """Write ENR 3 files"""

        split_route = route.split(" ")
        route_len = len(split_route)
        logger.debug(f"{is_upper} {split_route}")
        start = 1
        if len(split_route) > 2 and split_route[2] == "NCS!":
            start = 3

        uorl = "LOWER"
        if is_upper:
            uorl = "UPPER"

        file_path = os.path.join(
            functions.work_dir,
            "DataFrames",
            f"ENR-3.2-{uorl}-{split_route[0]}.txt"
            )
        with open(file_path, "w", encoding="utf-8") as file:
            for idx in range(start, route_len-1, 1):
                if (idx + 1) < route_len:
                    # If the point is only 3 characters, it needs padding with 2 extra spaces
                    point = split_route[idx]
                    if len(split_route[idx]) == 3:
                        point = f"{split_route[idx]}  "

                    point_plus = split_route[idx+1]
                    if len(split_route[idx+1]) == 3:
                        point_plus = f"{split_route[idx+1]}  "

                    # Deal with any non-continuous sections of an airway
                    if point == "NCS!":
                        file.write(";non continuous section\n")
                    elif point_plus == "NCS!" or point is None:
                        pass
                    else:
                        line_to_write = f"{point} {point} {point_plus} {point_plus.rstrip()}"
                        if idx + 1 == route_len - 1:
                            file.write(line_to_write)
                        else:
                            file.write(f"{line_to_write}\n")

    def write_enr_5(self, data_store:dict):
        """Write ENR 5 files"""

        if data_store["data"]:
            file_path = os.path.join(
                functions.work_dir,
                "DataFrames",
                f"{data_store['file_name']}-{data_store['eid']}.txt"
                )
            with open(file_path, "w", encoding="utf-8") as file:
                # Request data
                if data_store["no_build"]:
                    sct_data = ("The 'no build' option has been selected...\n"
                                f"{data_store['coords']}")
                else:
                    sct_data = self.build.request_output(data_store["coords"])

                id_split = str(data_store["eid"]).split(" ", maxsplit=2)
                # Add comments into the sct output
                output = f";{id_split[0]}{id_split[1]} - {data_store['name']}"
                file.write(output)
                # Add the returned coords
                coords_split = sct_data.split("\n")
                for crd in coords_split:
                    output = f"\n{id_split[0]}{id_split[1]}\t{crd}"
                    file.write(output)

    def route_check_enr_3(self, row:dict, scraped_data:dict, vor_dme:dict, nav_point:dict) -> dict:
        """Check to see if this is a significant point"""
        scraped_data["coords"] = lists.Regex.coordinates(row["coordinates_bearing"])
        if scraped_data["coords"]:
            scraped_data["coord_grp"] = (f"{scraped_data['coords'][1]} "
                                            f"{scraped_data['coords'][3]}")
        else:
            raise ValueError(f"No coordinates match for {row['coordinates_bearing']}")

        scraped_data["vordmendb"] = re.match(
            r"^([A-Z\s]+)\s\s([VORDMENB]{3}(\/[VORDMENB]{3})?)"
            r"\s+\(\s+([A-Z]{3})\s+\)$",
            row["name"]
            )
        if scraped_data["vordmendb"]:
            # Check to see if this is a VOR/DME/NDB point
            vor_dme[scraped_data["vordmendb"][4]] = scraped_data["coord_grp"]
            scraped_data["point"] = scraped_data["vordmendb"][4]
        else:
            # If it isn't VOR/DME/NDB then is must be a nav point
            nav_point[row["name"]] = scraped_data["coord_grp"]
            scraped_data["point"] = row['name']

        if scraped_data["uplo"] == 0:
            prefix = "u"
            key = "upper"
        elif scraped_data["uplo"] == 1:
            prefix = "l"
            key = "lower"
        else:
            prefix = "x"

        if prefix == "x":
            # If the last route segment was flagged as both airway types then...
            scraped_data.update(self.route_upper_lower("u", "upper", scraped_data))
            scraped_data.update(self.route_upper_lower("l", "lower", scraped_data))
        else:
            scraped_data.update(self.route_upper_lower(prefix, key, scraped_data))

        dict_out = {}
        dict_out["scraped"] = scraped_data
        dict_out["vordme"] = vor_dme
        dict_out["nav"] = nav_point

        return dict_out

    def vertical_limits_enr_3(self, scraped_data:dict, row:dict) -> dict:
        """Check vertical limits"""

        vert_limits = lists.Regex.flight_level(row["vertical_limits"])
        if len(vert_limits) in [1,2]:
            upper_fl = str(vert_limits[0]).split(" ")[1]
            if len(vert_limits) == 2:
                lower_fl = str(vert_limits[1]).split(" ")[1]
            else:
                lower_fl = 0
            if (int(upper_fl) > self.airway_split and
                int(lower_fl) >= self.airway_split):
                # Upper airway only
                logger.debug(f"Upper airway only {upper_fl} > {self.airway_split}")
                logger.debug(f"Upper airway only {lower_fl} >= {self.airway_split}")
                scraped_data["uplo"] = 0
            elif (int(upper_fl) <= self.airway_split and
                    int(lower_fl) < self.airway_split):
                # Lower airway only
                logger.debug(f"Lower airway only {upper_fl} <= {self.airway_split}")
                logger.debug(f"Lower airway only {lower_fl} <= {self.airway_split}")
                scraped_data["uplo"] = 1
            else:
                # Must be both upper and lower
                logger.debug(f"Both airways {upper_fl} and {lower_fl}")
                scraped_data["uplo"] = 2
            return scraped_data
        ve_text = f"Can't find upper and lower levels from {row['vertical_limits']}"
        raise ValueError(ve_text)

    @staticmethod
    def route_upper_lower(prefix:str, key:str, scraped_data:str) -> dict:
        """Identify upper and lower routes"""

        if scraped_data[prefix+"_count"] == scraped_data["p_count"]:
            scraped_data[key] = f"{scraped_data[key]} {scraped_data['point']}"
        else:
            scraped_data[key] = (f"{scraped_data[key]} NCS! {scraped_data['last_point']} "
                                    f"{scraped_data['point']}")
            scraped_data[prefix+"_count"] = scraped_data["p_count"]

        scraped_data[prefix+"_count"] += 1

        return scraped_data
