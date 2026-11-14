"""Offline end-to-end QA runner: feeds ``mock.scenario`` through ``Brain`` and
checks every output against its expected clinical outcome.

Runnable: ``python -m astro_brain.qa [--seed N] [--length N] [--anomalies N] [--json]``.
Pure, argv-free pieces (``run_scenario``, ``evaluate``) are what the tests call;
``main`` is the thin CLI/print layer and the only place in this module allowed
to call ``print``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .doctor.fallback import FLAG_ADVICE
from .doctor.layer import DoctorLayer
from .doctor.ollama_client import OllamaClient
from .mock import ANOMALIES, Step, scenario
from .pipeline import Brain

_ENV_QA_LLM = "ASTRO_QA_LLM"

CONTRACT_OUTPUT_KEYS: frozenset[str] = frozenset(
    {
        "timestamp",
        "astronautId",
        "alertLevel",
        "news2Score",
        "activeFlags",
        "flagDetails",
        "likelyConditions",
        "doctorRecommendation",
        "doctorSource",
        "bodySystems",
        "medicalKit",
        "plans",
    }
)


@dataclass(frozen=True)
class StepResult:
    """Outcome of checking one scenario step's ``Brain.process`` output."""

    index: int
    anomaly_name: str | None
    expected_level: str
    got_level: str
    flags: tuple[str, ...]
    doctor_source: str
    passed: bool
    failures: tuple[str, ...] = ()


def _build_brain() -> Brain:
    if os.environ.get(_ENV_QA_LLM) == "1":
        return Brain()
    return Brain(doctor=DoctorLayer(OllamaClient(), enabled=False))


def _expectations_for(step: Step) -> tuple[str, frozenset[str]]:
    if step.anomaly_name is None:
        return "green", frozenset()
    anomaly = ANOMALIES[step.anomaly_name]
    return anomaly.expected_level, anomaly.expected_codes


def _expected_conditions_for(step: Step) -> frozenset[str]:
    if step.anomaly_name is None:
        return frozenset()
    return ANOMALIES[step.anomaly_name].expected_conditions


def _condition_codes(output: Mapping[str, Any]) -> set[str]:
    conditions = output.get("likelyConditions", [])
    return {condition["code"] for condition in conditions} if isinstance(conditions, list) else set()


def _check_expected_conditions(output: Mapping[str, Any], expected: frozenset[str]) -> str | None:
    missing = expected - _condition_codes(output)
    if missing:
        return f"missing expected conditions {sorted(missing)}"
    return None


def _mentions_a_concern(text: str, active_flags: set[str]) -> bool:
    return any(FLAG_ADVICE[code] in text for code in active_flags if code in FLAG_ADVICE)


def _check_contract_keys(output: Mapping[str, Any]) -> str | None:
    actual = set(output.keys())
    if actual != CONTRACT_OUTPUT_KEYS:
        return f"output keys {sorted(actual)} != contract keys {sorted(CONTRACT_OUTPUT_KEYS)}"
    return None


def _check_json_serialisable(output: Mapping[str, Any]) -> str | None:
    try:
        json.dumps(output)
    except (TypeError, ValueError) as exc:
        return f"output is not JSON-serialisable: {exc}"
    return None


def _check_alert_level(output: Mapping[str, Any], expected_level: str) -> str | None:
    got = output.get("alertLevel")
    if got != expected_level:
        return f"alertLevel {got!r} != expected {expected_level!r}"
    return None


def _check_expected_codes(active_flags: set[str], expected_codes: frozenset[str]) -> str | None:
    missing = expected_codes - active_flags
    if missing:
        return f"missing expected flags {sorted(missing)}"
    return None


def _check_recommendation(
    output: Mapping[str, Any], expected_level: str, active_flags: set[str]
) -> str | None:
    recommendation = output.get("doctorRecommendation", "")
    if not recommendation:
        return "doctorRecommendation is empty"
    if expected_level != "green" and active_flags and not _mentions_a_concern(recommendation, active_flags):
        return "doctorRecommendation does not mention any active-flag concern"
    return None


def evaluate(step: Step, output: Mapping[str, Any]) -> StepResult:
    """Check ``output`` (``Brain.process(step.raw)``) against ``step``'s expectation."""
    expected_level, expected_codes = _expectations_for(step)
    expected_conditions = _expected_conditions_for(step)
    active_flags = set(output.get("activeFlags", []))

    failures = [
        failure
        for failure in (
            _check_contract_keys(output),
            _check_json_serialisable(output),
            _check_alert_level(output, expected_level),
            _check_expected_codes(active_flags, expected_codes),
            _check_expected_conditions(output, expected_conditions),
            _check_recommendation(output, expected_level, active_flags),
        )
        if failure is not None
    ]

    return StepResult(
        index=step.index,
        anomaly_name=step.anomaly_name,
        expected_level=expected_level,
        got_level=str(output.get("alertLevel")),
        flags=tuple(sorted(active_flags)),
        doctor_source=str(output.get("doctorSource", "")),
        passed=not failures,
        failures=tuple(failures),
    )


def run_scenario(brain: Brain, steps: Sequence[Step]) -> tuple[StepResult, ...]:
    """Process every step through ``brain`` and evaluate the result."""
    return tuple(evaluate(step, brain.process(step.raw)) for step in steps)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="astro_brain.qa", description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--length", type=int, default=24)
    parser.add_argument("--anomalies", type=int, default=4)
    parser.add_argument("--json", action="store_true", help="print raw outputs instead of a table")
    return parser.parse_args(argv)


def _print_table(results: Sequence[StepResult]) -> None:
    header = f"{'idx':>3}  {'anomaly':<20}{'expected':<9}{'got':<9}{'flags':<40}{'source':<9}status"
    print(header)
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        anomaly = result.anomaly_name or "-"
        flags = ",".join(result.flags) or "-"
        print(
            f"{result.index:>3}  {anomaly:<20}{result.expected_level:<9}{result.got_level:<9}"
            f"{flags:<40}{result.doctor_source:<9}{status}"
        )
        for failure in result.failures:
            print(f"       -> {failure}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    steps = scenario(seed=args.seed, length=args.length, anomalies=args.anomalies)
    brain = _build_brain()

    if args.json:
        outputs = [brain.process(step.raw) for step in steps]
        print(json.dumps(outputs, indent=2))
        results = tuple(evaluate(step, output) for step, output in zip(steps, outputs))
        return 0 if all(result.passed for result in results) else 1

    results = run_scenario(brain, steps)
    _print_table(results)
    passed = sum(1 for result in results if result.passed)
    print(f"QA: {passed}/{len(results)} steps passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
