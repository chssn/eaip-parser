"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.9

# Standard Libraries
import filecmp
import os
import re

# Third Party Libraries
from loguru import logger

# Local Libraries
from eaip_parser import functions


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
                    matching_files.append(search[1])
        return [matching_files, matching_full_path]

    @staticmethod
    def quick_split(data_in:list) -> list:
        """Quickly splits something"""
        split_a = []
        for lni in data_in:
            lines_split = str(lni).split(" ")
            for item in lines_split:
                if item != "":
                    split_a.append(item.rstrip("\n"))
        return split_a

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
    def airways_line_by_line(comp_data:dict) -> dict:
        """Compare two airways line by line"""
        for line_a, line_b in zip(comp_data["lines_a"], comp_data["lines_b"]):
            # Regex to match the line formatting of:
            # POINT_A POINT_A POINT_B POINT_B
            comp_data["match_a"] = re.match(
                r"^([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\n$",
                line_a)
            comp_data["match_b"] = re.match(
                r"^([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\s+([A-Z]{3,5})\n$",
                line_b)
            if comp_data["match_a"] and comp_data["match_b"]:
                if (comp_data["match_a"][1] == comp_data["match_b"][1] and
                    comp_data["match_a"][2] == comp_data["match_b"][2] and
                    comp_data["match_a"][3] == comp_data["match_b"][3] and
                    comp_data["match_a"][4] == comp_data["match_b"][4]):
                    # If points in both line A and line B match exactly...
                    continue
                comp_data["check_ok"] = False
                if line_a in comp_data["lines_b"]:
                    # If line A exists somewhere in file B
                    logger.info(
                        f"{line_a.rstrip()} wasn't at the expected place in "
                        f"{comp_data['end_a']}, however does exist in "
                        f"{comp_data['end_b']}")
                elif line_b in line_a:
                    # If line B exists somewhere in file A
                    logger.info(
                        f"{line_b.rstrip()} wasn't at the expected place in "
                        f"{comp_data['end_b']}, however does exist in "
                        f"{comp_data['end_a']}")
                else:
                    # If there isn't any match for line A in file B...
                    logger.trace(f"{comp_data['side_a']} - {line_a.rstrip()}")
                    logger.trace(f"{comp_data['side_b']} - {line_b.rstrip()}")
        return comp_data

    @staticmethod
    def airways_filename_finder(file_list:list, file:str) -> list:
        """Find a filename from a list"""
        if len(file_list) > 0:
            for file_fp in file_list:
                if str(file_fp).endswith(str(file)):
                    full_path = file_fp
                    file_name = re.match(r".*([A-Z]+[0-9]+\.txt)$", str(full_path))
                    logger.debug(full_path)
                    if file_name:
                        logger.debug(file_name.group(1))
                    break
            if file_name:
                return [full_path, file_name.group(1)]
        raise ValueError("An empty list has been passed")

    @staticmethod
    def airways_comparison(
        csf_list:list,
        scraped_list:list,
        a_type:str,
        csf_list_full:list,
        scraped_list_full:list
        ) -> None:
        """Do a load of comparrisons"""

        for file in csf_list:
            comp_data:dict = {}
            comp_data["end_a"] = ""
            comp_data["end_b"] = ""
            # Get the filename from csf
            csf_file = UkSectorFile.airways_filename_finder(csf_list_full[1], file)
            comp_data["side_a"] = csf_file[0]
            comp_data["end_a"] = csf_file[1]
            # Get the filename from scrape
            scp_file = UkSectorFile.airways_filename_finder(
                scraped_list_full[1],
                str(f"{a_type}-{file}")
                )
            comp_data["side_b"] = scp_file[0]
            comp_data["end_b"] = scp_file[1]
            if (comp_data["end_a"] != comp_data["end_b"] or
                (comp_data["end_a"] == 0 and comp_data["end_b"] == 0)):
                raise ValueError(f"{comp_data['end_a']} != {comp_data['end_b']} :: {file}")
            # If the files don't match then do a bit more digging
            if not filecmp.cmp(str(comp_data["side_a"]), str(comp_data["side_b"]), shallow=False):
                logger.trace(f"{file} doesn't match")
                # Open both files side by side
                with open(comp_data["side_a"], "r", encoding="utf-8") as file_a, \
                    open(comp_data["side_b"], "r", encoding="utf-8") as file_b:
                    comp_data["check_ok"] = True
                    # Read file contents into variables
                    comp_data["lines_a"] = file_a.readlines()
                    comp_data["lines_b"] = file_b.readlines()

                    logger.debug(comp_data["end_b"])
                    comp_data.update(UkSectorFile.airways_line_by_line(comp_data))
                if comp_data["check_ok"]:
                    # If everything matches then there isn't anything to do!
                    logger.trace(f"Full line match for {file}")
                else:
                    comp_data["rev_check"] = False
                    # Put each side into an array
                    comp_data["splt_a"] = UkSectorFile.quick_split(comp_data["lines_a"])
                    comp_data["splt_b"] = UkSectorFile.quick_split(comp_data["lines_b"])
                    # Reverse the second list
                    comp_data["splt_b"].reverse()
                    comp_data["breaker"] = False
                    for item_a, item_b in zip(comp_data["splt_a"], comp_data["splt_b"]):
                        if item_a != item_b:
                            logger.warning(f"No match - {item_a} {item_b}")
                            comp_data["breaker"] = True
                            break
                    if not comp_data["breaker"]:
                        logger.info(f"{a_type} {file} is back-to-front")
                        comp_data["rev_check"] = True

                    if not comp_data["rev_check"]:
                        # If anything doesn't line up then print both files side by side
                        logger.warning(f"No match for contents of {a_type} {file}")

                        print(f"{a_type}  |  {comp_data['side_a']}  |  {comp_data['side_b']}")
                        for line_a, line_b in zip(comp_data["lines_a"], comp_data["lines_b"]):
                            print(f"{line_a.rstrip()}  |  {line_b.rstrip()}")

        for file in scraped_list:
            # If there is no matching file, then it isn't there
            comp_data["copy_file"] = os.path.join(
                functions.work_dir, "DataFrames", f"ENR-3.2-{a_type}-{file}")
            comp_data["copy_dest"] = os.path.join(
                functions.work_dir, "DataFrames", "Output", "Airways", a_type)
            # Filter out any files that are 0 bytes
            if int(os.path.getsize(comp_data["copy_file"])) > 0:
                logger.info(f"{a_type} {str(file).split('.', maxsplit=1)[0]} was found during "
                            "the scrape but doesn't seem to be in the current sector file")
                logger.debug(comp_data["copy_file"])
                logger.debug(comp_data["copy_dest"])
                functions.copy_files(comp_data["copy_file"], comp_data["copy_dest"])

    def airways_rnav(self):
        """Run validation on rnav airways"""

        # Put all of the current sector file (csf) airways into a list
        csf_rnav_lower = self.find_files_by_regex("(.+)", self.root_dir + "\\Airways\\RNAV\\Lower")
        csf_rnav_upper = self.find_files_by_regex("(.+)", self.root_dir + "\\Airways\\RNAV\\Upper")
        # Put all of the scraped airways into a list
        file_path = os.path.join(functions.work_dir, "DataFrames")
        scraped_rnav_lower = self.find_files_by_regex("ENR-3.2-LOWER-(.+)", file_path)
        scraped_rnav_upper = self.find_files_by_regex("ENR-3.2-UPPER-(.+)", file_path)

        logger.debug(csf_rnav_lower)
        logger.debug(scraped_rnav_lower)
        logger.debug(csf_rnav_upper)
        logger.debug(scraped_rnav_upper)

        # Produce lists of matching and non-matching file names as a starter
        list_match_csf_lower = self.list_match(csf_rnav_lower[0], scraped_rnav_lower[0])
        list_match_scraped_lower = self.list_match(scraped_rnav_lower[0], csf_rnav_lower[0])
        list_match_csf_upper = self.list_match(csf_rnav_upper[0], scraped_rnav_upper[0])
        list_match_scraped_upper = self.list_match(scraped_rnav_upper[0], csf_rnav_upper[0])

        logger.debug(list_match_csf_lower)
        logger.debug(list_match_scraped_lower)
        logger.debug(list_match_csf_upper)
        logger.debug(list_match_scraped_upper)

        # Run the actual validation
        self.airways_comparison(
            list_match_csf_lower[0],
            list_match_scraped_lower[1],
            "LOWER",
            csf_rnav_lower,
            scraped_rnav_lower
            )
        self.airways_comparison(
            list_match_csf_upper[0],
            list_match_scraped_upper[1],
            "UPPER",
            csf_rnav_upper,
            scraped_rnav_upper
            )

    @staticmethod
    def compare_enr_4(lines_a, lines_b) -> None:
        """Line by line comparator for ENR 4 data"""

        no_match = True
        for line_a, line_b in zip(lines_a, lines_b):
            logger.info("-"*60)
            if (line_a.rstrip() != line_b.rstrip()) and (line_a in lines_b):
                logger.success(f"Not in sequence - {line_a.rstrip()}")
                no_match = False
            elif (line_a.rstrip() != line_b.rstrip()) and (line_a not in lines_b):
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

            logger.info("A to B")
            self.compare_enr_4(lines_a=lines_a, lines_b=lines_b)
            logger.info("B to A")
            self.compare_enr_4(lines_a=lines_b, lines_b=lines_a)
