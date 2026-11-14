"""Phase multipliers for the prototype IMM-lite ranking."""
from __future__ import annotations
from types import MappingProxyType

PHASE_PRIORS = MappingProxyType({
    "PHASE_1_ACUTE_ADAPTATION": MappingProxyType({
        "ALTITUDE_SICKNESS": 1.1, "SANS": 0.8, "DEPRESSION": 0.8,
        "NUTRITIONAL_DEFICIT": 1.1,
    }),
    "PHASE_2_LONG_DURATION": MappingProxyType({
        "SANS": 1.3, "DEPRESSION": 1.2, "SLEEP_DISORDER": 1.2,
        "NUTRITIONAL_DEFICIT": 1.2, "CARDIAC_ARRHYTHMIA": 1.1,
    }),
})


def phase_multiplier(condition: str, mission_phase: str | None) -> float:
    """Return the documented design multiplier for a mission phase."""
    if mission_phase is None:
        return 1.0
    return float(PHASE_PRIORS.get(mission_phase, {}).get(condition, 1.0))
