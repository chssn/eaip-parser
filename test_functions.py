"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries

# Third Party Libraries
import pytest

# Local Libraries
from eaip_parser.functions import Geo

def test_north_south():
    """north_south"""
    assert Geo.north_south("+") == "N"
    assert Geo.north_south("-") == "S"
    with pytest.raises(ValueError):
        Geo.north_south("A")

def test_east_west():
    """east_west"""
    assert Geo.east_west("+") == "E"
    assert Geo.east_west("-") == "W"
    with pytest.raises(ValueError):
        Geo.east_west("A")

def test_plus_minus():
    """plus_minus"""
    assert Geo.plus_minus("N") == "+"
    assert Geo.plus_minus("E") == "+"
    assert Geo.plus_minus("S") == "-"
    assert Geo.plus_minus("W") == "-"
    with pytest.raises(ValueError):
        Geo.plus_minus("A")
    with pytest.raises(ValueError):
        Geo.plus_minus("--")

def test_back_bearing():
    """back_bearing"""
    test_cases = [
        (270, 90),
        (270.00, 90),
        (270.43, 90.43),
        (270.42971633, 90.43),
        (90, 270),
        (90.00, 270),
        (90.43, 270.43),
        (90.42971633, 270.43),
        (0, 180),
        (360, 180),
        (180, 0),
    ]
    for input_bearing, expected_result in test_cases:
        assert Geo.back_bearing(input_bearing) == expected_result

    with pytest.raises(ValueError):
        Geo.back_bearing(360.1)
    with pytest.raises(ValueError):
        Geo.back_bearing(-4)
    with pytest.raises(ValueError):
        Geo.back_bearing("A")
