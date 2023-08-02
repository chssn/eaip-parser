"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import re

# A list of country codes and associated language
country_codes = {
    "EG": "en-GB",
}

# A list of sections contained in the eAIP excluding aerodrome specific pages
eaip_sections = [
    "ENR-1.6",
    "ENR-1.8",
    "ENR-2.1",
    "ENR-2.2",
    "ENR-3.1",
    "ENR-3.2",
    "ENR-3.3",
    "ENR-3.4",
    "ENR-4.1",
    "ENR-4.2",
    "ENR-4.4",
    "ENR-5.1",
    "ENR-5.2",
    "ENR-5.3",
    "ENR-5.4",
    "ENR-5.5",
    "ENR-5.6",
    "AD-1.3",
]

# Column headers for airspace tables (ENR 2)
column_headers_airspace = [
    "data",
    "unit",
    "callsign",
    "frequency",
    "remarks",
]

# Column headers for route tables (ENR 3)
column_headers_route = [
    "route",
    "name",
    "coordinates_bearing",
    "distance",
    "vertical_limits",
    "ifr_limits_even",
    "ifr_limits_odd",
    "del1",
    "del2",
    "del3",
]

# Column headers for navigation warning areas (ENR 5)
column_headers_nav_warn = [
    "area",
    "vert_limits",
    "remarks",
]


class Regex:
    """A whole host of regex patterns"""

    @staticmethod
    def flight_level(string_to_search:str) -> list:
        """Searches for a bunch of flight levels"""
        return re.findall(r"(FL\s\d{2,3})", str(string_to_search))

    @staticmethod
    def lateral_limits(string_to_search:str) -> list:
        """Searches for lateral limits"""
        return re.match(r"^([A-Z0-9\s]+)(\s\d{6}(\.\d{2})?[NS]{1}.*)", str(string_to_search))

    @staticmethod
    def frequency(string_to_search:str, anchor:bool=False) -> list:
        """Searches for a frequency"""
        if anchor:
            return re.match(r"^(\d{3}\.\d{3})$", str(string_to_search))
        return re.match(r"(\d{3}\.\d{3})", str(string_to_search))

    @staticmethod
    def coordinates(string_to_search:str) -> list:
        """Searches for a coordinate pair"""
        return re.match(
            r"^(\d{6}(\.\d{2})?[NS])(?:\s+)(\d{7}(\.\d{2})?[EW])$",
            str(string_to_search)
            )

    @staticmethod
    def tacan_channel(string_to_search:str) -> list:
        """Searches for a bunch of flight levels"""
        return re.match(r"(\d{2,3}[XY]{1})", str(string_to_search))

    @staticmethod
    def vor_dme_ndb(string_to_search:str) -> list:
        """Searches for the word(s) VOR, DME and NDB"""
        return re.match(
            r"^([A-Z\s\']+)\s\s([VORDMENB]{3}(\/[VORDMENB]{3})?)",
            str(string_to_search)
            )
