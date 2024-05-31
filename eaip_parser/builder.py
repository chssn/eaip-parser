"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.9

# Standard Libraries
import json
import os
import re
import shutil
import time
from dataclasses import dataclass

# Third Party Libraries
import requests # type: ignore
from loguru import logger
import pandas as pd # type: ignore

# Local Libraries
from eaip_parser import functions, lists, process


@dataclass
class BuildSettings:
    """Build settings"""
    elnp:bool=True
    wpt:bool=True
    dupe:bool=True
    xchglatlon:bool=False
    title:bool=False
    output_format:str="sct"


@dataclass
class ArcSettings:
    """Arc Settings"""
    arctype:int=0
    arcres:int=9
    polynl:int=1

class KiloJuliett:
    """A class to build using https://kilojuliett.ch/webtools/geo/coordinatesconverter"""

    def __init__(self, base_url:str="https://kilojuliett.ch/webtools/geo/json") -> None:
        self.request_settings: dict = {}
        self.base_url = base_url
        self.rate_limit = 0

    def settings(
            self,
            build_settings: BuildSettings = BuildSettings(),
            arc_settings: ArcSettings = ArcSettings()
            ) -> None:
        """Sets the settings"""

        # Dictionary to map BuildSettings attributes to corresponding request settings
        build_settings_mapping = {
            "elnp": "elnp",
            "wpt": "wpt",
            "dupe": "dupe",
            "xchglatlon": "xchglatlon",
            "title": "title",
        }

        # Update request_settings based on BuildSettings attributes
        for attr, setting_name in build_settings_mapping.items():
            if getattr(build_settings, attr):
                set_to = "on"
                if setting_name == "title":
                    set_to = r"%3B"
                self.request_settings[setting_name] = set_to

        # Dictionary to map ArcSettings attributes to corresponding request settings
        arc_settings_mapping = {
            "arctype": "arctype",
            "arcres": "arcres",
            "polynl": "polynl",
        }

        # Update request_settings based on ArcSettings attributes
        for attr, setting_name in arc_settings_mapping.items():
            value = getattr(arc_settings, attr)
            if attr == "arctype" and value not in [0, 1]:
                raise ValueError("Arc type can only be 0 (Orthodromic) or 1 (Loxodromic)")
            if attr == "arcres" and not 0 <= value <= 180:
                raise ValueError("Arc resolution must be a value in degrees >= 0 and <= 180")
            if attr == "polynl" and not 0 < value < 10:
                raise ValueError("Number of new lines between polygons must be > 0 and < 10")
            self.request_settings[setting_name] = value

        # Set output format
        formats = [
            "xls",
            "ese",
            "sct",
            "dez",
            "vrc",
            "ts-line",
            "qtsp",
            "vsys-dd",
        ]
        if build_settings.output_format in formats:
            self.request_settings["format"] = build_settings.output_format
        else:
            raise ValueError(f"Format type must be one of {formats}")

        logger.debug(self.request_settings)

    @staticmethod
    def data_input_validator(data:str) -> str:
        """Validates inputed data"""

        regex_list = [
            r"^[NS]{1}\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?(\:|\s)"
            r"[EW]{1}\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?",
            r"^\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?[NS]{1}(\:|\s)"
            r"\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?[EW]{1}",
            r"^[NS]{1}\d{1,2}°\d{2}\.\d{2}'\s[EW]{1}\d{1,3}°\d{2}\.\d{2}'",
            r"^\d{1,2}°\d{2}\.\d{2}'[NS]{1}\s\d{1,3}°\d{2}\.\d{2}'[EW]{1}",
            r"^\d{6}[NS]{1}\s\d{7}[EW]{1}",
            r"^[NS]{1}\d{6}\s[EW]{1}\d{6,7}",
            r"^\d{4}[NS]{1}\d{5}[EW]{1}",
            r"^\d{2}[NS]{1}\d{3}[EW]{1}",
            r"^\d{2}°\d{2}'\d{2}\"[NS]{1}\s\,\s\d{3}°\d{2}'\d{2}\"[EW]{1}",
            r"^[NS]{1}\d{2}°\d{2}'\d{2}\"\s\,\s[EW]{1}\d{1,3}°\d{2}'\d{2}\"",
            r"^\-?\d{2}\.\d{5}\,\s\-?\d{2}\.\d{6}",
            r"^[NS]{1}\d{1}\.\d{3}\,\s[EW]{1}\d{1}\.\d{3}"
        ]

        for pattern in regex_list:
            if re.match(pattern, data):
                return data
        raise ValueError(f"The entry {data} isn't valid")

    @staticmethod
    def check_in_uk(coords:str) -> bool:
        """Checks if the returned values are within the bounds of the United Kingdom"""

        lat = re.findall(r"(?:^|\s)([NS])(\d{3})", coords)
        lon = re.findall(r"(?:^|\s)([EW])(\d{3})", coords)
        if len(lat) > 0 and len(lon) > 0:
            for item in lat:
                if item[0] == "S":
                    logger.error(f"{item} not within UK bounds! {coords}")
                    return False
                if int(item[1]) < 46 or int(item[1]) > 62:
                    logger.error(f"{item} not within UK bounds! {coords}")
                    return False
            for item in lon:
                if item[0] == "W" and int(item[1]) > 11:
                    logger.error(f"{item} not within UK bounds! {coords}")
                    return False
                if item[0] == "E" and int(item[1]) > 2:
                    logger.error(f"{item} not within UK bounds! {coords}")
                    return False

            return True
        raise ValueError(f"No results found in the given string: {coords}")

    def request_output(self, data_in:str) -> str:
        """
        Requests the transformed input data from
        https://kilojuliett.ch/webtools/geo/coordinatesconverter
        """

        self.request_settings["input"] = data_in
        logger.trace(data_in)

        headers = {
            "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "Accept": "application/json,text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Ch-Ua-Mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
            "Sec-Ch-Ua-Platform": "\"\"",
            "Origin": "https://kilojuliett.ch",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://kilojuliett.ch/webtools/geo/coordinatesconverter",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
            }

        # Apply a rate limiter
        if self.rate_limit > 1000:
            logger.info(f"Rate limit hit for {self.base_url} - Pausing for 10 seconds...")
            self.rate_limit = 0
            time.sleep(10)
            logger.info("Continuing...")

        attempt = 0
        while attempt < 5:
            response = requests.post(
                self.base_url,
                headers=headers,
                data=self.request_settings,
                timeout=30
                )

            # If any response other than 200, pause and try again
            if response.status_code != 200:
                attempt += 1
                logger.warning(f"Unable to connect to {self.base_url} - Attempt {attempt}")
                time.sleep(5)
                continue
            self.rate_limit += 1
            json_load = json.loads(response.text)
            if self.check_in_uk(json_load["txt"]):
                return json_load["txt"]
            else:
                return "NUK"
        raise requests.exceptions.HTTPError(f"Error loading {self.base_url}")


