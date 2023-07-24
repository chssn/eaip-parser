"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import os

# Third Party Libraries

# Local Libraries

work_dir = os.path.dirname(__file__)

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
