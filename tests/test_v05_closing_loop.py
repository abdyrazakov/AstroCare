from __future__ import annotations

import pytest

from astro_brain.contract import ContractError, parse_sample
from astro_brain.dashboard import StateStore
from astro_brain.mission_log import MissionLog
from astro_brain.mock import apply_anomaly, nominal_raw
from astro_brain.pipeline import Brain


def _brain() -> Brain:
    from astro_brain.doctor.layer import DoctorLayer
    return Brain(DoctorLayer(object(), enabled=False))


@pytest.mark.parametrize("score", [3, 4, 5, 6])
def test_phq2_positive(score: int) -> None:
    raw = nominal_raw("2026-11-14T10:00:00Z")
    raw["phq2_score"] = score
    output = _brain().process(raw)
    assert "PHQ2_POSITIVE" in output["activeFlags"]
    assert "brain" in output["bodySystems"]


@pytest.mark.parametrize("score", [0, 1, 2])
def test_phq2_negative(score: int) -> None:
    raw = nominal_raw("2026-11-14T10:00:00Z")
    raw["phq2_score"] = score
    assert "PHQ2_POSITIVE" not in _brain().process(raw)["activeFlags"]


@pytest.mark.parametrize("value", [-1, 7, True, 2.5])
def test_phq2_contract_rejects_invalid(value: object) -> None:
    raw = nominal_raw("2026-11-14T10:00:00Z")
    raw["phq2_score"] = value
    with pytest.raises(ContractError):
        parse_sample(raw)


def test_plans_nominal() -> None:
    output = _brain().process(nominal_raw("2026-11-14T10:00:00Z"))
    assert output["plans"]["exercise"]["status"] == "normal"
    assert output["plans"]["nutrition"]["status"] == "normal"


@pytest.mark.parametrize("name,status", [("sepsis_like", "cancelled"), ("sleep_deprivation", "reduced"), ("exercise_deficit", "normal"), ("caloric_deficit", "reduced")])
def test_plans_follow_flags(name: str, status: str) -> None:
    output = _brain().process(apply_anomaly(nominal_raw("2026-11-14T10:00:00Z"), name))
    assert output["plans"]["exercise"]["status"] == status


def test_plans_include_makeup_session() -> None:
    output = _brain().process(apply_anomaly(nominal_raw("2026-11-14T10:00:00Z"), "exercise_deficit"))
    assert any(item["note"].startswith("Make-up") for item in output["plans"]["exercise"]["sessions"])


def _output(timestamp: str, level: str, flags: list[str], conditions: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {"timestamp": timestamp, "astronautId": "A1", "alertLevel": level, "activeFlags": flags, "likelyConditions": conditions or []}


def test_mission_log_coalesces_same_signature() -> None:
    log = MissionLog()
    log.record(_output("2026-11-14T00:00:00Z", "green", []))
    log.record(_output("2026-11-14T00:00:10Z", "green", []))
    assert len(log.episodes("A1")) == 1


def test_mission_log_splits_on_change_and_closes() -> None:
    log = MissionLog()
    log.record(_output("2026-11-14T00:00:00Z", "green", []))
    log.record(_output("2026-11-14T00:00:10Z", "yellow", ["HR_HIGH"]))
    episodes = log.episodes("A1")
    assert len(episodes) == 2
    assert episodes[0]["end"] == "2026-11-14T00:00:10Z"


def test_mission_report_time_and_conditions() -> None:
    log = MissionLog()
    log.record(_output("2026-11-14T00:00:00Z", "yellow", ["HR_HIGH"], [{"code": "SANS", "confidence": 0.6}]))
    log.record(_output("2026-11-14T00:00:20Z", "green", []))
    report = log.report("A1")
    assert report["timeByLevel"]["yellow"] == 20.0
    assert report["conditionsSeen"][0]["code"] == "SANS"


def test_mission_report_text_is_sbar() -> None:
    log = MissionLog()
    log.record(_output("2026-11-14T00:00:00Z", "green", []))
    assert log.report_text("A1").startswith("SBAR")


def test_state_store_records_mission_log() -> None:
    store = StateStore()
    store.update(_output("2026-11-14T00:00:00Z", "green", []), {})
    assert store.mission_log.episodes("A1")


@pytest.mark.parametrize("path", ["A1", "A2", "UNKNOWN", "ASTRO-01"])
def test_missing_mission_report_is_none(path: str) -> None:
    assert MissionLog().report(path) is None


@pytest.mark.parametrize("target", [None, 90, 120, 150])
def test_plan_target_is_additive(target: int | None) -> None:
    raw = nominal_raw("2026-11-14T00:00:00Z")
    if target is not None:
        raw["required_exercise_minutes"] = target
    output = _brain().process(raw)
    assert output["plans"]["exercise"]["targetMinutes"] == target or target is None and output["plans"]["exercise"]["targetMinutes"] == 150


@pytest.mark.parametrize("astronaut", ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"])
def test_mission_log_separates_astronauts(astronaut: str) -> None:
    log = MissionLog()
    sample = _output("2026-11-14T00:00:00Z", "green", [])
    sample["astronautId"] = astronaut
    log.record(sample)
    assert len(log.episodes(astronaut)) == 1
