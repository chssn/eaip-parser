"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import math
import os
import re

# Third Party Libraries
from loguru import logger

# Local Libraries

work_dir = os.path.dirname(__file__)

def split(word:str) -> list:
    """Splits a word and returns as a list"""
    if isinstance(word, str):
        return [char for char in word]
    raise ValueError("This function can only process strings.")

class Geo:
    """Class containing various geo tools"""

    @staticmethod
    def north_south(arg:str) -> str:
        """Turns a compass point into the correct + or - for lat and long"""
        if arg in ("+","-"):
            if arg == '+':
                return "N"
            return "S"
        raise ValueError("This function only accepts a '+' or '-' as an input!")

    @staticmethod
    def east_west(arg:str) -> str:
        """Turns a compass point into the correct + or - for lat and long"""
        if arg in ("+","-"):
            if arg == '+':
                return "E"
            return "W"
        raise ValueError("This function only accepts a '+' or '-' as an input!")

    @staticmethod
    def plus_minus(arg:str) -> str:
        """Turns a compass point into the correct + or - for lat and long"""
        if arg in ("N","E","S","W"):
            if arg in ('N','E'):
                return "+"
            return "-"
        raise ValueError("This function only accepts a 'N', 'E', 'S' or 'W' as an input!")

    @staticmethod
    def back_bearing(brg:float) -> float:
        """Calculates a back bearing"""
        if float(brg) <= 360 and float(brg) >=0:
            if (float(brg) - 180) < 0:
                back = float(brg) + 180
            else:
                back = float(brg) - 180
            return round(back, 2)
        raise ValueError("This function only accepts an input between 0 and 360")

    @staticmethod
    def dd2dms(latitude:float, longitude:float) -> str:
        """Converts Decimal Degrees to Degress, Minutes and Seconds"""

        if isinstance(latitude, float) and isinstance(longitude, float):
            # math.modf() splits whole number and decimal into tuple
            # eg 53.3478 becomes (0.3478, 53)
            split_degx = math.modf(longitude)

            # the whole number [index 1] is the degrees
            degrees_x = int(split_degx[1])

            # multiply the decimal part by 60: 0.3478 * 60 = 20.868
            # split the whole number part of the total as the minutes: 20
            # abs() absoulte value - no negative
            minutes_x = abs(int(math.modf(split_degx[0] * 60)[1]))

            # multiply the decimal part of the split above by 60 to get the seconds
            # 0.868 x 60 = 52.08, round excess decimal places to 2 places
            # abs() absoulte value - no negative
            seconds_x = abs(round(math.modf(split_degx[0] * 60)[0] * 60,2))

            # repeat for latitude
            split_degy = math.modf(latitude)
            degrees_y = int(split_degy[1])
            minutes_y = abs(int(math.modf(split_degy[0] * 60)[1]))
            seconds_y = abs(round(math.modf(split_degy[0] * 60)[0] * 60,2))

            # account for E/W & N/S
            if longitude < 0:
                e_or_w = "W"
            else:
                e_or_w = "E"

            if latitude < 0:
                n_or_s = "S"
            else:
                n_or_s = "N"

            # abs() remove negative from degrees, was only needed for if-else above
            output = (n_or_s + str(abs(round(degrees_y))).zfill(3) +
                      "." + str(round(minutes_y)).zfill(2) +
                      "." + str(seconds_y).zfill(3) +
                      " " + e_or_w + str(abs(round(degrees_x))).zfill(3) +
                      "." + str(round(minutes_x)).zfill(2) +
                      "." + str(seconds_x).zfill(3)
                      )

            return output
        else:
            raise ValueError("This function expects floats to be passed to it.")

    @staticmethod
    def dms2dd(lat:str, lon:str) -> list:
        """Converts Degress, Minutes and Seconds to Decimal Degrees"""

        lat_split = re.search(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3}\.?\d{0,3})", lat)
        if not lat_split:
            lat_split = re.search(r"^(\d{2})(\d{2})(\d{2})([NS]{1})$", lat)
        n_or_s = re.search(r"([NS]{1})", lat)

        lon_split = re.search(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3}\.?\d{0,3})", lon)
        if not lon_split:
            lon_split = re.search(r"^(\d{3})(\d{2})(\d{2})([EW]{1})$", lon)
        e_or_w = re.search(r"([EW]{1})", lon)

        if lat_split and n_or_s and lon_split and e_or_w:
            lat_dd = lat_split[1]
            lat_mm = lat_split[2]
            lat_ss = lat_split[3]
            lat_out = int(lat_dd) + int(lat_mm) / 60 + float(lat_ss) / 3600

            lon_dd = lon_split[1]
            lon_mm = lon_split[2]
            lon_ss = lon_split[3]
            lon_out = int(lon_dd) + int(lon_mm) / 60 + float(lon_ss) / 3600

            if n_or_s[1] == "S":
                lat_out = lat_out - (lat_out * 2)
            if e_or_w[1] == "W":
                lon_out = lon_out - (lon_out * 2)

            return [lat_out, lon_out]
        else:
            logger.debug(f"{lat} {lat_split}")
            logger.debug(f"{lon} {lon_split}")
            raise ValueError(
                "This function accepts lat/lon in the format DDD.MMM.SSS.sss \
                     or DDMMSS / DDDMMSS prefixed or suffixed by N, S, E or W"
                )
