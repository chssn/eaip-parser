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
from eaip_parser import lists
from eaip_parser.webscrape import Webscrape

@pytest.fixture
def webscrape_object(**kwargs):
    """Define a fixture to create an instance of YourClassName for testing"""
    return Webscrape(**kwargs)

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
        "2010-00-00",
        "2010-13-39",
        "2010-02-30",
        "A",
        "2010-2-8"
    ]
    for date in bad_dates:
        with pytest.raises(ValueError):
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
