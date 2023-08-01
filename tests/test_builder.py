"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.8

# Standard Libraries

# Third Party Libraries
import pytest
import requests
from loguru import logger

# Local Libraries
from eaip_parser.builder import KiloJuliett, BuildSettings, ArcSettings

def test_init():
    """__init__"""
    kj_test = KiloJuliett()
    assert not kj_test.request_settings
    assert kj_test.base_url == "https://kilojuliett.ch:443/webtools/geo/json"

    kj_test = KiloJuliett(base_url="402356895uy089wgja[n[arg]]")
    assert kj_test.base_url == "402356895uy089wgja[n[arg]]"

def test_settings():
    """settings"""

    # General test cases
    test_cases = [
        (False, False, False, False, False, 0, 9, 1, "xls", {
            "arctype": 0,
            "arcres": 9,
            "polynl": 1,
            "format": "xls",
        }),
        (True, True, True, True, True, 1, 90, 9, "vsys-dd", {
            "arctype": 1,
            "arcres": 90,
            "polynl": 9,
            "format": "vsys-dd",
            "elnp": "on",
            "wpt": "on",
            "dupe": "on",
            "xchglatlon": "on",
            "title": r"%3B",
        }),
        ("A", "B", "C", "D", "E", 1, 90, 9, "vsys-dd", {
            "arctype": 1,
            "arcres": 90,
            "polynl": 9,
            "format": "vsys-dd",
            "elnp": "on",
            "wpt": "on",
            "dupe": "on",
            "xchglatlon": "on",
            "title": r"%3B",
        })
    ]
    for (
        elnp,
        wpt,
        dupe,
        xchglatlon,
        title,
        arctype,
        arcres,
        polynl,
        output_format,
        expected_result
        ) in test_cases:
        kj_test = KiloJuliett()
        kj_test_settings = BuildSettings(
            elnp,
            wpt,
            dupe,
            xchglatlon,
            title,
            output_format
        )
        kj_test_arc_settings = ArcSettings(
            arctype,
            arcres,
            polynl,
        )
        kj_test.settings(build_settings=kj_test_settings, arc_settings=kj_test_arc_settings)
        logger.debug(kj_test.request_settings)
        logger.debug(expected_result)
        assert kj_test.request_settings == expected_result

    # Default settings
    default = {
        "elnp": "on",
        "wpt": "on",
        "dupe": "on",
        "arctype": 0,
        "arcres": 9,
        "polynl": 1,
        "format": "sct",
    }
    kj_test = KiloJuliett()
    kj_test.settings()
    logger.debug(kj_test.request_settings)
    logger.debug(default)
    assert kj_test.request_settings == default

    with pytest.raises(ValueError):
        kj_test.settings(arc_settings=ArcSettings(arctype=2))
    with pytest.raises(ValueError):
        kj_test.settings(arc_settings=ArcSettings(arcres=-2))
    with pytest.raises(ValueError):
        kj_test.settings(arc_settings=ArcSettings(arcres=181))
    with pytest.raises(ValueError):
        kj_test.settings(arc_settings=ArcSettings(polynl=-2))
    with pytest.raises(ValueError):
        kj_test.settings(arc_settings=ArcSettings(polynl=11))
    with pytest.raises(ValueError):
        kj_test.settings(build_settings=BuildSettings(output_format="ABC"))

def test_data_input_validator():
    """data_input_validator"""

    good_test_cases = [
        "N123.12.12.123:E456.45.45.456",
        "S123.12.12.123:W456.45.45.456",
        "123.12.12.123N:456.45.45.456E",
        "123.12.12.123S:456.45.45.456W",
        "N123.12.12:E456.45.45",
        "S123.12.12:W456.45.45",
        "123.12.12N:456.45.45E",
        "123.12.12S:456.45.45W",
        "N123.12:E456.45",
        "S123.12:W456.45",
        "123.12N:456.45E",
        "123.12S:456.45W",
        "N12°34.56' E1°23.45'",
        "S12°34.56' W1°23.45'",
        "12°34.56'N 1°23.45'E",
        "12°34.56'S 1°23.45'W",
        "123456N 1234567E",
        "123456S 1234567W",
        "N123456 E1234567",
        "S123456 W1234567",
        "N123456 E123456",
        "S123456 W123456",
        "1234N12345E",
        "1234S12345W",
        "1234N12345E",
        "12S123W",
        "N12°34'56\" , E123°34'56\"",
        "S12°34'56\" , W123°34'56\"",
        "12°34'56\"N , 123°34'56\"E",
        "12°34'56\"S , 123°34'56\"W",
        "12.12345, 12.123456",
        "12.12345, -12.123456",
        "-12.12345, 12.123456",
        "-12.12345, -12.123456",
        "N1.123, E1.123",
        "S1.123, W1.123"
    ]
    for test in good_test_cases:
        output = KiloJuliett().data_input_validator(test)
        assert output == test

    bad_test_cases = [
        "N123.12.12.123:N456.45.45.45",
        "S123.12.12.12:W456.45.45.456",
        "123.12.12.123:456.5.45.456E",
        "1.12.12.123S:456.45.45.456W",
        "M123.12.12:E456.45.45",
        "S123.12.12W456.45.45",
        "123.12.12N:46.45.45E",
        "123.12.2S:456.45.45W",
        "N123.12:E56.45",
        "S23.12:W456.45",
        "123.12N:456.45",
        "123.12:456.45W",
        "N12°34.56' E1°2345'",
        "S1234.56' W1°23.45'",
        "12°34.56'N 1°23.45'",
        "12°34.56'S 1°23.45W",
        "12346N 1234567E",
        "123456S 123467W",
        "N12356 E1234567",
        "S123456, W1234567",
        "N123456 , E123456",
        "S123456 S123456",
        "1234E12345N",
        "123412345W",
        "1234N12345",
        "12S13W",
        "N12°34'56 , E123°34'56\"",
        "S12°34'56\", W123°34'56\"",
        "12°34'56\"N, 12334'56\"E",
        "12°34'56\" , 123°34'56\"W",
        "12.12345,12.123456",
        "12.12345 -12.123456",
        "-12.1234, 12.123456",
        "-12.12345,-12.123456",
        "N1.123,E1.123",
        "S1.123,    W1.123"
        "ABS",
    ]
    for test in bad_test_cases:
        logger.debug(f"Testing {test}")
        with pytest.raises(ValueError):
            KiloJuliett().data_input_validator(test)
    
    with pytest.raises(TypeError):
        KiloJuliett().data_input_validator(123)

