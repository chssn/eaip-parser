"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.9

# Standard Libraries
import filecmp
import os
from pathlib import Path

# Third Party Libraries
import pandas as pd
import pytest
from loguru import logger
from unittest.mock import MagicMock, patch

# Local Libraries
import tests.standard_test_cases as stc
from eaip_parser import functions, lists
from eaip_parser.webscrape import Webscrape, ProcessData

work_dir = os.path.dirname(__file__)
parent_dir = Path(work_dir).resolve().parents[0]
logger.debug(f"Working directory is {work_dir}")

# Create DataFrames directory if it doesn't already exist
path_to_build = os.path.join(parent_dir, "eaip_parser", "DataFrames")
if not os.path.exists(path_to_build):
    os.makedirs(path_to_build)

class TestWebscrape:
    class TestInitMethod:
        def test_country_pass(self):
            # Test the default settings
            webscrapi = Webscrape()
            assert webscrapi.country == "EG"

            test_cases = [
                "EG",
                "eG",
                "Eg",
                "eg",
            ]
            for test in test_cases:
                webscrapi = Webscrape(country_code=test)
                assert webscrapi.country == "EG"

            # Test all countries given in the list
            for country, language in lists.country_codes.items():
                webscrapi = Webscrape(country_code=country)
                assert webscrapi.language == language

        def test_country_error(self):
            # Test invalid data
            with pytest.raises(ValueError):
                Webscrape(country_code="England")
            with pytest.raises(KeyError):
                Webscrape(country_code="IR")

        def test_cycle(self):
            for input_date, expected_result in stc.test_url_current:
                webscrapi = Webscrape(next_cycle=False, date_in=input_date)
                assert webscrapi.cycle_url == expected_result

        def test_next_cycle(self):
            for input_date, expected_result in stc.test_url_next:
                webscrapi = Webscrape(date_in=input_date)
                assert webscrapi.cycle_url == expected_result

        def test_date_in_pass(self):
            dates = [
                "2000-01-01",
                "2099-12-31",
            ]
            for date in dates:
                webscapi = Webscrape(date_in=date)
                assert webscapi.date_in == date

        def test_date_in_error(self):
            bad_dates = [
                ("2010-00-00", "month must be in 1..12"),
                ("2010-13-39", "month must be in 1..12"),
                ("2010-02-30", "day is out of range for month"),
                ("A", "Invalid isoformat string: 'A'"),
                ("2010-2-8", "Invalid isoformat string: '2010-2-8'")
            ]
            for date, error in bad_dates:
                with pytest.raises(ValueError, match=error):
                    Webscrape(date_in=date)

    def test_run(self):
        obj = Webscrape()

        # Mock the parse and process methods
        with patch.object(obj, "parse_ad_2") as mock_parse_ad_2, \
                patch.object(obj, "parse_enr_2_1") as mock_parse_enr_2_1, \
                patch.object(obj, "parse_enr_2_2") as mock_parse_enr_2_2, \
                patch.object(obj, "parse_enr_3_2") as mock_parse_enr_3_2, \
                patch.object(obj, "parse_enr_3_3") as mock_parse_enr_3_3, \
                patch.object(obj, "parse_enr_4_1") as mock_parse_enr_4_1, \
                patch.object(obj, "parse_enr_4_4") as mock_parse_enr_4_4, \
                patch.object(obj, "parse_enr_5_1") as mock_parse_enr_5_1, \
                patch.object(obj, "parse_enr_5_2") as mock_parse_enr_5_2, \
                patch.object(obj, "parse_enr_5_3") as mock_parse_enr_5_3, \
                patch.object(obj.proc, "process_enr_2") as mock_process_enr_2, \
                patch.object(obj.proc, "process_enr_3") as mock_process_enr_3, \
                patch.object(obj.proc, "process_enr_4") as mock_process_enr_4, \
                patch.object(obj.proc, "process_enr_5") as mock_process_enr_5, \
                patch.object(obj.proc_a, "run") as mock_process_run:

            # Call the run method
            obj.run(download_first=True, no_build=False, clean_start=False)

        # Assert that the parse methods were called when download_first is True
        assert mock_parse_ad_2.called
        assert mock_parse_enr_2_1.called
        assert mock_parse_enr_2_2.called
        assert mock_parse_enr_3_2.called
        assert mock_parse_enr_3_3.called
        assert mock_parse_enr_4_1.called
        assert mock_parse_enr_4_4.called
        assert mock_parse_enr_5_1.called
        assert mock_parse_enr_5_2.called
        assert mock_parse_enr_5_3.called

        # Assert that the process methods were called
        assert mock_process_enr_2.called_with(no_build=False)
        assert mock_process_enr_3.called_with(no_build=False)
        assert mock_process_enr_4.called_with(no_build=False)
        assert mock_process_enr_5.called_with(no_build=False)
        assert mock_process_run.called

    class TestUrlSuffixMethod:
        test_object = Webscrape()

        def test_pass(self):
            sections = [
                "GEN-0.0",
                "GEN-0.1",
                "GEN-6.9",
                "ENR-0.0",
                "ENR-0.1",
                "ENR-6.99",
                "AD-0.0",
                "AD-0.1",
                "AD-6.9",
                "AD-2.EGPD",
                "AD-3.EGBC",
                "AD-2.AAAA",
                "AD-3.ZZZZ",
            ]
            for section in sections:
                wso = self.test_object.url_suffix(section)
                assert wso == str(f"EG-{section}-en-GB.html")

        def test_error(self):
            bad_sections = [
                "GNE-0.0",
                "EGN-0.0",
                "ENG-0.0",
                "NEG-0.0",
                "NGA-0.0",
                "ERN-0.0",
                "NER-0.0",
                "NRE-0.0",
                "REN-0.0",
                "RNE-0.0",
                "DA-0.0",
                "ADENRGEN-0.0",
                "ENR-1.100",
                "ENR-7.1",
                "wifflepiggy",
            ]
            for section in bad_sections:
                error = f"{section} is in an unexpected format!"
                with pytest.raises(ValueError, match=error):
                    self.test_object.url_suffix(section)

            with pytest.raises(TypeError):
                self.test_object.url_suffix(1234)

    class TestGetTableMethod:
        obj = Webscrape()

        def test_get_table_with_tables(self):
            # Mock the pd.read_html method to return a list of DataFrames
            mock_tables = [
                pd.DataFrame({"Column1": [1, 2], "Column2": [3, 4]}),
                pd.DataFrame({"Column3": [5, 6], "Column4": [7, 8]})
                ]
            with patch("pandas.read_html", return_value=mock_tables) as mock_read_html:
                # Call the get_table() method
                result = self.obj.get_table(section="AD-0.0", match=".+")

                # Check if pd.read_html was called with the correct arguments
                mock_read_html.assert_called_once_with(
                    self.obj.cycle_url + self.obj.url_suffix(section="AD-0.0"),
                    flavor="bs4",
                    match=".+"
                    )

                # Check if the method returned the expected result
                assert result == mock_tables

        def test_get_table_no_tables(self):
            # Mock the pd.read_html method to return an empty list
            with patch("pandas.read_html", return_value=[]) as mock_read_html:
                # Call the get_table() method and expect an exception to be raised
                with pytest.raises(functions.NoUrlDataFoundError) as exc_info:
                    self.obj.get_table(section="AD-0.0", match=".+")

                # Check if pd.read_html was called with the correct arguments
                mock_read_html.assert_called_once_with(
                    self.obj.cycle_url + self.obj.url_suffix(section="AD-0.0"),
                    flavor="bs4",
                    match=".+"
                    )

                # Check if the correct exception was raised
                error = (f"No data found at the given url - {self.obj.cycle_url}"
                        f"{self.obj.url_suffix(section='AD-0.0')}")
                assert str(exc_info.value) == error

