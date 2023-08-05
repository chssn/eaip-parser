"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import math
import os
import re
import shutil
import subprocess

# Third Party Libraries
import git
from loguru import logger

# Local Libraries

work_dir = os.path.dirname(__file__)
logger.debug(f"Working directory is {work_dir}")

def copy_files(file:str, destination:str) -> None:
    """Copy files from A to B"""

    # Check if the destination directory exists, if not then create it
    if not os.path.exists(destination):
        os.makedirs(destination)

    shutil.copy(file, destination)

def split(word:str) -> list:
    """Splits a word and returns as a list"""
    if isinstance(word, str):
        return list(word)
    raise ValueError("This function can only process strings.")

def generate_file_names(file_start:str, file_type:str="csv") -> list:
    """Generates an incremental list of filenames"""

    path = os.path.join(work_dir, "DataFrames")
    enr_files = ([file for file in os.listdir(path) if
                    file.startswith(file_start) and file.endswith(file_type)])
    return enr_files

def is_25khz(frequency:str):
    """
    Works out if the given frequency is 25KHz
    Returns FALSE if this is a 25KHz frequency (the logic is much easier that way)
    If not, rounds to the nearest 25KHz
    """

    freq_match = re.match(r"^(\d{3})\.(\d{3})$", frequency)
    if freq_match:
        if frequency.endswith(("00", "25", "50", "75")):
            return False
        round_decimal = round(int(freq_match[2]) / 25) * 25
        if round_decimal == 1000:
            return f"{str(int(freq_match[1])+1)}.000"
        return f"{freq_match[1]}.{str(round_decimal).zfill(3)}"
    raise ValueError("Expected frequency in the format nnn.nnn MHz")


class GitActions:
    """
    Performs git actions on the defined repo
    """

    def __init__(self, git_folder:str="UK-Sector-File", branch:str="main") -> None:
        # Currently hardcoded for VATSIM UK
        self.repo_url = "https://github.com/VATSIM-UK/UK-Sector-File.git"

        # Set some git vars
        self.branch = branch
        self.git_folder = git_folder
        self.git_path = f"{work_dir}\\{git_folder}"

    @staticmethod
    def is_git_installed() -> bool:
        """Checks to see if the git package is installed"""
        try:
            # Execute the git command to check if it is recognized
            version = subprocess.check_output(['git', '--version'])
            logger.debug(f"Git is installed - {str(version.decode()).strip()}")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    @staticmethod
    def install_git() -> bool:
        """Trys to install the git package"""
        logger.info("Lauching PowerShell to run the following command:"
                    "winget install --id Git.Git -e --source winget")
        logger.info("You can find out more about winget here - "
                    "https://learn.microsoft.com/en-us/windows/package-manager/winget/")

        # Run the PowerShell command and capture the completed process
        completed_process = subprocess.run(
            ["powershell.exe", "-Command", "winget install --id Git.Git -e --source winget"],
            capture_output=True,
            text=True,
            shell=True,
            check=True
        )

        # Check the return code of the completed process
        if completed_process.returncode == 0:
            logger.success("PowerShell command executed successfully.")
            return True
        logger.error("PowerShell command failed with exit status:", completed_process.returncode)
        logger.error("Error output:", completed_process.stderr)
        return False

    def check_requirements(self) -> bool:
        """Checks to see if the basic requirements are satisfied"""

        # Test if Git is installed
        if not self.is_git_installed():
            logger.error("Git is not installed")
            print("For this tool to work properly, the 'git' package is required.")
            print("This tool can automatically download the 'git' package from:")
            print("\thttps://git-scm.com/download/win")
            consent = input("Are you happy for this tool to install 'git'? [Y|n] ")
            if consent.upper() == "Y" or consent is None:
                logger.success("User has constented to the 'git' package being installed")
                if self.install_git():
                    logger.success("Git has been installed")
                    return True
            logger.error("User has not consented to the 'git' package being installed")
            return False
        return True

    def clone(self) -> bool:
        """
        Perform the clone operation. Returns TRUE if the folder already exists and FALSE if not
        """

        folder = f"{self.git_path}"
        if os.path.exists(folder):
            logger.success(f"The repo has already been cloned to {folder}")
            return True
        logger.info(f"Cloning into {self.repo_url}")
        git.Repo.clone_from(self.repo_url, folder, branch=self.branch)
        logger.success("The repo has been successfully cloned")
        return False

    def pull(self) -> bool:
        """Performs a 'git pull' operation"""
        if os.path.exists(self.git_path):
            logger.info(f"Pulling changes from {self.repo_url} to {self.git_path}")

            # Open the repository
            repo = git.Repo(self.git_path)

            if str(repo.active_branch) == str(self.branch):
                # Pull the latest commit
                logger.debug(f"Pull {self.repo_url}")
                repo.git.pull()
        else:
            raise FileNotFoundError(self.git_path)
        return False


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
        raise ValueError("This function expects floats to be passed to it.")

    @staticmethod
    def dms2dd(lat:str, lon:str) -> dict:
        """Converts Degress, Minutes and Seconds to Decimal Degrees"""

        # try and match DDD.MMM.SSS.sss latitude
        lat_split = re.search(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3}\.?\d{0,3})", lat)
        if not lat_split:
            # try and match DDMMSS latitude
            lat_split = re.search(r"^(\d{2})(\d{2})(\d{2})([NS]{1})$", lat)
        n_or_s = re.search(r"([NS]{1})", lat)

        # try and match DDD.MMM.SSS.sss longitude
        lon_split = re.search(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3}\.?\d{0,3})", lon)
        if not lon_split:
            # try and match DDDMMSS longitude
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

            return_coords = {
                "lat": lat_out,
                "lon": lon_out,
            }
            return return_coords
        logger.debug(f"{lat} {lat_split}")
        logger.debug(f"{lon} {lon_split}")
        raise ValueError(
            "This function accepts lat/lon in the format DDD.MMM.SSS.sss \
                    or DDMMSS / DDDMMSS prefixed or suffixed by N, S, E or W"
            )