class BuildAirports:
    """Build the 'Airports' Folder"""

    def __init__(self, no_build:bool=False) -> None:
        # Load the list of aerodromes
        self.df_ad_1_3 = self.load_df("AD-1.3.csv")
        # Init some vars
        self.airport_dir = ""
        self.build = KiloJuliett()
        self.build.settings()
        self.coord = ""
        self.icao = ""
        self.icao_title = ""
        self.no_build = no_build

    def run(self) -> None:
        """Run the full process"""

        # For each aerodrome defined in AD 1.3 do this
        for index, row in self.df_ad_1_3.iterrows():
            self.coord = ""
            self.icao = row['icao_designator']
            self.icao_title = str(row["location"]).title()
            logger.info(f"Building files for {self.icao} ({index})")
            # Create the directory to store output
            self.airport_dir = self.create_dirs(self.icao)
            self.txt_airspace()
            self.text_basic()
            self.text_positions()
            self.text_runway()

    @staticmethod
    def create_dirs(dir_name:str) -> str:
        """Create the required dirs"""

        # Check to see if directory already exists
        output_dir = os.path.join(functions.work_dir, "DataFrames", "Output", "Airports", dir_name)
        if os.path.exists(output_dir):
            # Delete the temp directory
            shutil.rmtree(output_dir)
            logger.info(f"Deleted old output directory - {output_dir}")
        # Create the temp directory
        os.makedirs(output_dir)

        return output_dir

    @staticmethod
    def runway_flip_flop(runway:str) -> str:
        """Returns something representing the opposing runway"""

        # Search the given string - not sure what the X suffix denotes but G seems to be grass
        rwy = re.match(r"^(\d{1,2})([LRCXG]{1})?$", str(runway).upper())
        if runway is not None and rwy:
            # Flip the number using modulo 36 as we're dealing in 2 digit numbers
            if int(rwy[1]) >= 0 and int(rwy[1]) <= 36:
                rwy_opp = str((int(rwy[1]) + 18) % 36)
                # Get the alternate letter if any
                if len(rwy.groups()) + 1 == 3:
                    if rwy[2] == "L":
                        return f"{rwy_opp.zfill(2)}R"
                    if rwy[2] == "R":
                        return f"{rwy_opp.zfill(2)}L"
                    if rwy[2] == "C":
                        return f"{rwy_opp.zfill(2)}C"
                    if rwy[2] == "X":
                        return f"{rwy_opp.zfill(2)}X"
                    if rwy[2] == "G":
                        return f"{rwy_opp.zfill(2)}G"

                # This function will return a single digit runway number if no suffix and
                # mathmatically calculated. This is required for df searches.
                return str(rwy_opp)
        raise ValueError(f"{runway} is not a valid string")

    @staticmethod
    def runway_print(runway:str) -> str:
        """Returns a printable runway complete with spaces"""

        if len(runway) == 1 and re.match(r"^\d{1}$", runway):
            # Two spaces
            return f"0{runway}  "
        if len(runway) == 2 and re.match(r"^\d{1}[LRCXG]$", runway):
            # Single space
            return f"0{runway} "
        if len(runway) == 2 and re.match(r"^\d{2}$", runway):
            # Two spaces
            return f"{runway}  "
        if len(runway) == 3 and re.match(r"^\d{2}[LRCXG]$", runway):
            # Single space
            return f"{runway} "
        raise ValueError(f"{runway} is an unknown input format for runway")

    @staticmethod
    def delete_zero_file_size(file:str) -> None:
        """Deletes any 0 length files"""

        if os.path.exists(file):
            file_size_bytes = os.path.getsize(file)
            if file_size_bytes == 0:
                os.remove(file)

    def get_single_coord(self, coord:str) -> str:
        """Return a single coordinate from KiloJuliett"""

        logger.debug(coord)
        coord_xform = self.build.request_output(f'{coord} {coord}')
        xform_split = coord_xform.split(" ")
        return f"{xform_split[0]} {xform_split[1]}"

    def load_df(self, file_name:str, filter_by_icao:bool=False) -> pd.DataFrame:
        """Loads a dataframe and optionally filters by icao"""
        df_to_load = os.path.join(functions.work_dir, "DataFrames", file_name)
        loaded_df = pd.read_csv(df_to_load)
        if filter_by_icao:
            loaded_df = loaded_df[loaded_df["aerodrome"] == self.icao]
        return loaded_df

    def txt_airspace(self) -> None:
        """Build the 'Airspace.txt' file"""

        start = True
        data:dict = {}
        ats_data = self.load_df("AA - ATS.csv", True)
        file_path = os.path.join(self.airport_dir, "Airspace.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            for index, row in ats_data.iterrows():
                # Loop through every row the filter returns for this icao aerodrome
                logger.trace(index)
                des_split = str(row["designation"]).split("  ", maxsplit=2)
                # Turn 'THIS PLACE ATZ' into 'This Place ATZ'
                data["p_title"] = des_split[0].title().split()
                data["p_title"][-1] = data["p_title"][-1].upper()
                data["p_title"] = " ".join(data["p_title"])
                # Request data
                if self.no_build:
                    sct_data = ["The 'no build' option has been selected...", des_split[1]]
                else:
                    # Filter out long winded text
                    short_filter = des_split[1]
                    if re.search("longest", short_filter):
                        short_filter = des_split[1].split("longest", maxsplit=1)[0]
                    # This MUST be an if and not an elif due to the GURNSEY ATZ problem
                    if re.search("extending", short_filter):
                        short_filter = des_split[1].split("extending", maxsplit=1)[0]
                    sct_data_output = self.build.request_output(short_filter)
                    # Split any returned data into a list
                    sct_data = sct_data_output.split("\n")

                data["limits"] = lists.Regex.vertical_limits(row["vertical_limits"])
                data["title"] = (f"{data['p_title']} {row['airspace_class']} "
                                 f"{data['limits'][2]}-{data['limits'][1]}")
                # Loop through every coordinate returned
                for idx, item in enumerate(sct_data):
                    if idx == 0:
                        title = f"\n;{data['title']}\n"
                        if start:
                            title = f";{data['title']}\n"
                            start = False
                        file.write(title)
                    line = f"{self.icao} {data['p_title']} {item}\n"
                    file.write(line)
        self.delete_zero_file_size(file_path)

    def text_basic(self) -> None:
        """
        Build the 'Basic.txt' file
        https://github.com/VATSIM-UK/UK-Sector-File/wiki/Basic.txt
        Line 1: Airport name
        Line 2: Airport lat / lon
        Line 3: Primary frequency
        """

        try:
            df_load = self.load_df(f"{self.icao}_0.csv")
        except FileNotFoundError as error:
            logger.warning(f"{error} - No files found for {self.icao}")
            return None
        basic_data = process.ProcessAerodromes.ad_2_2(df_load)
        # Request data
        if self.no_build and basic_data:
            coord_out = (f"The 'no build' option has been selected...\n{basic_data['arp_lat']} "
                        f"{basic_data['arp_lon']}")
        elif basic_data:
            # Needs to be sent as double coords due to 3rd party limitations
            coord_row = f"{basic_data['arp_lat']} {basic_data['arp_lon']}"
            coord_xform = self.build.request_output(f'{coord_row} {coord_row}')
            xform_split = coord_xform.split(" ")
            coord_out = f"{xform_split[0]} {xform_split[1]}"
        self.coord = coord_out
        file_path = os.path.join(self.airport_dir, "Basic.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.icao_title + "\n")
            file.write(coord_out + "\n")
            # Third line is written in txt_positions
        self.delete_zero_file_size(file_path)
        return None

    @staticmethod
    def text_centerline() -> None:
        """Build the 'Centreline.txt' file"""
        logger.warning("Inactive module")

    @staticmethod
    def text_fixes() -> None:
        """Build the 'Fixes.txt' file"""
        logger.warning("Inactive module")

    @staticmethod
    def text_freetext() -> None:
        """Build the 'Freetext.txt' file"""
        logger.warning("Inactive module")

    @staticmethod
    def text_ownership() -> None:
        """Build the 'Ownership.txt' file"""
        logger.warning("Inactive module")

    def text_positions(self) -> None:
        """Build the 'Positions.txt' file"""

        # Check that aerodrome coordinates have been set
        if self.coord is None:
            raise ValueError("Coordinates have not been set")

        data:dict = {}
        data["ignore"] = []
        runway_data = self.load_df("AA - COMMS.csv", True)
        file_path = os.path.join(self.airport_dir, "Positions.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            for index, row in runway_data.iterrows():
                logger.trace(index)
                data["cs_split"] = str(row["callsign"]).split()
                cs_mapping = {
                    "RADAR": (f"{self.icao}_APP", f"{self.icao[-2]}{self.icao[-1]}R"),
                    "APPROACH": (f"{self.icao}_APP", f"{self.icao[-2]}{self.icao[-1]}F"),
                    "DIRECTOR": (f"{self.icao}_F_APP", f"{self.icao[-2]}{self.icao[-1]}F"),
                    "TOWER": (f"{self.icao}_TWR", f"{self.icao[-2]}{self.icao[-1]}T"),
                    "GROUND": (f"{self.icao}_GND", f"{self.icao[-2]}{self.icao[-1]}G"),
                    "DELIVERY": (f"{self.icao}_DEL", f"{self.icao[-2]}{self.icao[-1]}D"),
                    "RADIO": (f"{self.icao}_R_TWR", f"{self.icao[-2]}{self.icao[-1]}T"),
                    "INFORMATION": (f"{self.icao}_INFORMATION", f"{self.icao[-2]}{self.icao[-1]}T"),
                }

                # Check if data["cs_split"] has two elements
                if len(data["cs_split"]) == 2:
                    # Check if data["cs_split"][1] exists in the cs_mapping dictionary
                    if data["cs_split"][1] in cs_mapping and len(data["cs_split"]) == 2:
                        # Get the corresponding callsign and short values
                        data["callsign"], data["short"] = cs_mapping[data["cs_split"][1]]
                        if row["designation"] == "ATIS" and data["cs_split"][1] == "INFORMATION":
                            data["callsign"] = f"{self.icao}_ATIS"
                    else:
                        # If nothing matches then skip this row
                        continue
                else:
                    # If nothing matches then skip this row
                    continue

                data["middle"] = "D"
                if data["cs_split"][1] == "ATIS":
                    data["middle"] = "S"

                freq = lists.Regex.frequency(row["frequency"])
                if freq:
                    freq_out = freq[1]
                else:
                    freq_out = "None"

                data["rt"] = str(row["callsign"]).title()
                data["psfix"] = data['callsign'].split("_")
                data["ll"] = self.coord.split()
                data["freq"] = freq_out
                if data["callsign"] == f"{self.icao}_TWR":
                    file_basic = os.path.join(self.airport_dir, "Basic.txt")
                    with open(file_basic, "a", encoding="utf-8") as file_b:
                        file_b.write(data["freq"])

                if data['psfix'][-1] != "ATIS":
                    data["entry"] = (
                        f"{data['callsign']}:{data['rt']}:{data['freq']}:{data['short']}:"
                        f"{data['middle']}:{data['psfix'][0]}:{data['psfix'][-1]}:-:-:"
                        f"CODE:CODE:{data['ll'][0]}:{data['ll'][1]}::")
                else:
                    data["entry"] = (
                        f"{data['callsign']}:{data['rt']}:{data['freq']}:{data['short']}:"
                        f"{data['middle']}:{data['psfix'][0]}:{data['psfix'][-1]}:-:-::::::")
                file.write(f"{data['entry']}\n")

    @staticmethod
    def text_positions_mentor() -> None:
        """Build the 'Positions_Mentor.txt' file"""
        logger.warning("Inactive module")

    def text_runway(self) -> None:
        """
        Build the 'Runway.txt' file
        https://github.com/VATSIM-UK/UK-Sector-File/wiki/Runway.txt
        Space separated
        1. Runway number with optional L, R or C suffix
        2. Runway number for opposite end
        3. Magnetic runway heading
        4. Magnetic runway heading for opposite end
        5. Runway start lat
        6. Runway start lon
        7. Runway end lat
        8. Runway end lon
        """

        data:dict = {}
        data["ignore"] = []
        runway_data = self.load_df("AA - RUNWAYS.csv", True)
        file_path = os.path.join(self.airport_dir, "Runway.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            for index, row in runway_data.iterrows():
                if (index not in data["ignore"] and
                    pd.notna(row["coordinates"]) and
                    pd.notna(row["bearing"])):
                    data["opp_runway"] = self.runway_flip_flop(row["rwy"])
                    data["runway"] = row["rwy"]
                    data["bearing"] = re.match(r"^(\d+(\.\d+)?)", str(row["bearing"]))
                    data["bearing"] = round(float(data["bearing"][1]))
                    data["coords"] = lists.Regex.coordinates(row["coordinates"], False)

                    # Create a filtered df to identify the opposite end of the runway
                    df_opp = runway_data[runway_data["rwy"] == data["opp_runway"]]
                    if len(df_opp) == 1:
                        # Add this index to the ignore list so we don't duplicate
                        data["ignore"].append(df_opp.index)
                        data["opp_bearing"] = re.match(
                            r"^(\d+(\.\d+)?)", str(df_opp["bearing"].values[0]))
                        data["opp_bearing"] = round(float(data["opp_bearing"][1]))
                        data["opp_coords"] = lists.Regex.coordinates(
                            df_opp["coordinates"].values[0], False)
                    else:
                        logger.warning(
                            f"An unusual number of runways were returned for {self.icao}")
                        continue

                    # Request data
                    if self.no_build:
                        sct_data = "The 'no build' option has been selected..."
                    else:
                        # Needs to be sent as double coords due to 3rd party limitations
                        coord_out = f"{data['coords'][1]} {data['coords'][3]}"
                        data["end_a"] = self.get_single_coord(coord_out)
                        coord_out = f"{data['opp_coords'][1]} {data['opp_coords'][3]}"
                        data["end_b"] = self.get_single_coord(coord_out)
                        sct_data = f"{data['end_a']} {data['end_b']}"

                    line = (f"{self.runway_print(data['runway'])}"
                            f"{self.runway_print(data['opp_runway'])}"
                            f"{str(data['bearing']).zfill(3)} {str(data['opp_bearing']).zfill(3)} "
                            f"{sct_data}")
                    file.write(line + "\n")
        self.delete_zero_file_size(file_path)

    @staticmethod
    def text_smaa() -> None:
        """Build the 'SMAA.txt' file"""
        logger.warning("Inactive module")

    @staticmethod
    def text_sector() -> None:
        """Build the 'Sector.txt' file"""
        logger.warning("Inactive module")

    @staticmethod
    def text_vrps() -> None:
        """Build the 'VRPs.txt' file"""
        logger.warning("Inactive module")