class TestProcessData:
    def test_search_enr_2_x(self):
        """search_enr_2_x"""

        webscrapi = ProcessData()
        file_names = ["ENR-2.1_0","ENR-2.1_1", "ENR-2.2_0", "ENR-2.2_1", "ENR-2.2_2"]
        for proc in file_names:
            file_path = os.path.join(work_dir, "test_data", f"{proc}.csv")
            df_out = pd.read_csv(file_path)
            # The function being tested
            webscrapi.search_enr_2_x(df_out, proc, no_build=True)
            filecmp.clear_cache()
            file_a = os.path.join(work_dir, "test_data", f"{proc}_AIRSPACE_NB.sct")
            file_b = os.path.join(parent_dir, "eaip_parser", "DataFrames", f"{proc}_AIRSPACE.sct")
            assert filecmp.cmp(file_a, file_b, shallow=False) is True

    def test_search_enr_3_x(self):
        """search_enr_3_x"""

        webscrapi = ProcessData()
        file_names = [
            ("ENR-3.2_151.csv", "ENR-3.2-UPPER-Q63.txt"),
            ("ENR-3.2_67.csv", "ENR-3.2-LOWER-N16.txt"),
            ("ENR-3.2_88.csv", "ENR-3.2-LOWER-N90.txt"),
            ("ENR-3.2_22.csv", "ENR-3.2-LOWER-L603.txt"),
            ("ENR-3.2_5.csv", "ENR-3.2-LOWER-L15.txt"),
            ("ENR-3.2_26.csv", "ENR-3.2-UPPER-L612.txt"),
            ]
        for file_in, file_out in file_names:
            file_path = os.path.join(work_dir, "test_data", file_in)
            df_out = pd.read_csv(file_path)
            # The function being tested
            webscrapi.search_enr_3_x(df_out)
            logger.debug(f"Testing {file_out}")
            filecmp.clear_cache()
            file_a = os.path.join(work_dir, "test_data", file_out)
            file_b = os.path.join(parent_dir, "eaip_parser", "DataFrames", file_out)
            assert filecmp.cmp(file_a, file_b, shallow=False) is True

    def test_process_enr_4(self):
        """process_enr_4"""

        webscrapi = ProcessData()
        file_names = [
            ("ENR-4.1.csv", "VOR_UK.txt", "1"),
            ("ENR-4.4.csv", "FIXES_UK.txt", "4"),
        ]
        for file_in, file_out, sub_section in file_names:
            df_out_path = os.path.join(work_dir, "test_data", f"{file_in}")
            df_out = pd.read_csv(df_out_path)
            if sub_section == "1":
                output = webscrapi.search_enr_4_1(df_out, no_build=True)
            elif sub_section == "4":
                output = webscrapi.search_enr_4_4(df_out, no_build=True)

            file_path = os.path.join(functions.work_dir, "DataFrames", file_out)
            logger.debug(file_path)
            with open(file_path, "w", encoding="utf-8") as file:
                for line in output:
                    file.write(f"{line}\n")

            logger.debug(f"Testing {file_out}")
            filecmp.clear_cache()
            file_a = os.path.join(work_dir, "test_data", file_out)
            file_b = os.path.join(parent_dir, "eaip_parser", "DataFrames", file_out)
            assert filecmp.cmp(file_a, file_b, shallow=False) is True
