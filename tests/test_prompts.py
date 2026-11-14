"""Tests for astro_brain.doctor.prompts: SYSTEM_PROMPT and build_user_prompt."""

from __future__ import annotations

import json

from astro_brain.doctor.prompts import SYSTEM_PROMPT, build_user_prompt
from conftest import FakeFlag, make_assessment


def test_system_prompt_mentions_key_constraints():
    # Assert
    assert "flight-surgeon" in SYSTEM_PROMPT.lower()
    assert "markdown" in SYSTEM_PROMPT.lower()
    assert "ground medical" in SYSTEM_PROMPT.lower()
    assert "diagnos" in SYSTEM_PROMPT.lower()


def test_build_user_prompt_is_valid_compact_json_with_expected_keys():
    # Arrange
    flag = FakeFlag(
        code="RADIATION_ELEVATED",
        severity="yellow",
        message="Radiation dose rate 140.0 µSv/h is above the 100 µSv/h threshold.",
        value=140.0,
        threshold=100,
    )
    assessment = make_assessment(alert_level="yellow", news2_total=2, flags=(flag,))

    # Act
    prompt = build_user_prompt(assessment)
    parsed = json.loads(prompt.split("\n", 1)[1])

    # Assert
    assert parsed["alertLevel"] == "yellow"
    assert parsed["news2Score"] == 2
    assert parsed["flags"] == [
        {
            "code": "RADIATION_ELEVATED",
            "severity": "yellow",
            "message": "Radiation dose rate 140.0 µSv/h is above the 100 µSv/h threshold.",
            "value": 140.0,
            "threshold": 100,
        }
    ]
    assert parsed["likelyConditions"] == []


def test_build_user_prompt_includes_likely_conditions():
    from conftest import FakeCondition

    condition = FakeCondition(
        code="SLEEP_DISORDER",
        label="Sleep disorder",
        confidence=0.88,
        drivers=("SLEEP_DEFICIT",),
    )
    assessment = make_assessment(likely_conditions=(condition,))

    parsed = json.loads(build_user_prompt(assessment).split("\n", 1)[1])

    assert parsed["likelyConditions"] == [condition.to_dict()]


def test_build_user_prompt_with_no_flags_is_empty_list():
    # Arrange
    assessment = make_assessment(alert_level="green", news2_total=0, flags=())

    # Act
    parsed = json.loads(build_user_prompt(assessment).split("\n", 1)[1])

    # Assert
    assert parsed["flags"] == []


def test_prompt_requires_every_flag_and_three_to_four_sentences():
    flags = (FakeFlag("LOW_MOOD", "yellow", "m"),
             FakeFlag("SLEEP_DEFICIT", "yellow", "m"))
    prompt = build_user_prompt(make_assessment(alert_level="yellow", flags=flags))
    assert prompt.splitlines()[0] == "Flags to address (all of them): LOW_MOOD, SLEEP_DEFICIT"
    assert "exactly 3 to 4 sentences" in SYSTEM_PROMPT
    assert "one concrete action for every active flag" in SYSTEM_PROMPT
    assert "final sentence" in SYSTEM_PROMPT
    assert "Never repeat input numbers" in SYSTEM_PROMPT


def test_single_flag_still_requires_three_sentences():
    assert "Even with only one flag, write at least three sentences" in SYSTEM_PROMPT
    assert "second sentence" in SYSTEM_PROMPT
