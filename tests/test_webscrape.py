"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
from datetime import date
from unittest.mock import patch, Mock

# Third Party Libraries
import pandas as pd
import pytest
import requests
from bs4 import BeautifulSoup

# Local Libraries
import tests.standard_test_cases as stc
from eaip_parser.webscrape import Webscrape

def test_init_country():
    """__init__"""

    # Test the default settings
    webscrapi = Webscrape()
    assert webscrapi.country == "EG"

    # Test all lowercase
    webscrapi = Webscrape(country_code="ir")
    assert webscrapi.country == "IR"

    # Test mixed case
    webscrapi = Webscrape(country_code="zP")
    assert webscrapi.country == "ZP"

    # Test invalid data
    with pytest.raises(ValueError):
        webscrapi = Webscrape(country_code="England")

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

webscrape = Webscrape(date_in="2021-05-16")

@pytest.fixture
def webscrape_object():
    """Define a fixture to create an instance of YourClassName for testing"""
    return Webscrape()

@pytest.fixture
def mock_requests_get():
    """Define a fixture to mock the requests.get function"""
    with patch("requests.get") as mock_get:
        yield mock_get

def test_get_table_soup_success(webscrape_object, mock_requests_get):
    """Mock the requests.get function to return a successful response"""
    post_url = "example_post_url"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html><body><table></table></body></html>"
    mock_requests_get.return_value = mock_response

    # Call the function under test
    soup = webscrape_object.get_table_soup(post_url)

    # Assert the expected behavior
    assert isinstance(soup, BeautifulSoup)

def test_get_table_soup_connection_error(webscrape_object, mock_requests_get):
    """Mock the requests.get function to raise a ConnectTimeout"""
    post_url = "example_post_url"
    mock_requests_get.side_effect = requests.ConnectTimeout("Connection Timeout")

    with pytest.raises(requests.ConnectTimeout):
        # Call the function under test
        webscrape_object.get_table_soup(post_url)

def test_get_table_soup_error_status_code(webscrape_object, mock_requests_get):
    """Mock the requests.get function to return an error response"""
    post_url = "example_post_url"
    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    # Call the function under test
    soup = webscrape_object.get_table_soup(post_url)

    # Assert the expected behavior
    assert soup is False

def test_parse_ad_01_data(webscrape_object):
    """Test cases for parse_ad_01_data function"""

    # Mock the get_table_soup method to return a BeautifulSoup object
    with open("tests/test_ad_01_data.html", "r", encoding="utf-8") as mock_data:
        mock_soup = BeautifulSoup(mock_data, "lxml")
    webscrape_object.get_table_soup = lambda _: mock_soup

    # Call the function under test
    result_df = webscrape_object.parse_ad_01_data()

    # Define the expected DataFrame
    expected_df = pd.read_csv("tests/test_ad_01_data.csv", index_col=0)

    # Assert the DataFrame content and structure
    pd.testing.assert_frame_equal(result_df, expected_df, check_dtype=False)

def test_parse_ad_02_data(webscrape_object):
    """Test cases for parse_ad_02_data function"""

    # Mock the get_table_soup method to return a BeautifulSoup object
    with open("tests/test_ad_02_data.html", "r", encoding="utf-8") as mock_data:
        mock_soup = BeautifulSoup(mock_data, "lxml")
    webscrape_object.get_table_soup = lambda _: mock_soup

    # Call the function under test
    test_iterator = pd.read_csv("tests/test_ad_02_ad_01_data.csv", index_col=0)
    results = webscrape_object.parse_ad_02_data(df_ad_01=test_iterator)

    # Define the expected DataFrame
    expected_df_0 = pd.read_csv("tests/test_ad_02_data_0.csv", index_col=0)
    expected_df_1 = pd.read_csv("tests/test_ad_02_data_1.csv", index_col=0, dtype={'runway': object})
    expected_df_2 = pd.read_csv("tests/test_ad_02_data_2.csv", index_col=0, dtype={'frequency': object})

    # Assert the DataFrame content and structure
    pd.testing.assert_frame_equal(results[0], expected_df_0)
    pd.testing.assert_frame_equal(results[1], expected_df_1, check_dtype=False)
    pd.testing.assert_frame_equal(results[2], expected_df_2)

def test_parse_enr016_data(webscrape_object):
    """Test cases for parse_enr_016_data function"""

    # Mock the get_table_soup method to return a BeautifulSoup object
    with open("tests/test_enr_016_data.html", "r", encoding="utf-8") as mock_data:
        mock_soup = BeautifulSoup(mock_data, "lxml")
    webscrape_object.get_table_soup = lambda _: mock_soup

    # Call the function under test
    test_iterator = pd.read_csv("tests/test_ad_01_data.csv", index_col=0)
    result_df = webscrape_object.parse_enr_016_data(df_ad_01=test_iterator)

    # Define the expected DataFrame
    expected_df = pd.read_csv("tests/test_enr_016_data.csv", index_col=0, dtype={'start': object, 'end': object})

    # Assert the DataFrame content and structure
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_parse_enr02_data():
    pass

def test_parse_enr03_data(webscrape_object):
    """Test cases for parse_enr_03_data function"""

    sections = [1, 3]
    for section in sections:
        # Mock the get_table_soup method to return a BeautifulSoup object
        with open(f"tests/test_enr_03{section}_data.html", "r", encoding="utf-8") as mock_data:
            mock_soup = BeautifulSoup(mock_data, "lxml")
        webscrape_object.get_table_soup = lambda _: mock_soup

        # Call the function under test
        result_df = webscrape_object.parse_enr_03_data(section=section)

        # Define the expected DataFrame
        expected_df = pd.read_csv(f"tests/test_enr_03{section}_data.csv", index_col=0)
        expected_points_df = pd.read_csv(f"tests/test_enr_03{section}_points.csv", index_col=0)

        # Assert the DataFrame content and structure
        pd.testing.assert_frame_equal(result_df[0], expected_df)
        pd.testing.assert_frame_equal(result_df[1], expected_points_df)

    with pytest.raises(ValueError):
        webscrape.parse_enr_03_data(7)

    with pytest.raises(ValueError):
        webscrape.parse_enr_03_data("7")

def test_search():
    """search"""
    test_cases = [
        ("eaghyadfhdfah", "TDME;GEO_LAT", "eaghyadfhdfah</span>diupoahta89uya9jh43>TDME;GEO_LATuyigpgpiu", "eaghyadfhdfah"),
    ]
    for find, name, string, expected_result in test_cases:
        output = Webscrape.search(find, name, string)
        assert output[0] == expected_result
