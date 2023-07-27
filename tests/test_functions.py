"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries

# Third Party Libraries
import pytest

# Local Libraries
import eaip_parser.functions as functions
from eaip_parser.functions import Geo

def test_is_25khz():
    """is_25khz"""
    test_cases = [
        ("121.800", False),
        ("121.875", False),
        ("121.805", "121.800"),
        ("121.870", "121.875"),
        ("121.070", "121.075"),
        ("121.995", "122.000"),
    ]
    for freq, outcome in test_cases:
        assert functions.is_25khz(freq) == outcome

    with pytest.raises(TypeError):
        functions.is_25khz(121.875)
    with pytest.raises(ValueError):
        functions.is_25khz("121.87")
    with pytest.raises(ValueError):
        functions.is_25khz("12.875")
    with pytest.raises(ValueError):
        functions.is_25khz("1211.875")
    with pytest.raises(ValueError):
        functions.is_25khz("121.8755")

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

def test_split():
    """split"""
    assert functions.split("hI8829!!") == ["h", "I", "8", "8", "2", "9", "!", "!"]
    with pytest.raises(ValueError):
        functions.split(8829)

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

def test_dd2dms():
    """dd2dms"""
    test_cases = [
        (51.77592, 1.86495, "N051.46.33.31 E001.51.53.82"),
        (-51.77592, -1.86495, "S051.46.33.31 W001.51.53.82"),
        (500.498, 865.6498, "N500.29.52.8 E865.38.59.28"),
        (-500.498, -865.6498, "S500.29.52.8 W865.38.59.28"),
    ]
    for lat, lon, expected_result in test_cases:
        assert Geo.dd2dms(lat, lon) == expected_result

    with pytest.raises(ValueError):
        Geo.dd2dms(1.7, 2)
    with pytest.raises(ValueError):
        Geo.dd2dms(-1, 2.7)
    with pytest.raises(ValueError):
        Geo.dd2dms(1, 2)
    with pytest.raises(ValueError):
        Geo.dd2dms("A", 2)
    with pytest.raises(ValueError):
        Geo.dd2dms(1.7, "B")
    with pytest.raises(ValueError):
        Geo.dd2dms("A", "B")

def test_dms2dd():
    """dms2dd"""
    test_cases = [
        ("N051.46.33.31", "E001.51.53.82", [51.77592, 1.86495]),
        ("S051.46.33.31", "W001.51.53.82", [-51.77592, -1.86495]),
        ("N500.29.52.8", "E865.38.59.28", [500.498, 865.6498]),
        ("S500.29.52.8", "W865.38.59.28", [-500.498, -865.6498]),
        ("051.46.33.31N", "001.51.53.82E", [51.77592, 1.86495]),
        ("051.46.33.31S", "001.51.53.82W", [-51.77592, -1.86495]),
        ("500.29.52.8N", "865.38.59.28E", [500.498, 865.6498]),
        ("500.29.52.8S", "865.38.59.28W", [-500.498, -865.6498]),
        ("N051.46.33", "E001.51.53", [51.77592, 1.86495]),
        ("S051.46.33", "W001.51.53", [-51.77592, -1.86495]),
        ("N500.29.52", "E865.38.59", [500.498, 865.6498]),
        ("S500.29.52", "W865.38.59", [-500.498, -865.6498]),
        ("051.46.33.31N", "001.51.53E", [51.77592, 1.86495]),
        ("051.46.33S", "001.51.53W", [-51.77592, -1.86495]),
        ("500.29.52N", "865.38.59E", [500.498, 865.6498]),
        ("500.29.52S", "865.38.59W", [-500.498, -865.6498]),
        ("514633S", "0015153W", [-51.77592, -1.86495]),
        ("514633N", "0015153E", [51.77592, 1.86495]),
    ]
    for lat, lon, expected_result in test_cases:
        pytest.approx(Geo.dms2dd(lat, lon), expected_result)

    with pytest.raises(ValueError):
        Geo.dms2dd("051.46.33.31", "001.51.53.82")
    with pytest.raises(ValueError):
        Geo.dms2dd("051.46.N33.31", "001.51.53.82")
    with pytest.raises(ValueError):
        Geo.dms2dd("051.46.33.31N", "001.51.53.82")
    with pytest.raises(ValueError):
        Geo.dms2dd("N051.46.", "E001.51.53.82")
    with pytest.raises(ValueError):
        Geo.dms2dd("N051.46.33.31", "E001")
    with pytest.raises(TypeError):
        Geo.dms2dd(1.7, "B")
    with pytest.raises(TypeError):
        Geo.dms2dd("A", 1.7)
    with pytest.raises(ValueError):
        Geo.dms2dd("A", "B")
