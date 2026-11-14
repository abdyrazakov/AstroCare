"""Deterministic daily exercise and nutrition plans."""
from __future__ import annotations

from typing import Any

PLAN_EVIDENCE = "NASA SP-20250000273; NTRS 20110016265 — prescription; plan bands DESIGN DECISION"

_CANCEL_CONDITIONS = {
    "HYPOVOLEMIC_SHOCK", "SEPSIS", "CARDIAC_ARRHYTHMIA",
    "ACUTE_RADIATION_SYNDROME", "RESPIRATORY_INFECTION_LOWER",
}
_REDUCE_FLAGS = {
    "SLEEP_DEFICIT", "PVT_SLOW", "LOW_MOOD", "CALORIC_DEFICIT",
    "CALORIC_LOW", "RADIATION_ELEVATED",
}


def build_plans(sample: Any, assessment: Any) -> dict[str, object]:
    conditions = {item.code for item in assessment.likely_conditions if item.confidence >= 0.5}
    flags = {flag.code for flag in assessment.flags}
    target = sample.required_exercise_minutes or 150
    cancelled = bool(conditions & _CANCEL_CONDITIONS) or "CABIN_CO2_HIGH" in flags
    reduced = bool(flags & _REDUCE_FLAGS) or "SANS" in conditions
    if cancelled:
        exercise_status = "cancelled"
        reason = "Exercise is cancelled because of " + ", ".join(sorted(conditions & _CANCEL_CONDITIONS or {"CABIN_CO2_HIGH"})) + "."
        sessions: list[dict[str, object]] = []
    elif reduced:
        exercise_status = "reduced"
        reason = "Reduce workload while active fatigue or exposure concerns are monitored."
        sessions = [{"type": "resistive", "minutes": round(target * 0.5), "note": "Reduced session; reassess before continuing."}]
    else:
        exercise_status = "normal"
        reason = "Continue the planned ARED and aerobic schedule."
        sessions = [{"type": "resistive", "minutes": 45, "note": "ARED/resistive session."}, {"type": "aerobic", "minutes": 30, "note": "Aerobic conditioning."}]
        if "EXERCISE_DEFICIT" in flags:
            sessions.append({"type": "resistive", "minutes": max(0, target - 75), "note": "Make-up session if tolerated."})
    nutrition_status = "increase" if flags & {"CALORIC_LOW", "CALORIC_DEFICIT"} else "monitor" if "NUTRITIONAL_DEFICIT" in conditions else "normal"
    hydration = "increase fluids and monitor urine output" if conditions & {"HYPOVOLEMIC_SHOCK", "ACUTE_RADIATION_SYNDROME"} or "TEMP_HIGH" in flags else "normal hydration"
    return {
        "exercise": {"status": exercise_status, "reason": reason, "sessions": sessions, "targetMinutes": target, "evidenceRef": PLAN_EVIDENCE},
        "nutrition": {"status": nutrition_status, "targetKcal": sample.caloric_target, "hydration": hydration, "evidenceRef": "JSC-63555; hydration advice is DESIGN DECISION"},
    }
