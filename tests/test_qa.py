"""Tests for astro_brain.qa: the offline end-to-end scenario QA runner."""

from __future__ import annotations

import dataclasses

from astro_brain.doctor.layer import DoctorLayer
from astro_brain.doctor.ollama_client import OllamaClient
from astro_brain.mock import Step, nominal_raw, scenario
from astro_brain.pipeline import Brain
from astro_brain.qa import CONTRACT_OUTPUT_KEYS, evaluate, main, run_scenario

TIMESTAMP = "2026-11-14T10:00:00Z"


def _offline_brain() -> Brain:
    return Brain(doctor=DoctorLayer(OllamaClient(), enabled=False))


def test_full_offline_scenario_run_passes_100_percent():
    brain = _offline_brain()
    steps = scenario(seed=42)
    results = run_scenario(brain, steps)
    failed = [result for result in results if not result.passed]
    assert not failed, f"failures: {failed}"
    assert len(results) == len(steps)


def test_run_scenario_returns_one_result_per_step():
    brain = _offline_brain()
    steps = scenario(seed=1, length=6)
    results = run_scenario(brain, steps)
    assert [result.index for result in results] == [step.index for step in steps]


def test_evaluate_passes_for_correct_nominal_output():
    brain = _offline_brain()
    step = Step(index=0, raw=nominal_raw(TIMESTAMP), anomaly_name=None)
    output = brain.process(step.raw)
    result = evaluate(step, output)
    assert result.passed
    assert result.got_level == "green"
    assert result.expected_level == "green"


def test_evaluate_fails_for_a_deliberately_wrong_expectation():
    brain = _offline_brain()
    step = Step(index=0, raw=nominal_raw(TIMESTAMP), anomaly_name=None)
    output = brain.process(step.raw)
    # Deliberately wrong expectation: a nominal sample is green, not red.
    wrong_step = dataclasses.replace(step, anomaly_name="radiation_storm")
    result = evaluate(wrong_step, output)
    assert not result.passed
    assert result.failures


def test_evaluate_flags_missing_contract_key():
    brain = _offline_brain()
    step = Step(index=0, raw=nominal_raw(TIMESTAMP), anomaly_name=None)
    output = brain.process(step.raw)
    broken_output = dict(output)
    del broken_output["doctorSource"]
    result = evaluate(step, broken_output)
    assert not result.passed
    assert any("contract keys" in failure for failure in result.failures)
    assert set(output.keys()) == CONTRACT_OUTPUT_KEYS


def test_evaluate_fails_when_active_flags_missing_expected_code():
    brain = _offline_brain()
    step = Step(index=0, raw=nominal_raw(TIMESTAMP), anomaly_name=None)
    output = brain.process(step.raw)
    broken_output = dict(output)
    broken_output["activeFlags"] = []
    result = evaluate(step, broken_output)
    # nominal step expects no codes, so this alone should still pass codes-wise;
    # flip to an anomaly step to exercise the missing-code path.
    anomaly_step = dataclasses.replace(step, anomaly_name="tachycardia")
    anomaly_result = evaluate(anomaly_step, broken_output)
    assert result.passed
    assert not anomaly_result.passed
    assert any("missing expected flags" in failure for failure in anomaly_result.failures)


def test_main_exits_zero_on_default_offline_scenario(capsys):
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "QA:" in captured.out
    assert "steps passed" in captured.out


def test_main_json_flag_prints_a_list_of_outputs(capsys):
    exit_code = main(["--json", "--length", "3", "--anomalies", "3"])
    captured = capsys.readouterr()
    assert exit_code == 0
    import json

    outputs = json.loads(captured.out)
    assert isinstance(outputs, list)
    assert len(outputs) == 3
    for output in outputs:
        assert set(output.keys()) == CONTRACT_OUTPUT_KEYS
