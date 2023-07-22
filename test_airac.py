import datetime
import pytest
import re
from eaip_parser.airac import Airac

airac = Airac()

def test_airac_basedate():
    assert airac.base_date == datetime.date.fromisoformat("2019-01-02")

def test_airac_cycledays():
    assert airac.cycle_days == 28

def test_initialise_known_date():
    result = airac.initialise("2023-06-01")
    assert result == 57

def test_initialise_not_date():
    with pytest.raises(ValueError):
        airac.initialise("2021")

def test_initialise_is_int():
    result = airac.initialise()
    assert isinstance(result, int)
