"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import json
import re

# Third Party Libraries
import requests
from loguru import logger

# Local Libraries


class KiloJuliett():
    """A class to build using https://kilojuliett.ch/webtools/geo/coordinatesconverter"""

    def __init__(self, base_url:str="https://kilojuliett.ch:443/webtools/geo/json") -> None:
        self.request_settings = {}
        self.base_url = base_url

    def settings(
            self,
            elnp:bool=True,
            wpt:bool=True,
            dupe:bool=True,
            xchglatlon:bool=False,
            title:bool=False,
            arctype:int=0,
            arcres:int=9,
            polynl:int=1,
            output_format:str="sct"
            ) -> None:
        """Sets the settings"""

        # New ploygon after empty line
        if elnp:
            self.request_settings["elnp"] = "on"

        # Decode waypoints
        if wpt:
            self.request_settings["wpt"] = "on"

        # Allow duplicates
        if dupe:
            self.request_settings["dupe"] = "on"

        # Switch lat/lon values
        if xchglatlon:
            self.request_settings["xchglatlon"] = "on"

        # Add polygon details
        if title:
            self.request_settings["title"] = r"%3B"

        # Add arc type
        if arctype in [0,1]:
            self.request_settings["arctype"] = arctype
        else:
            raise ValueError("Arc type can only be 1 (Orthodromic) or 2 (Loxodromic)")

        # Add arc resolution / steps in degrees
        if arcres > 0 and arcres < 180:
            self.request_settings["arcres"] = arcres
        else:
            raise ValueError("Arc resolution must be a value in degrees >0 and <180")

        # Number of new lines between polygons
        if polynl > 0 and polynl < 10:
            self.request_settings["polynl"] = polynl
        else:
            raise ValueError("Number of new lines between polygons must be >0 and <10")

        # Set output format
        formats = [
            "xls",
            "ese",
            "sct",
            "dez",
            "vrc",
            "ts-line",
            "qtsp",
            "vsys-dd"
        ]
        if output_format in formats:
            self.request_settings["format"] = output_format
        else:
            raise ValueError(f"Format type must be one of {formats}")

        logger.debug(self.request_settings)

    @staticmethod
    def data_input_validator(data:str) -> str:
        """Validates inputed data"""

        if re.search(
            r"^[NS]{1}\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?(\:|\s)"
            r"[EW]{1}\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?",
            data
            ):
            return data
        elif re.search(
            r"^\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?[NS]{1}(\:|\s)"
            r"\d{3}\.\d{2}(\.\d{2})?(\.\d{3})?[EW]{1}",
            data
            ):
            return data
        elif re.search(
            r"^[NS]{1}\d{1,2}°\d{2}\.\d{2}'\s[EW]{1}\d{1,3}°\d{2}\.\d{2}'",
            data
            ):
            return data
        elif re.search(
            r"^\d{1,2}°\d{2}\.\d{2}'[NS]{1}\s\d{1,3}°\d{2}\.\d{2}'[EW]{1}",
            data
            ):
            return data
        elif re.search(r"^\d{6}[NS]{1}\s\d{7}[EW]{1}", data):
            return data
        elif re.search(r"^[NS]{1}\d{6}\s[EW]{1}\d{6,7}", data):
            return data
        elif re.search(r"^\d{4}[NS]{1}\d{5}[EW]{1}", data):
            return data
        elif re.search(r"^\d{2}[NS]{1}\d{3}[EW]{1}", data):
            return data
        elif re.search(r"^\d{2}[NS]{1}\d{3}[EW]{1}", data):
            return data
        elif re.search(
            r"^\d{2}°\d{2}'\d{2}\"[NS]{1}\s\,\s\d{3}°\d{2}'\d{2}\"[EW]{1}",
            data
            ):
            return data
        elif re.search(
            r"^[NS]{1}\d{2}°\d{2}'\d{2}\"\s\,\s[EW]{1}\d{1,3}°\d{2}'\d{2}\"",
            data
            ):
            return data
        elif re.search(r"^\-?\d{2}\.\d{5}\,\s\-?\d{2}\.\d{6}", data):
            return data
        elif re.search(r"^[NS]{1}\d{1}\.\d{3}\,\s[EW]{1}\d{1}\.\d{3}", data):
            return data
        raise ValueError(f"The entry {data} isn't valid")

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

        response = requests.post(
            self.base_url,
            headers=headers,
            data=self.request_settings,
            timeout=30
            )

        if response.status_code != 200:
            raise requests.HTTPError(f"{self.base_url} not found")
        json_load = json.loads(response.text)

        return json_load["txt"]
