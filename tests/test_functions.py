"""
eAIP Parser
Chris Parkinson (@chssn)
"""

#!/usr/bin/env python3.9

# Standard Libraries
import os
import subprocess

# Third Party Libraries
import git
import pytest
from unittest.mock import MagicMock, patch

# Local Libraries
import eaip_parser.functions as functions
from eaip_parser.functions import Geo, GitActions, TacanVor, NoUrlDataFoundError

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

def test_generate_file_names():
    test_data = [
        "file1.csv",
        "file2.csv",
        "flie3.csv",
        "file4.txt",
    ]
    with patch("os.listdir", return_value=test_data):
        output = functions.generate_file_names("file", "csv")
        assert output == ["file1.csv", "file2.csv"]

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
        expected_dict = {
            "lat": expected_result[0],
            "lon": expected_result[1],
        }
        pytest.approx(Geo.dms2dd(lat, lon), expected_dict)

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

def test_git_init():
    """GitActions()"""
    # Test default settings
    test_git = GitActions()
    assert test_git.repo_url == "https://github.com/VATSIM-UK/UK-Sector-File.git"
    assert test_git.branch == "main"
    assert test_git.git_folder == "UK-Sector-File"
    assert test_git.git_path == f"{functions.work_dir}\\UK-Sector-File"

    # Test modified settings
    test_git = GitActions(git_folder="TEST_A", branch="TEST_B")
    assert test_git.repo_url == "https://github.com/VATSIM-UK/UK-Sector-File.git"
    assert test_git.branch == "TEST_B"
    assert test_git.git_folder == "TEST_A"
    assert test_git.git_path == f"{functions.work_dir}\\TEST_A"

def test_git_installed(mocker):
    """is_git_installed true"""
    # Mock subprocess.check_output to simulate Git being installed
    mocker.patch("subprocess.check_output", return_value=b"git version 2.32.0")

    # Call the is_git_installed function
    result = GitActions.is_git_installed()

    assert result is True

def test_git_not_installed(mocker):
    """is_git_installed false"""
    # Mock subprocess.check_output to simulate Git being installed
    mocker.patch("subprocess.check_output", side_effect=FileNotFoundError("git"))

    # Call the is_git_installed function
    result = GitActions.is_git_installed()

    assert result is False

@pytest.mark.parametrize("exit_code, expected_result", [(0, True), (1, False)])
def test_install_git(mocker, exit_code, expected_result):
    """install_git"""
    # Mock subprocess.Popen to simulate the PowerShell command
    mocker.patch("subprocess.run")
    process_instance = subprocess.run.return_value
    process_instance.returncode = exit_code

    # Call the install_git function
    result = GitActions.install_git()

    assert result == expected_result


class TestCheckRequirements:
    """check_requirements"""
    def test_requirements_satisfied(self, monkeypatch):
        """Mock is_git_installed to return True"""
        monkeypatch.setattr(GitActions, "is_git_installed", lambda self: True)

        your_class_instance = GitActions()

        result = your_class_instance.check_requirements()

        assert result is True

    def test_requirements_not_satisfied_with_install(self, monkeypatch):
        """Mock is_git_installed to return False and install_git to return True"""
        monkeypatch.setattr(GitActions, "is_git_installed", lambda self: False)
        monkeypatch.setattr(GitActions, "install_git", lambda self: True)

        your_class_instance = GitActions()

        # Mock user input consent to "Y"
        monkeypatch.setattr("builtins.input", lambda _: "Y")

        result = your_class_instance.check_requirements()

        assert result is True

    def test_requirements_not_satisfied_without_install(self, monkeypatch):
        """Mock is_git_installed to return False and install_git to return False"""
        monkeypatch.setattr(GitActions, "is_git_installed", lambda self: False)
        monkeypatch.setattr(GitActions, "install_git", lambda self: False)

        your_class_instance = GitActions()

        # Mock user input consent to "N"
        monkeypatch.setattr("builtins.input", lambda _: "N")

        result = your_class_instance.check_requirements()

        assert result is False


class TestClone:
    """clone"""
    def test_repo_already_cloned(self, monkeypatch):
        """Mock os.path.exists to return True"""
        monkeypatch.setattr(os.path, "exists", lambda _: True)

        your_class_instance = GitActions()

        result = your_class_instance.clone()

        assert result is True

    def test_repo_not_cloned(self, monkeypatch):
        """Mock os.path.exists to return False"""
        monkeypatch.setattr(os.path, "exists", lambda _: False)

        # Mock git.Repo.clone_from to do nothing
        # (since we don't want to perform actual cloning in tests)
        monkeypatch.setattr(git.Repo, "clone_from", lambda *args, **kwargs: None)

        your_class_instance = GitActions()

        result = your_class_instance.clone()

        assert result is False


class TestPull:
    """pull"""
    def test_pull_successful(self, monkeypatch):
        """Mock os.path.exists to return True"""
        monkeypatch.setattr(os.path, "exists", lambda _: True)

        # Mock git.Repo to return a mock object with the desired active_branch
        class MockRepo:
            active_branch = "your_branch"  # Replace "your_branch" with the desired branch name
            git = git.cmd.Git()  # Mock git attribute to avoid actual git pull

        monkeypatch.setattr(git, "Repo", lambda _: MockRepo())

        your_class_instance = GitActions()

        result = your_class_instance.pull()

        assert result is False

    def test_repo_not_exists(self):
        """Mock os.path.exists to return False"""
        with pytest.raises(FileNotFoundError):
            os.path.exists = lambda _: False

            your_class_instance = GitActions()

            your_class_instance.pull()


class TestNoUrlDataFoundError:
    """NoUrlDataFound"""
    def test_exception_message(self):
        url = "https://example.com/data"
        message = "No data found at the given URL"
        error_instance = NoUrlDataFoundError(url, message)

        assert error_instance.url == url
        assert error_instance.message == message
        assert str(error_instance) == f"{message} - {url}"


class TestTacanVor:
    """TacanVor"""
    def test_tacan_to_vor_ils(self):
        test_cases = [
            ("37X", "110.00"),
            ("44X", "110.70"),
            ("44Y", "110.75"),
            ("123Y", "117.65"),
            ("126X", "117.90"),
            ("126Y", "117.95")
        ]
        test_tacan = TacanVor()
        for tacan, vor in test_cases:
            assert test_tacan.tacan_to_vor_ils(tacan) == vor
