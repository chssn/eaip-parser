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
    def north_south(arg):
        """Turns a compass point into the correct + or - for lat and long"""
        if arg == '+':
            return "N"
        return "S"

    @staticmethod
    def east_west(arg):
        """Turns a compass point into the correct + or - for lat and long"""
        if arg == '+':
            return "E"
        return "W"

    @staticmethod
    def plus_minus(arg):
        """Turns a compass point into the correct + or - for lat and long"""
        if arg in ('N','E'):
            return "+"
        return "-"

    @staticmethod
    def back_bearing(brg):
        """Calculates a back bearing"""
        if (float(brg) - 180) < 0:
            back = float(brg) + 180.00
        else:
            back = float(brg) - 180.00
        return round(back, 2)
