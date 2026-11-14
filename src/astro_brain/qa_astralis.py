"""Optional validation bridge for the local Astralis simulator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adapters.astralis import stream_tick_to_input
from .pipeline import Brain
from .doctor.layer import DoctorLayer
from .doctor.ollama_client import OllamaClient

SCENARIOS = (
    "HYPERCAPNIC_CABIN", "SOLAR_PARTICLE_EVENT", "SANS_FLUID_SHIFT",
    "NEUROCOGNITIVE_FATIGUE", "MISSED_ARED",
)
EXPECTED = {
    "HYPERCAPNIC_CABIN": {"CABIN_CO2_ELEVATED", "CABIN_CO2_HIGH", "CO2_HEADACHE"},
    "SOLAR_PARTICLE_EVENT": {"RADIATION_ELEVATED", "RADIATION_CRITICAL", "ACUTE_RADIATION_SYNDROME"},
    "SANS_FLUID_SHIFT": {"IOP_HIGH", "SANS"},
    "NEUROCOGNITIVE_FATIGUE": {"PVT_SLOW", "SLEEP_DISORDER"},
    "MISSED_ARED": {"EXERCISE_DEFICIT"},
}
GENERIC = {"TEMP_LOW", "TEMP_HIGH", "NEWS2_MEDIUM", "NEWS2_HIGH", "EXERCISE_DEFICIT"}


def run(path: str, mission_seconds: int, step: int) -> list[dict[str, object]]:
    sys.path.insert(0, str(Path(path).resolve()))
    from simulation_engine.controller import SimulationController

    results: list[dict[str, object]] = []
    for scenario_id in SCENARIOS:
        controller = SimulationController(random_seed=42)
        controller.create_mission()
        try:
            controller.inject_scenario(scenario_id)
        except Exception as exc:
            results.append({"scenario": scenario_id, "status": "SKIP", "reason": str(exc)})
            continue
        controller.start()
        brain = Brain(DoctorLayer(OllamaClient(), enabled=False))
        seen: set[str] = set()
        first: dict[str, dict[str, object]] = {}
        generic_seen: set[str] = set()
        generic_first: dict[str, dict[str, object]] = {}
        peak = "green"
        for _ in range(0, mission_seconds, step):
            controller.advance(step)
            ticks = controller.stream_ticks()
            daily = controller.daily_logs()
            daily_by_key = {(item.get("astronaut_id"), item.get("mission_day")): item for item in daily}
            latest_by_id = {str(tick.get("astronaut_id")): tick for tick in ticks}
            for tick in latest_by_id.values():
                astronaut = str(tick.get("astronaut_id"))
                output = brain.process(stream_tick_to_input(tick, daily_by_key.get((astronaut, tick.get("mission_day")))))
                signals = set(output["activeFlags"])
                signals.update(str(item["code"]) for item in output.get("likelyConditions", []))
                for signal in signals & (GENERIC - EXPECTED[scenario_id]):
                    generic_seen.add(signal)
                    if signal not in generic_first:
                        generic_first[signal] = {
                            "second": controller.get_state().mission_time_seconds,
                            "value": tick.get("temp_c"),
                            "astronaut": astronaut,
                            "daily": daily_by_key.get((astronaut, tick.get("mission_day"))),
                        }
                for signal in signals & EXPECTED[scenario_id]:
                    seen.add(signal)
                    if signal not in first:
                        value = {
                            "CABIN_CO2_ELEVATED": tick.get("cabin_ppco2"),
                            "CABIN_CO2_HIGH": tick.get("cabin_ppco2"),
                            "IOP_HIGH": tick.get("iop_mmhg"),
                            "PVT_SLOW": tick.get("pvt_slowest10_rt"),
                            "RADIATION_ELEVATED": tick.get("radiation_dose_rate"),
                            "RADIATION_CRITICAL": tick.get("radiation_dose_rate"),
                            "EXERCISE_DEFICIT": (
                                daily_by_key.get((astronaut, tick.get("mission_day"))) or {}
                            ).get("ared_exercise_completed"),
                            "CO2_HEADACHE": tick.get("cabin_ppco2"),
                            "SANS": tick.get("iop_mmhg"),
                            "ACUTE_RADIATION_SYNDROME": tick.get("radiation_dose_rate"),
                        }.get(signal)
                        first[signal] = {"second": controller.get_state().mission_time_seconds, "value": value, "astronaut": astronaut}
                if {"green": 0, "yellow": 1, "red": 2}[output["alertLevel"]] > {"green": 0, "yellow": 1, "red": 2}[peak]:
                    peak = output["alertLevel"]
        results.append({"scenario": scenario_id, "status": "PASS" if seen else "FAIL", "signals": sorted(seen), "first": first, "generic": sorted(generic_seen), "genericFirst": generic_first, "peak": peak})
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="astro_brain.qa_astralis")
    parser.add_argument("--astralis-path", default="/tmp/astralis")
    parser.add_argument("--mission-seconds", type=int, default=1800)
    parser.add_argument("--step", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        results = run(args.astralis_path, args.mission_seconds, args.step)
    except ImportError as exc:
        print(f"QA-astralis: SKIP ({exc})")
        return 0
    for result in results:
        print(result)
    passed = sum(result["status"] == "PASS" for result in results)
    print(f"QA-astralis: {passed}/{len(results)} scenarios detected")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
