"""Tests for astro_brain.doctor.fallback: deterministic rule-based recommendation text."""

from __future__ import annotations

from astro_brain.doctor.fallback import FLAG_ADVICE, NOMINAL_TEXT, build_fallback
from conftest import FakeFlag, make_assessment

# The 18 flag codes from AGENTS.md section 3.
ALL_FLAG_CODES = (
    "HR_HIGH",
    "HR_LOW",
    "SPO2_LOW",
    "BP_LOW",
    "BP_HIGH",
    "TEMP_HIGH",
    "TEMP_LOW",
    "RESP_HIGH",
    "RESP_LOW",
    "CONSCIOUSNESS_ALTERED",
    "NEWS2_MEDIUM",
    "NEWS2_HIGH",
    "RADIATION_ELEVATED",
    "RADIATION_CRITICAL",
    "EXERCISE_DEFICIT",
    "CALORIC_DEFICIT",
    "SLEEP_DEFICIT",
    "LOW_MOOD",
)


def _yellow(code: str) -> FakeFlag:
    return FakeFlag(code=code, severity="yellow", message=f"{code} message")


def _red(code: str) -> FakeFlag:
    return FakeFlag(code=code, severity="red", message=f"{code} message")


def test_flag_advice_covers_every_contract_flag_code():
    # Assert
    for code in ALL_FLAG_CODES:
        assert code in FLAG_ADVICE
        assert isinstance(FLAG_ADVICE[code], str)
        assert FLAG_ADVICE[code]


def test_build_fallback_green_no_flags_returns_nominal_text():
    # Arrange
    assessment = make_assessment(alert_level="green", flags=())

    # Act
    result = build_fallback(assessment)

    # Assert
    assert result == NOMINAL_TEXT
    assert "nominal" in NOMINAL_TEXT.lower()


def test_build_fallback_yellow_starts_with_attention_required_and_ends_with_recheck():
    # Arrange
    assessment = make_assessment(alert_level="yellow", flags=(_yellow("SLEEP_DEFICIT"),))

    # Act
    result = build_fallback(assessment)

    # Assert
    assert result.startswith("Attention required.")
    assert result.endswith("Re-check in 15 minutes; contact ground medical if it persists.")
    assert FLAG_ADVICE["SLEEP_DEFICIT"] in result


def test_build_fallback_red_starts_with_immediate_action_and_ends_with_contact_now():
    # Arrange
    assessment = make_assessment(alert_level="red", flags=(_red("NEWS2_HIGH"),))

    # Act
    result = build_fallback(assessment)

    # Assert
    assert result.startswith("IMMEDIATE ACTION REQUIRED.")
    assert result.endswith("Contact ground medical now.")
    assert FLAG_ADVICE["NEWS2_HIGH"] in result


def test_build_fallback_orders_red_flags_before_yellow_flags():
    # Arrange
    yellow_flag = _yellow("SLEEP_DEFICIT")
    red_flag = _red("NEWS2_HIGH")
    # Yellow flag listed first in the tuple, but red must be surfaced first in the text.
    assessment = make_assessment(alert_level="red", flags=(yellow_flag, red_flag))

    # Act
    result = build_fallback(assessment)

    # Assert
    red_pos = result.index(FLAG_ADVICE["NEWS2_HIGH"])
    yellow_pos = result.index(FLAG_ADVICE["SLEEP_DEFICIT"])
    assert red_pos < yellow_pos


def test_build_fallback_caps_at_four_flags():
    # Arrange
    flags = tuple(_yellow(code) for code in ALL_FLAG_CODES[:6])
    assessment = make_assessment(alert_level="yellow", flags=flags)

    # Act
    result = build_fallback(assessment)

    # Assert
    included = [code for code in ALL_FLAG_CODES[:6] if FLAG_ADVICE[code] in result]
    assert len(included) == 4
    # The first four flags (in original order) should be the ones included.
    assert included == list(ALL_FLAG_CODES[:4])


def test_build_fallback_unknown_flag_code_never_raises():
    # Arrange
    assessment = make_assessment(alert_level="yellow", flags=(_yellow("SOME_FUTURE_FLAG"),))

    # Act
    result = build_fallback(assessment)

    # Assert: no KeyError, and some generic sentence mentioning the code is present.
    assert "SOME_FUTURE_FLAG" in result


def test_build_fallback_is_deterministic():
    # Arrange
    assessment = make_assessment(alert_level="yellow", flags=(_yellow("LOW_MOOD"),))

    # Act
    first = build_fallback(assessment)
    second = build_fallback(assessment)

    # Assert
    assert first == second
