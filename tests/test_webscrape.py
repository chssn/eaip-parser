"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

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

def test_init_country():
    """__init__"""

    # Test the default settings
    webscrapi = Webscrape()
    assert webscrapi.country == "EG"

    # Test all lowercase
    webscrapi = Webscrape(country_code="eg")
    assert webscrapi.country == "EG"

    # Test mixed case
    webscrapi = Webscrape(country_code="eG")
    assert webscrapi.country == "EG"

    # Test all countries given in the list
    for country, language in lists.country_codes.items():
        webscrapi = Webscrape(country_code=country)
        assert webscrapi.language == language

    # Test invalid data
    with pytest.raises(ValueError):
        webscrapi = Webscrape(country_code="England")
    with pytest.raises(KeyError):
        webscrapi = Webscrape(country_code="IR")

def test_init_cycle():
    """__init__"""
    for input_date, expected_result in stc.test_url_current:
        webscrapi = Webscrape(next_cycle=False, date_in=input_date)
        assert webscrapi.cycle_url == expected_result

def test_init_next_cycle():
    """__init__"""
    for input_date, expected_result in stc.test_url_next:
        webscrapi = Webscrape(date_in=input_date)
        assert webscrapi.cycle_url == expected_result

def test_init_date_in():
    """__init__"""
    dates = [
        "2000-01-01",
        "2099-12-31",
    ]
    for date in dates:
        webscapi = Webscrape(date_in=date)
        assert webscapi.date_in == date

    bad_dates = [
        ("2010-00-00", "month must be in 1..12"),
        ("2010-13-39", "month must be in 1..12"),
        ("2010-02-30", "day is out of range for month"),
        ("A", "Invalid isoformat string: 'A'"),
        ("2010-2-8", "Invalid isoformat string: '2010-2-8'")
    ]
    for date, error in bad_dates:
        with pytest.raises(ValueError, match=error):
            webscapi = Webscrape(date_in=date)

def test_url_suffix():
    """url_suffix"""
    sections = [
        "AD-1.4",
        "wgobna3489au tafgh[WN]",
        1234
    ]
    webscrapi = Webscrape()
    for section in sections:
        wso = webscrapi.url_suffix(section)
        assert wso == str(f"EG-{section}-en-GB.html")

def test_search_enr_2_x():
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

def test_search_enr_3_x():
    """search_enr_3_x"""

    webscrapi = ProcessData()
    file_names = [
        ("ENR-3.2_151.csv", "ENR-3.2-UPPER-Q63.txt"),
        ("ENR-3.2_67.csv", "ENR-3.2-LOWER-N16.txt"),
        ("ENR-3.2_88.csv", "ENR-3.2-LOWER-N90.txt"),
        ("ENR-3.2_22.csv", "ENR-3.2-LOWER-L603.txt"),
        ("ENR-3.2_5.csv", "ENR-3.2-LOWER-L15.txt"),
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

def test_process_enr_4():
    """process_enr_4"""

    webscrapi = ProcessData()
    file_names = [
        "FIXES_UK.txt",
        "VOR_UK.txt",
        ]
    webscrapi.process_enr_4(no_build=True)
    for file_out in file_names:
        logger.debug(f"Testing {file_out}")
        filecmp.clear_cache()
        file_a = os.path.join(work_dir, "test_data", file_out)
        file_b = os.path.join(parent_dir, "eaip_parser", "DataFrames", file_out)
        assert filecmp.cmp(file_a, file_b, shallow=False) is True

def test_generate_file_names():
    # Test case 1: Test with matching filenames
    file_start = "test_file"
    expected_files = ["test_file_1.csv", "test_file_2.csv", "test_file_3.csv"]
    create_test_files(expected_files)
    result = Webscrape.generate_file_names(file_start)
    assert result == expected_files

    # Test case 2: Test with non-matching filenames
    file_start = "non_matching"
    expected_files = []
    create_test_files(["other_file_1.csv", "other_file_2.csv"])
    result = Webscrape.generate_file_names(file_start)
    assert result == expected_files

    # Test case 3: Test with a different file type
    file_start = "test_file"
    expected_files = ["test_file_1.json", "test_file_2.json"]
    create_test_files(expected_files)
    result = Webscrape.generate_file_names(file_start, file_type="json")
    assert result == expected_files

def create_test_files(files):
    # Helper function to create test files in the 'DataFrames' folder
    path = os.path.join(functions.work_dir, "DataFrames")
    os.makedirs(path, exist_ok=True)
    for filename in files:
        full_path = os.path.join(path, filename)
        open(full_path, "w").close()


class TestGetTableMethod:
    def test_get_table_with_tables(self):
        # Create an instance of YourClass
        your_class_instance = Webscrape()

        # Mock the pd.read_html method to return a list of DataFrames
        mock_tables = [pd.DataFrame({"Column1": [1, 2], "Column2": [3, 4]}), pd.DataFrame({"Column3": [5, 6], "Column4": [7, 8]})]
        with patch("pandas.read_html", return_value=mock_tables) as mock_read_html:
            # Call the get_table() method
            result = your_class_instance.get_table(section="TestSection", match=".+")

            # Check if pd.read_html was called with the correct arguments
            mock_read_html.assert_called_once_with(your_class_instance.cycle_url + your_class_instance.url_suffix(section="TestSection"), flavor="bs4", match=".+")

            # Check if the method returned the expected result
            assert result == mock_tables

    def test_get_table_no_tables(self):
        # Create an instance of YourClass
        your_class_instance = Webscrape()

        # Mock the pd.read_html method to return an empty list
        with patch("pandas.read_html", return_value=[]) as mock_read_html:
            # Call the get_table() method and expect an exception to be raised
            with pytest.raises(functions.NoUrlDataFoundError) as exc_info:
                your_class_instance.get_table(section="TestSection", match=".+")

            # Check if pd.read_html was called with the correct arguments
            mock_read_html.assert_called_once_with(your_class_instance.cycle_url + your_class_instance.url_suffix(section="TestSection"), flavor="bs4", match=".+")

            # Check if the correct exception was raised
            assert str(exc_info.value) == "No data found at the given url - " + your_class_instance.cycle_url + your_class_instance.url_suffix(section="TestSection")
