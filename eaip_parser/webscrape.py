"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import re

# Third Party Libraries
import pandas as pd
from loguru import logger

# Local Libraries
from . import airac, builder, functions, lists

# Define a few decorators

def parse_table(section:str) -> None:
    """A decorator to parse the given section"""
    def decorator_func(func):
        def wrapper(self, *args, **kwargs):
            logger.info(f"Parsing {section} data...")
            tables = self.get_table(section)
            if tables:
                dataframe = func(self, tables, *args, **kwargs)
                if isinstance(dataframe, pd.DataFrame):
                    dataframe.to_csv(f"{functions.work_dir}\\DataFrames\\{section}.csv")
                elif isinstance(dataframe, list):
                    for idx, dfl in enumerate(dataframe):
                        dfl.to_csv(f"{functions.work_dir}\\DataFrames\\{section}_{idx}.csv")
                else:
                    raise TypeError("Not entirely sure what was returned there...")
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

        # Validate the entry for date_in
        if date_in != 0:
            if not re.match(r"^20\d{2}\-[0-1]{1}\d{1}\-[0-3]{1}\d{1}$", date_in):
                raise ValueError("Expected date in the format YYYY-MM-DD")
        self.date_in = date_in

    def run(self, download_first:bool=True, no_build:bool=False) -> None:
        """Runs the full webscrape"""

        self.parse_ad_1_3()
        self.process_enr_2(download_first=download_first, no_build=no_build)

    def url_suffix(self, section:str) -> str:
        """Returns a url suffix formatted for the European eAIP standard"""
        return str(f"{self.country}-{section}-{self.language}.html")

    def get_table(self, section:str) -> list:
        """Gets a table from the given url as a list of dataframes"""

        # Combine the airac cycle url with the page being scraped
        address = self.cycle_url + self.url_suffix(section=section)
        logger.debug(address)

        try:
            # Read the full address into a list of dataframes
            tables = pd.read_html(address, flavor="bs4")

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

    def parse_all_tables(self) -> None:
        """Parses a list of tables, saving the output to the DataFrames folder"""

        # Store the current value of self.debug before forcing to True
        debug_flag = self.debug
        self.debug = True

        for section in lists.eaip_sections:
            self.get_table(section)

        # Reset the value of self.debug
        self.debug = debug_flag

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
        column_headers = [
            "data",
            "unit",
            "callsign",
            "frequency",
            "remarks",
        ]
        fir_uir_tma_cta.columns = column_headers
        ctr.columns = column_headers

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
        atz_column_headers = [
            "data",
            "unit",
            "callsign",
            "frequency",
            "remarks",
        ]
        fra_column_headers = [
            "lateral_limits",
            "vertical_limits",
            "remarks"
        ]
        cia_column_headers = [
            "vertical_limits",
            "lateral_limits",
            "remarks"
        ]
        atz.columns = atz_column_headers
        fra.columns = fra_column_headers
        cia.columns = cia_column_headers

        return [atz, fra, cia]

    def search_enr_2_x(self, df_enr_2:pd.DataFrame, file_name:str, no_build:bool=False):
        """Generic ENR 2 search actions"""

        # Start the iterator
        areas = {}
        limits_class = {}
        for index, row in df_enr_2.iterrows():
            if file_name == "ENR-2.2_1":
                # Special case for UK Free Route Airspace
                lat_lim = re.match(
                    r"^([A-Z0-9\s]+)(\s\d{6}(\.\d{2})?[NS]{1}.*)", row["lateral_limits"]
                    )
                logger.debug(str(lat_lim[2]).lstrip())
                areas[lat_lim[1]] = str(lat_lim[2]).lstrip()

                ver_lim = re.findall(r"(FL\s\d{1,3})", row["vertical_limits"])
                limit_text = (f"UK Free Route Airspace from {ver_lim[0]} to {ver_lim[1]}")
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
                    frequency = re.match(r"(\d{3}\.\d{3})", str(row["frequency"]))
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
                # Pass text to the builder
                self.build.text_input(loc)
                # Request data
                if no_build:
                    sct_data = f"The 'no build' option has been selected...\n{loc}"
                else:
                    sct_data = self.build.request_output()

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

    def process_enr_2(self, download_first:bool=True, no_build:bool=False) -> None:
        """Process ENR 2 data"""

        if download_first:
            self.parse_enr_2_1()
            self.parse_enr_2_2()

        def run_process(file_name:str) -> None:
            df_out = pd.read_csv(f"{functions.work_dir}\\DataFrames\\{file_name}.csv")
            self.search_enr_2_x(df_out, file_name, no_build=no_build)

        file_names = ["ENR-2.1_0","ENR-2.1_1", "ENR-2.2_0", "ENR-2.2_1", "ENR-2.2_2"]
        for proc in file_names:
            run_process(proc)
