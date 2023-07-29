"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import filecmp
import os
import re

# Third Party Libraries
from loguru import logger

# Local Libraries
from . import functions


class UkSectorFile():
    """Carry out validation of the UK Sector File"""

    def __init__(self) -> None:
        git = functions.GitActions()
        self.root_dir = git.git_path

    @staticmethod
    def find_files_by_regex(pattern:str, dir_path:str) -> list:
        """Return a list of files that match the given regex"""
        matching_files = []
        matching_full_path = []
        for root, _, files in os.walk(dir_path):
            for filename in files:
                search = re.match(pattern, filename)
                if search:
                    matching_full_path.append(os.path.join(root, filename))
                    matching_files.append(search.group(1))
        return [matching_files, matching_full_path]

    def airways_rnav(self):
        """Run validation on rnav airways"""

        # Put all of the current sector file (csf) lower airways into a list
        csf_rnav_lower = self.find_files_by_regex("(.+)", self.root_dir + "\\Airways\\RNAV\\Lower")
        # Put all of the scraped lower airways into a list
        scraped_rnav_lower = self.find_files_by_regex(
            "ENR-3.2-LOWER-(.*)", functions.work_dir + "\\DataFrames")

        def list_match(list_to_match:list, list_to_compare:list) -> list:
            match_list = []
            no_match_list = []
            for item in list_to_match:
                if item in list_to_compare:
                    match_list.append(item)
                else:
                    logger.trace(f"No match for {item}")
                    no_match_list.append(item)
            return [match_list, no_match_list]

        # Produce lists of matching and non-matching file names as a starter
        list_match_csf = list_match(csf_rnav_lower[0], scraped_rnav_lower[0])
        list_match_scraped = list_match(scraped_rnav_lower[0], csf_rnav_lower[0])

        for file in list_match_csf[0]:
            # Get the filename from csf
            for file_fp in csf_rnav_lower[1]:
                if str(file_fp).endswith(str(file)):
                    side_a = file_fp
                    break
            # Get the filename from scrape
            for file_fp in scraped_rnav_lower[1]:
                if str(file_fp).endswith(str(file)):
                    side_b = file_fp
                    break
            # If the files don't match then do a bit more digging
            if not filecmp.cmp(side_a, side_b, shallow=False):
                logger.trace(f"{file} doesn't match")
                with open(side_a, "r", encoding="utf-8") as file_a, open(side_b, "r", encoding="utf-8") as file_b:
                    check_okay = True
                    lines_a = file_a.readlines()
                    lines_b = file_b.readlines()
                    end_a = str(side_a).split('\\')[-1]
                    end_b = str(side_b).split('\\')[-1]
                    for line_a, line_b in zip(lines_a, lines_b):
                        match_a = re.match(
                            r"^([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\n$",
                            line_a)
                        match_b = re.match(
                            r"^([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\n$",
                            line_b)
                        if match_a and match_b:
                            if (match_a.group(1) == match_b.group(1) and
                                match_a.group(2) == match_b.group(2) and
                                match_a.group(3) == match_b.group(3) and
                                match_a.group(4) == match_b.group(4)):
                                pass
                            else:
                                check_okay = False
                                if line_a in lines_b:
                                    logger.info(end_a)
                                    logger.info(
                                        f"{line_a.rstrip()} wasn't in the expected place "
                                        f"however does exist in {end_b}")
                                elif line_b in line_a:
                                    logger.info(end_b)
                                    logger.info(
                                        f"{line_b.rstrip()} wasn't in the expected place "
                                        f"however does exist in {end_a}")
                                elif (match_a.group(1) == match_b.group(3) and
                                      match_a.group(2) == match_b.group(4)):
                                    logger.warning(f"{file} may be back-to-front")
                                else:
                                    logger.error(f"No match for contents of {file}")
                                    logger.trace(f"{side_a} - {line_a.rstrip()}")
                                    logger.trace(f"{side_b} - {line_b.rstrip()}")
                    if check_okay:
                        logger.trace(f"Full line match for {file}")
                    else:
                        print(f"{end_a}  |  {end_b}")
                        for line_a, line_b in zip(lines_a, lines_b):
                            print(f"{line_a.rstrip()}  |  {line_b.rstrip()}")

        for file in list_match_scraped[1]:
            logger.error(f"{file} doesn't exist")
