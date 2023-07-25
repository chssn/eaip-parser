"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries
import re
from datetime import date

# Third Party Libraries
import pytest
import requests

# Local Libraries
import tests.standard_test_cases as stc
from eaip_parser.airac import Airac

airac = Airac()

def test_airac_basedate():
    """__init__"""
    assert airac.base_date == date.fromisoformat("2019-01-02")

def test_airac_cycledays():
    """__init__"""
    assert airac.cycle_days == 28

def test_initialise_known_date():
    """initialise"""
    assert airac.initialise("2019-01-02") == 0
    assert airac.initialise("2023-07-12") == 59
    assert airac.initialise("2023-07-19") == 59
    assert airac.initialise("2023-08-09") == 60
    assert airac.initialise("2023-08-10") == 60
    assert airac.initialise("2028-12-20") == 130
    assert airac.initialise("2028-12-21") == 130

def test_initialise_not_date():
    """initialise"""
    with pytest.raises(ValueError):
        airac.initialise("2021")

def test_initialise_is_int():
    """initialise"""
    result = airac.initialise()
    assert isinstance(result, int)

def test_cycle_is_regex():
    """cycle"""
    assert re.match(r"[\d]{4}\-[\d]{2}\-[\d]{2}", str(airac.cycle()))

def test_cycle_known_date():
    """cycle"""
    assert airac.cycle(date_in="2020-01-02") == date(2020, 1, 2)
    assert airac.cycle(date_in="2021-05-16") == date(2021, 4, 22)
    assert airac.cycle(date_in="2023-12-26") == date(2023, 11, 30)
    assert airac.cycle(date_in="2023-12-27") == date(2023, 12, 28)

def test_cycle_known_date_next_cycle():
    """cycle"""
    assert airac.cycle(next_cycle=True, date_in="2020-01-02") == date(2020, 1, 30)
    assert airac.cycle(next_cycle=True, date_in="2021-05-16") == date(2021, 5, 20)
    assert airac.cycle(next_cycle=True, date_in="2023-12-26") == date(2023, 12, 28)
    assert airac.cycle(next_cycle=True, date_in="2023-12-27") == date(2024, 1, 25)

def test_url_known_date():
    """url"""
    for input_date, expected_result in stc.test_url_current:
        assert airac.url(date_in=input_date) == expected_result

def test_url_known_date_next_cycle():
    """url"""
    for input_date, expected_result in stc.test_url_next:
        assert airac.url(next_cycle=True, date_in=input_date) == expected_result

def test_url_current_cycle():
    """url"""
    url_to_test = airac.url()
    rqst = requests.get(url_to_test + "EG-AD-0.1-en-GB.html", timeout=30)
    assert rqst.status_code == 200

def test_url_next_cycle():
    """url"""
    url_to_test = airac.url(next_cycle=True)
    rqst = requests.get(url_to_test + "EG-AD-0.1-en-GB.html", timeout=30)
    assert rqst.status_code == 200
