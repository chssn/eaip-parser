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
from . import functions, lists

# This is needed to supress 'xml as html' warnings with bs4
warnings.filterwarnings("ignore", category=UserWarning)


class ProcessAerodromes:
    """A class to process data scraped from AD 2"""

    def __init__(self) -> None:
        pass

    def run(self) -> None:
        """Run the full process"""

        # Load the list of aerodromes
        df_to_load = os.path.join(functions.work_dir, "DataFrames", "AD-1.3.csv")
        df_ad_1_3 = pd.read_csv(df_to_load)

        data = {}
        data["obstacles"] = pd.DataFrame(columns=lists.column_headers_ad_2_10)
        data["runways"] = pd.DataFrame(columns=lists.column_headers_ad_2_12)
        data["ats"] = pd.DataFrame(columns=lists.column_headers_ad_2_17)
        data["comms"] = pd.DataFrame(columns=lists.column_headers_ad_2_18)
        data["navaids"] = pd.DataFrame(columns=lists.column_headers_ad_2_19)
        file = {}

        # For each aerodrome defined in AD 1.3 do this
        for index, row in df_ad_1_3.iterrows():
            logger.info(f"Processing {row['icao_designator']} ({index})")
            # Find all the tables relating to the specified aerodrome
            data["aero_tables"] = functions.generate_file_names(row["icao_designator"])
            # Iterate over that list of tables
            for table in data["aero_tables"]:
                data["df_path"] = os.path.join(functions.work_dir, "DataFrames", table)
                data["table"] = pd.read_csv(data["df_path"])
                # Search for the table containing AD 2.2
                file["check"] = self.ad_2_2(data["table"])
                if file["check"]:
                    file["basic"] = file["check"]
                # Search for the table containing AD 2.10 and concat to obstacle df
                data["obstacles"] = pd.concat([
                    data["obstacles"],
                    self.ad_2_10(data["table"], row["icao_designator"])
                    ], ignore_index=True)

                # Search for the other tables
                data["search"] = [
                    # AD 2.12
                    ("runways", "Designations RWY Number", lists.column_headers_ad_2_12, [0]),
                    # AD 2.17
                    ("ats", "Designation and lateral limits", lists.column_headers_ad_2_17, [0]),
                    # AD 2.18
                    ("comms", "Service Designation", lists.column_headers_ad_2_18, [0]),
                    # AD 2.19
                    ("navaids", "Type of Aid CAT", lists.column_headers_ad_2_19, [0]),
                ]
                for idt, srch, columns, drop in data["search"]:
                    table_out = self.ad_2_generic(
                        data["table"],
                        row["icao_designator"],
                        srch,
                        columns,
                        drop
                        )
                    data[idt] = pd.concat([data[idt], table_out], ignore_index=True)

        # Do some house cleaning before commiting
        for item, dataframe in data.items():
            if (item not in ["table", "aero_tables", "search"] and
                isinstance(dataframe, pd.DataFrame)):
                del dataframe["id"]
                data["df_path"] = os.path.join(
                    functions.work_dir, "DataFrames", f"AA - {str(item).upper()}.csv"
                    )
                dataframe.to_csv(data["df_path"])

    @staticmethod
    def ad_2_generic(
        table:pd.DataFrame,
        icao:str,
        search:str,
        columns:list,
        drop:list
        ) -> pd.DataFrame:
        """Search for AD 2"""

        if re.search(search, table.to_string()):
            # Set column headers
            table.columns = columns
            # Drop top line
            table = table.drop(drop)
            # Reset the index
            table.reset_index(drop=True, inplace=True)
            # Add the aerodrome icao identifier
            table["aerodrome"] = icao

            return table
        return None

    @staticmethod
    def ad_2_2(table:pd.DataFrame) -> dict:
        """Search for AD 2.2 - AERODROME GEOGRAPHICAL AND ADMINISTRATIVE DATA"""

        if re.search("ARP coordinates and site at AD", table.to_string()):
            data_out = {}
            # Find the first row and print out the coordinates
            if table.iloc[0][2] == "ARP coordinates and site at AD":
                data_out["arp_lat"] = re.search(r"\d{6}[NS]", str(table.iloc[0][3]))[0]
                data_out["arp_lon"] = re.search(r"\d{7}[EW]", str(table.iloc[0][3]))[0]
            # Find the aerodrome elevation
            if table.iloc[2][2] == "Elevation / Reference temperature / Mean Low Temperature":
                data_out["elevation_ft"] = re.match(r"^\d{1,5}(?=\sFT)", str(table.iloc[2][3]))[0]
            # Find the magnetic variation
            if table.iloc[4][2] == "Magnetic Variation / Annual Change":
                data_out["mag_var"] = re.match(r"^\d{1,3}\.\d{1,3}°[EW]", str(table.iloc[4][3]))[0]

            logger.debug(data_out)
            return data_out
        return None

    @staticmethod
    def ad_2_10(table:pd.DataFrame, icao:str) -> pd.DataFrame:
        """Search for AD 2.10 - AERODROME OBSTACLES"""

        if (re.search("In Approach/Take-off areas", table.to_string()) or
            re.search("In circling area and at aerodrome", table.to_string())):
            # Set column headers
            table.columns = lists.column_headers_ad_2_10
            # Drop top two lines
            table = table.drop([0,1])
            # Filter out any intentionally blank lines
            table = table[~table["position"].str.startswith('INTENTIONALLY BLANK')]
            # Reset the index
            table.reset_index(drop=True, inplace=True)
            # Add the aerodrome icao identifier
            table["aerodrome"] = icao

            return table
        return None
