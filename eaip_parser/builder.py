"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import json
import re
import time
from dataclasses import dataclass

# Third Party Libraries
import requests
from loguru import logger

# Local Libraries


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

    def __init__(self, base_url:str="https://kilojuliett.ch:443/webtools/geo/json") -> None:
        self.request_settings = {}
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

        lat = re.findall(r"([NS])(\d{3})", coords)
        lon = re.findall(r"([EW])(\d{3})", coords)
        for item in lat:
            if item[0] == "S":
                logger.error(f"{item} not within UK bounds!\n{coords}")
                return False
            if int(item[1]) < 46 or int(item[1]) > 62:
                logger.error(f"{item} not within UK bounds!\n{coords}")
                return False
        for item in lon:
            if item[0] == "W" and int(item[1]) > 11:
                logger.error(f"{item} not within UK bounds!\n{coords}")
                return False
            if item[0] == "E" and int(item[1]) > 2:
                logger.error(f"{item} not within UK bounds!\n{coords}")
                return False

        return True

    def request_output(self, data_in:str) -> str:
        """
        Requests the transformed input data from
        https://kilojuliett.ch/webtools/geo/coordinatesconverter
        """

        self.request_settings["input"] = data_in
        logger.trace(data_in)

        headers = {
            "Sec-Ch-Ua": "",
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
            "Accept-Encoding": "gzip, deflate",
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
                raise ValueError(f"Failed with input data\n{data_in}")

        raise requests.HTTPError(f"{self.base_url} not found")
