"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.9

# Standard Libraries
import difflib
import os
import re

# Third Party Libraries
from loguru import logger

# Local Libraries
from eaip_parser import functions


class UkSectorFile:
    """Carry out validation of the UK Sector File"""

    def __init__(self) -> None:
        self._git_actions()

    def _git_actions(self) -> None:
        """Some git actions to compare against"""
        git = functions.GitActions()
        self.root_dir = git.git_path
        if git.check_requirements():
            if git.clone():
                git.pull()

    @staticmethod
    def find_files_by_regex(pattern:str, dir_path:str) -> dict:
        """Return a list of files that match the given regex"""
        matching_files:dict = {}
        for root, _, files in os.walk(dir_path):
            for filename in files:
                search = re.match(pattern, filename)
                if search:
                    full_path = os.path.join(root, filename)
                    matching_files[search[1]] = full_path

        return matching_files

    @staticmethod
    def list_match(list_to_match:list, list_to_compare:list) -> list:
        """Find matches and non-matches from comparing two lists"""
        logger.debug(list_to_match)
        logger.debug(list_to_compare)
        match_list = []
        no_match_list = []
        # Iterrate over the first list
        for item_m in list_to_match:
            # Check to see if each item in the first list exists in the second list
            for item_c in list_to_compare:
                if item_m == item_c:
                    match_list.append(item_m)
                    break
            else:
                logger.trace(f"No match for {item_m}")
                no_match_list.append(item_m)

        # Return two lists of matches and non-matches
        match_list.sort()
        no_match_list.sort()
        return [match_list, no_match_list]

    @staticmethod
    def read_file(file_path) -> list:
        """
        Read the content of a file and return it as a list of lines,
        stripping trailing whitespace.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.rstrip() for line in file]

    def compare(self, file_a:str, file_b:str):
        """Compare two items"""
        # Read file contents into variables
        lines_a = self.read_file(file_a)
        lines_b = self.read_file(file_b)

        diff = difflib.unified_diff(
            lines_a,
            lines_b,
            fromfile=file_a,
            tofile=file_b,
            lineterm=''
            )
        for line in diff:
            print(line.rstrip("\n"))

    def airways_rnav(self):
        """Run validation on rnav airways"""

        # Put all of the current sector file (csf) airways into a list
        sectorfile_rnav_lower = self.find_files_by_regex(
            "(.+)", self.root_dir + "\\ATS Routes\\RNAV\\Lower")
        sectorfile_rnav_upper = self.find_files_by_regex(
            "(.+)", self.root_dir + "\\ATS Routes\\RNAV\\Upper")
        # Put all of the scraped airways into a list
        file_path = os.path.join(functions.work_dir, "DataFrames")
        scraped_rnav_lower = self.find_files_by_regex("ENR-3.2-LOWER-(.+)", file_path)
        scraped_rnav_upper = self.find_files_by_regex("ENR-3.2-UPPER-(.+)", file_path)

        logger.debug(sectorfile_rnav_lower)
        logger.debug(scraped_rnav_lower)
        logger.debug(sectorfile_rnav_upper)
        logger.debug(scraped_rnav_upper)

        for file, file_path in sectorfile_rnav_lower.items():
            self.compare(file_path, scraped_rnav_lower[file])

    def vor_dme_tacan(self):
        """Run comparison on VOR DME TACAN lists"""
        file_a = os.path.join(functions.work_dir, "UK-Sector-File", "Navaids", "VOR_UK.txt")
        file_b = os.path.join(functions.work_dir, "DataFrames", "VOR_UK.txt")
        self.compare(file_a, file_b)