def test_request_output():
    """request_output"""
    good_test_cases = [
        ("A circle, 2.5 NM radius, centred at 522434N 0003340E on longest notified runway",
            """N052.27.03.899 E000.33.40.000 N052.27.02.052 E000.34.18.441
N052.27.02.052 E000.34.18.441 N052.26.56.556 E000.34.55.935
N052.26.56.556 E000.34.55.935 N052.26.47.547 E000.35.31.560
N052.26.47.547 E000.35.31.560 N052.26.35.247 E000.36.04.437
N052.26.35.247 E000.36.04.437 N052.26.19.960 E000.36.33.758
N052.26.19.960 E000.36.33.758 N052.26.02.062 E000.36.58.800
N052.26.02.062 E000.36.58.800 N052.25.41.997 E000.37.18.948
N052.25.41.997 E000.37.18.948 N052.25.20.258 E000.37.33.704
N052.25.20.258 E000.37.33.704 N052.24.57.381 E000.37.42.705
N052.24.57.381 E000.37.42.705 N052.24.33.930 E000.37.45.730
N052.24.33.930 E000.37.45.730 N052.24.10.482 E000.37.42.705
N052.24.10.482 E000.37.42.705 N052.23.47.615 E000.37.33.704
N052.23.47.615 E000.37.33.704 N052.23.25.892 E000.37.18.948
N052.23.25.892 E000.37.18.948 N052.23.05.846 E000.36.58.800
N052.23.05.846 E000.36.58.800 N052.22.47.970 E000.36.33.758
N052.22.47.970 E000.36.33.758 N052.22.32.705 E000.36.04.437
N052.22.32.705 E000.36.04.437 N052.22.20.425 E000.35.31.560
N052.22.20.425 E000.35.31.560 N052.22.11.431 E000.34.55.935
N052.22.11.431 E000.34.55.935 N052.22.05.945 E000.34.18.441
N052.22.05.945 E000.34.18.441 N052.22.04.101 E000.33.40.000
N052.22.04.101 E000.33.40.000 N052.22.05.945 E000.33.01.560
N052.22.05.945 E000.33.01.560 N052.22.11.431 E000.32.24.066
N052.22.11.431 E000.32.24.066 N052.22.20.425 E000.31.48.441
N052.22.20.425 E000.31.48.441 N052.22.32.705 E000.31.15.564
N052.22.32.705 E000.31.15.564 N052.22.47.970 E000.30.46.243
N052.22.47.970 E000.30.46.243 N052.23.05.846 E000.30.21.200
N052.23.05.846 E000.30.21.200 N052.23.25.892 E000.30.01.053
N052.23.25.892 E000.30.01.053 N052.23.47.615 E000.29.46.297
N052.23.47.615 E000.29.46.297 N052.24.10.482 E000.29.37.296
N052.24.10.482 E000.29.37.296 N052.24.33.930 E000.29.34.270
N052.24.33.930 E000.29.34.270 N052.24.57.381 E000.29.37.296
N052.24.57.381 E000.29.37.296 N052.25.20.258 E000.29.46.297
N052.25.20.258 E000.29.46.297 N052.25.41.997 E000.30.01.053
N052.25.41.997 E000.30.01.053 N052.26.02.062 E000.30.21.200
N052.26.02.062 E000.30.21.200 N052.26.19.960 E000.30.46.243
N052.26.19.960 E000.30.46.243 N052.26.35.247 E000.31.15.564
N052.26.35.247 E000.31.15.564 N052.26.47.547 E000.31.48.441
N052.26.47.547 E000.31.48.441 N052.26.56.556 E000.32.24.066
N052.26.56.556 E000.32.24.066 N052.27.02.052 E000.33.01.560"""),
    ]
    kj_test = KiloJuliett()
    kj_test.settings()
    for test, expected in good_test_cases:
        output = kj_test.request_output(test)
        assert output == expected

    with pytest.raises(requests.ConnectionError):
        kj_test.base_url = "https://thisdoesntwork.obviously"
        kj_test.request_output("any string will do")

    with pytest.raises(requests.HTTPError):
        kj_test.base_url = "https://www.aurora.nats.co.uk/non_existant_page.html"
        kj_test.request_output("any string will do")