class NoUrlDataFoundError(Exception):
    """Exception raised when no data has been found at the given url"""

    def __init__(self, url:str, message:str="No data found at the given url") -> None:
        self.url = url
        self.message = message
        super().__init__(f"{self.message} - {self.url}")


class TacanVor:
    """Converts TACAN to VOR and vice versa"""

    @staticmethod
    def validate_tacan(tacan:str) -> tuple:
        """Validates a string to see if it is a TACAN channel"""

        validate = re.match(r"^(\d{1,3})([XY]{1})$", tacan)
        if validate:
            return (validate[1], validate[2])
        raise ValueError("TACAN channels are in the format (\\d{1,3})([XY]{1})")

    def tacan_to_vor_ils(self, tacan:str) -> str:
        """Converts TACAN to VOR"""

        validate = self.validate_tacan(tacan)

        # VOR & ILS in the range 17X to 59Y and 70X to 126Y
        # Start from 17X = 108.00MHz and 70X = 112.3MHz
        # For each int increase then this should be +100KHz
        # If the suffix is X then nothing else needs doing
        # If the suffix is Y then an additional +50KHz
        # source: https://wiki.radioreference.com/index.php/\
        # Instrument_Landing_System_(ILS)_Frequencies

        if int(validate[0]) >= 17 and int(validate[0]) <= 59:
            diff = int(validate[0]) - 17
            increment = (diff * 0.1) + 108
            if validate[1] == "Y":
                increment += 0.05
        elif int(validate[0]) >= 70 and int(validate[0]) <= 126:
            diff = int(validate[0]) - 70
            increment = (diff * 0.1) + 112.3
            if validate[1] == "Y":
                increment += 0.05
        else:
            raise ValueError("Channel needs to be in the range 17-59 and 70-126")
        return str(format(increment, '.2f'))
