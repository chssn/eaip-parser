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


class UkSectorFile:
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

    @staticmethod
    def quick_split(input:list) -> list:
        """Quickly splits something"""
        split_a = []
        for lni in input:
            lines_split = str(lni).split(" ")
            for item in lines_split:
                if item != "":
                    split_a.append(item.rstrip("\n"))
        return split_a

    def airways_rnav(self):
        """Run validation on rnav airways"""

        def list_match(list_to_match:list, list_to_compare:list) -> list:
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

        def comparison(
                csf_list:list,
                scraped_list:list,
                a_type:str,
                csf_list_full:list,
                scraped_list_full:list
                ) -> None:
            for file in csf_list:
                quick_a = 0
                quick_b = 0
                # Get the filename from csf
                for file_fp in csf_list_full[1]:
                    if str(file_fp).endswith(str(file)):
                        side_a = file_fp
                        logger.debug(side_a)
                        quick_a = str(side_a).split("\\")[-1]
                        break
                # Get the filename from scrape
                for file_fp in scraped_list_full[1]:
                    if str(file_fp).endswith(str(f"{a_type}-{file}")):
                        side_b = file_fp
                        logger.debug(side_b)
                        quick_b = str(side_b).split("-")[-1]
                        break
                if quick_a != quick_b or (quick_a == 0 and quick_b == 0):
                    raise ValueError(f"{quick_a} != {quick_b} :: {file}")
                # If the files don't match then do a bit more digging
                if not filecmp.cmp(side_a, side_b, shallow=False):
                    logger.trace(f"{file} doesn't match")
                    # Open both files side by side
                    with open(side_a, "r", encoding="utf-8") as file_a, \
                        open(side_b, "r", encoding="utf-8") as file_b:
                        check_okay = True
                        # Read file contents into variables
                        lines_a = file_a.readlines()
                        lines_b = file_b.readlines()
                        end_a = str(side_a).split('\\')[-1]
                        end_b = str(side_b).split('\\')[-1]
                        logger.debug(end_b)
                        for line_a, line_b in zip(lines_a, lines_b):
                            # Regex to match the line formatting of:
                            # POINT_A POINT_A POINT_B POINT_B
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
                                    # If points in both line A and line B match exactly...
                                    continue
                                else:
                                    check_okay = False
                                    if line_a in lines_b:
                                        # If line A exists somewhere in file B
                                        logger.info(
                                            f"{line_a.rstrip()} wasn't at the expected place in "
                                            f"{end_a}, however does exist in {end_b}")
                                    elif line_b in line_a:
                                        # If line B exists somewhere in file A
                                        logger.info(
                                            f"{line_b.rstrip()} wasn't at the expected place in "
                                            f"{end_b}, however does exist in {end_a}")
                                    else:
                                        # If there isn't any match for line A in file B...
                                        logger.trace(f"{side_a} - {line_a.rstrip()}")
                                        logger.trace(f"{side_b} - {line_b.rstrip()}")
                    if check_okay:
                        # If everything matches then there isn't anything to do!
                        logger.trace(f"Full line match for {file}")
                    else:
                        reverse_check = False
                        # Put each side into an array
                        splt_a = self.quick_split(lines_a)
                        splt_b = self.quick_split(lines_b)
                        # Reverse the second list
                        splt_b.reverse()
                        breaker = False
                        if len(splt_a) == len(splt_b):
                            for item_a, item_b in zip(splt_a, splt_b):
                                if item_a != item_b:
                                    logger.warning(f"No match - {item_a} {item_b}")
                                    breaker = True
                                    break
                            if not breaker:
                                logger.info(f"{a_type} {file} is back-to-front")
                                reverse_check = True

                        if not reverse_check:
                            # If anything doesn't line up then print both files side by side
                            logger.warning(f"No match for contents of {a_type} {file}")

                            print(f"{a_type}  |  {end_a}  |  {end_b}")
                            for line_a, line_b in zip(lines_a, lines_b):
                                print(f"{line_a.rstrip()}  |  {line_b.rstrip()}")

            for file in scraped_list:
                # If there is no matching file, then it isn't there
                    logger.error(
                        f"{a_type} {str(file).split('.')[0]} was found during the scrape but "
                        "doesn't seem to be in the current sector file")

        # Put all of the current sector file (csf) airways into a list
        csf_rnav_lower = self.find_files_by_regex("(.+)", self.root_dir + "\\Airways\\RNAV\\Lower")
        csf_rnav_upper = self.find_files_by_regex("(.+)", self.root_dir + "\\Airways\\RNAV\\Upper")
        # Put all of the scraped airways into a list
        file_path = os.path.join(functions.work_dir, "DataFrames")
        scraped_rnav_lower = self.find_files_by_regex("ENR-3.2-LOWER-(.+)", file_path)
        scraped_rnav_upper = self.find_files_by_regex("ENR-3.2-UPPER-(.+)", file_path)

        # Produce lists of matching and non-matching file names as a starter
        list_match_csf_lower = list_match(csf_rnav_lower[0], scraped_rnav_lower[0])
        list_match_scraped_lower = list_match(scraped_rnav_lower[0], csf_rnav_lower[0])
        list_match_csf_upper = list_match(csf_rnav_upper[0], scraped_rnav_upper[0])
        list_match_scraped_upper = list_match(scraped_rnav_upper[0], csf_rnav_upper[0])

        # Run the actual validation
        comparison(
            list_match_csf_lower[0],
            list_match_scraped_lower[1],
            "LOWER",
            csf_rnav_lower,
            scraped_rnav_lower
            )
        comparison(
            list_match_csf_upper[0],
            list_match_scraped_upper[1],
            "UPPER",
            csf_rnav_upper,
            scraped_rnav_upper
            )

    @staticmethod
    def compare_4(lines_a, lines_b) -> None:
        """Line by line comparator for ENR 4 data"""

        no_match = True
        for line_a, line_b in zip(lines_a, lines_b):
            logger.info("-"*60)
            if line_a.rstrip() != line_b.rstrip():
                if line_a in lines_b:
                    logger.success(f"Not in sequence - {line_a.rstrip()}")
                    no_match = False
                else:
                    split_it = line_a.split(";", maxsplit=1)[0]
                    for item in lines_b:
                        if item.startswith(split_it):
                            chk_a = line_a.rstrip().upper()
                            chk_b = item.rstrip().upper()
                            if chk_a == chk_b:
                                logger.success(f"Not in sequence - {chk_a}")
                            else:
                                logger.warning(f"A: {chk_a}")
                                logger.warning(f"B: {chk_b}")
                            no_match = False
                if no_match:
                    logger.error(f"Not found in scraped data - {line_a.rstrip()}")
            else:
                logger.success(line_a.rstrip())

    def vor_dme_tacan(self):
        """Run validation on vor list"""

        side_a = os.path.join(functions.work_dir, "UK-Sector-File", "Navaids", "VOR_UK.txt")
        side_b = os.path.join(functions.work_dir, "DataFrames", "VOR_UK.txt")
        # Open both files side by side
        with open(side_a, "r", encoding="utf-8") as file_open_a, \
            open(side_b, "r", encoding="utf-8") as file_open_b:
            # Read file contents into variables
            lines_a = file_open_a.readlines()
            lines_b = file_open_b.readlines()

            logger.critical(f"A to B")
            self.compare_4(lines_a, lines_b)
            logger.critical(f"B to A")
            self.compare_4(lines_b, lines_a)
