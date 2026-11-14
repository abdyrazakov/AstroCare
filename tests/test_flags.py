"""Tests for astro_brain.flags: Flag dataclass and alert-level aggregation."""

import dataclasses

import pytest

from astro_brain.flags import Flag, alert_level_from_flags


def _yellow(code: str = "SLEEP_DEFICIT") -> Flag:
    return Flag(code=code, severity="yellow", message="Sleep below 6 h", value=4.5, threshold=6)


def _red(code: str = "NEWS2_HIGH") -> Flag:
    return Flag(code=code, severity="red", message="NEWS2 total >= 7", value=8, threshold=7)


def test_flag_to_dict_exposes_all_contract_keys():
    # Arrange
    flag = _yellow()

    # Act
    result = flag.to_dict()

    # Assert
    assert result == {
        "code": "SLEEP_DEFICIT",
        "severity": "yellow",
        "message": "Sleep below 6 h",
        "value": 4.5,
        "threshold": 6,
    }


def test_flag_value_and_threshold_default_to_none():
    # Arrange / Act
    flag = Flag(code="LOW_MOOD", severity="yellow", message="Mood low")

    # Assert
    assert flag.value is None
    assert flag.threshold is None
    assert flag.to_dict()["value"] is None
    assert flag.to_dict()["threshold"] is None


def test_flag_is_immutable():
    # Arrange
    flag = _yellow()

    # Act / Assert
    with pytest.raises(dataclasses.FrozenInstanceError):
        flag.code = "OTHER"  # type: ignore[misc]


def test_flag_rejects_unknown_severity():
    # Arrange / Act / Assert
    with pytest.raises(ValueError, match="severity"):
        Flag(code="X", severity="orange", message="bad")  # type: ignore[arg-type]


def test_alert_level_is_green_when_no_flags():
    # Arrange
    flags: tuple[Flag, ...] = ()

    # Act
    level = alert_level_from_flags(flags)

    # Assert
    assert level == "green"


def test_alert_level_is_yellow_when_only_yellow_flags():
    # Arrange
    flags = (_yellow("SLEEP_DEFICIT"), _yellow("LOW_MOOD"))

    # Act
    level = alert_level_from_flags(flags)

    # Assert
    assert level == "yellow"


def test_alert_level_is_red_when_any_red_flag_present():
    # Arrange
    flags = (_yellow("SLEEP_DEFICIT"), _red("RADIATION_CRITICAL"), _yellow("LOW_MOOD"))

    # Act
    level = alert_level_from_flags(flags)

    # Assert
    assert level == "red"


def test_alert_level_is_red_when_single_red_flag():
    # Arrange
    flags = (_red(),)

    # Act
    level = alert_level_from_flags(flags)

    # Assert
    assert level == "red"
