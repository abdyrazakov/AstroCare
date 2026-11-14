"""Tests for astro_brain.mock: nominal/anomaly raw samples and scenario generation."""

from __future__ import annotations

import pytest

from astro_brain.contract import parse_sample
from astro_brain.mock import ANOMALIES, apply_anomaly, nominal_raw, scenario, stream
from astro_brain.scoring import assess

TIMESTAMP = "2026-11-14T10:00:00Z"


def test_nominal_raw_passes_parse_sample():
    raw = nominal_raw(TIMESTAMP)
    sample = parse_sample(raw)
    assert sample.timestamp == TIMESTAMP
    assert sample.astronaut_id == "ASTRO-01"


def test_nominal_raw_assesses_green_with_no_flags():
    sample = parse_sample(nominal_raw(TIMESTAMP))
    result = assess(sample)
    assert result.alert_level == "green"
    assert result.flags == ()


def test_nominal_raw_custom_astronaut_id():
    raw = nominal_raw(TIMESTAMP, astronaut_id="ASTRO-09")
    assert raw["astronaut_id"] == "ASTRO-09"


@pytest.mark.parametrize("name", sorted(ANOMALIES))
def test_every_anomaly_raw_passes_parse_sample(name):
    raw = apply_anomaly(nominal_raw(TIMESTAMP), name)
    parse_sample(raw)  # must not raise


@pytest.mark.parametrize("name", sorted(ANOMALIES))
def test_every_anomaly_matches_its_expected_outcome_under_assess(name):
    anomaly = ANOMALIES[name]
    raw = apply_anomaly(nominal_raw(TIMESTAMP), name)
    result = assess(parse_sample(raw))

    assert result.alert_level == anomaly.expected_level, (
        f"{name}: expected alert_level {anomaly.expected_level!r}, got {result.alert_level!r} "
        f"(codes={result.flag_codes()})"
    )
    codes = set(result.flag_codes())
    missing = anomaly.expected_codes - codes
    assert not missing, f"{name}: expected codes {sorted(missing)} missing from {sorted(codes)}"
    missing_conditions = anomaly.expected_conditions - set(result.condition_codes())
    assert not missing_conditions, (
        f"{name}: expected conditions {sorted(missing_conditions)} missing from "
        f"{sorted(result.condition_codes())}"
    )


def test_apply_anomaly_does_not_mutate_input():
    raw = nominal_raw(TIMESTAMP)
    original = dict(raw)
    original_bp = dict(raw["bp"])

    apply_anomaly(raw, "hypotension")

    assert raw == original
    assert raw["bp"] == original_bp


def test_apply_anomaly_merges_nested_bp_without_dropping_fields():
    raw = nominal_raw(TIMESTAMP)
    updated = apply_anomaly(raw, "hypotension")
    assert updated["bp"] == {"systolic": 88, "diastolic": 55}
    # unrelated nominal fields untouched
    assert updated["hr"] == raw["hr"]


def test_apply_anomaly_unknown_name_raises_key_error_naming_it():
    with pytest.raises(KeyError, match="bogus-anomaly"):
        apply_anomaly(nominal_raw(TIMESTAMP), "bogus-anomaly")


def test_scenario_is_deterministic_for_same_seed():
    first = scenario(seed=7)
    second = scenario(seed=7)
    assert first == second


def test_scenario_different_seeds_can_differ():
    first = scenario(seed=1)
    second = scenario(seed=2)
    assert first != second


def test_scenario_anomaly_count_within_three_to_five():
    steps = scenario(seed=42)
    anomaly_steps = [step for step in steps if step.anomaly_name is not None]
    assert 3 <= len(anomaly_steps) <= 5


def test_scenario_length_and_index_order():
    steps = scenario(seed=42, length=10)
    assert len(steps) == 10
    assert [step.index for step in steps] == list(range(10))


def test_scenario_timestamps_spaced_sixty_seconds():
    steps = scenario(seed=42, length=3)
    timestamps = [step.raw["timestamp"] for step in steps]
    assert timestamps == [
        "2026-11-14T10:00:00Z",
        "2026-11-14T10:01:00Z",
        "2026-11-14T10:02:00Z",
    ]


def test_scenario_nominal_steps_parse_and_are_green():
    steps = scenario(seed=42, length=10)
    for step in steps:
        if step.anomaly_name is None:
            result = assess(parse_sample(step.raw))
            assert result.alert_level == "green"


def test_stream_cycles_scenario_without_sleeping():
    import itertools

    scenario_raws = [step.raw for step in scenario(seed=42)]
    raws = list(itertools.islice(stream(seed=42, period_s=0), 2 * len(scenario_raws)))
    assert raws[: len(scenario_raws)] == scenario_raws
    assert raws[len(scenario_raws) : 2 * len(scenario_raws)] == scenario_raws


def test_crew_stream_interleaves_independent_seeded_scenarios():
    from itertools import islice

    ids = ("ASTRO-01", "ASTRO-02", "ASTRO-03")
    raws = list(islice(stream(seed=42, period_s=0, astronaut_ids=ids), 72))
    assert [raw["astronaut_id"] for raw in raws] == list(ids) * 24
    for offset, astronaut_id in enumerate(ids):
        expected = [{**step.raw, "astronaut_id": astronaut_id}
                    for step in scenario(seed=42 + offset)]
        assert raws[offset::3] == expected
    signatures = [[{k: v for k, v in raw.items() if k != "astronaut_id"}
                   for raw in raws[offset::3]] for offset in range(3)]
    assert signatures[0] != signatures[1] != signatures[2]


@pytest.mark.parametrize("ids", [(), ("",), ("A", "A")])
def test_crew_stream_rejects_empty_or_duplicate_ids(ids):
    with pytest.raises(ValueError, match="astronaut_ids"):
        next(stream(period_s=0, astronaut_ids=ids))
