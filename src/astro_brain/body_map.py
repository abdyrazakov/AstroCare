"""Deterministic flag/condition to frontend body-zone mapping."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

ZONE_IDS = (
    "brain", "eyes", "inner_ear", "heart", "lungs", "liver", "pancreas", "kidneys",
    "stomach_gi", "spine", "skeleton_upper", "skeleton_lower", "knees", "muscles_arms",
    "muscles_legs", "skin_immune",
)
FLAG_ZONES: dict[str, tuple[str, ...]] = {
    "heart": ("heart",), "lungs": ("lungs",), "skin": ("skin_immune",),
    "brain": ("brain",), "eyes": ("eyes",), "radiation": ("skin_immune",),
}
CONDITION_ZONES = {
    "HYPOVOLEMIC_SHOCK": ("heart",), "SEPSIS": ("skin_immune", "heart"),
    "RESPIRATORY_INFECTION_LOWER": ("lungs", "brain"), "ALTITUDE_SICKNESS": ("lungs", "brain"),
    "ACUTE_RADIATION_SYNDROME": ("skin_immune", "stomach_gi", "skeleton_upper", "skeleton_lower"),
    "CARDIAC_ARRHYTHMIA": ("heart",), "SLEEP_DISORDER": ("brain",), "DEPRESSION": ("brain",),
    "NUTRITIONAL_DEFICIT": ("stomach_gi", "muscles_legs"),
}
_RANK = {"green": 0, "yellow": 1, "red": 2}


def zones_for_flag(code: str) -> tuple[str, ...]:
    if code.startswith(("HR_", "BP_")): return ("heart",)
    if code.startswith(("SPO2_", "RESP_", "CABIN_CO2_")): return ("lungs",)
    if code.startswith("TEMP_"): return ("skin_immune",)
    if code in {"CONSCIOUSNESS_ALTERED", "PVT_SLOW", "SLEEP_DEFICIT", "LOW_MOOD", "PHQ2_POSITIVE"}: return ("brain",)
    if code == "IOP_HIGH": return ("eyes",)
    if code == "HYPERCAPNIA": return ("lungs", "brain")
    if code == "SANS": return ("eyes", "brain")
    if code == "RADIATION_30DAY_LIMIT" or code == "RADIATION_CAREER_LIMIT":
        return ("skin_immune", "skeleton_upper", "skeleton_lower")
    if code.startswith("RADIATION_"): return ("skin_immune",)
    if code == "EXERCISE_DEFICIT": return ("muscles_legs", "skeleton_lower")
    if code.startswith("CALORIC_"): return ("stomach_gi",)
    return ()


def body_systems(flags: Iterable[Mapping[str, object]], conditions: Iterable[Mapping[str, object]]) -> dict[str, str]:
    result = {zone: "green" for zone in ZONE_IDS}
    for flag in flags:
        severity = str(flag.get("severity", "yellow"))
        for zone in zones_for_flag(str(flag.get("code", ""))):
            if _RANK.get(severity, 0) > _RANK[result[zone]]: result[zone] = severity
    for condition in conditions:
        if float(condition.get("confidence", 0)) < 0.5: continue
        for zone in CONDITION_ZONES.get(str(condition.get("code", "")), ()):
            if _RANK["yellow"] > _RANK[result[zone]]: result[zone] = "yellow"
    return result
