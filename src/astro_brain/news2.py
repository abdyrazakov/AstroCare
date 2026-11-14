"""Standard NEWS2 (Royal College of Physicians, scale 1 for SpO2).

Each vital-sign component is scored independently against a small, ordered
table of ``(upper_bound_inclusive, score)`` bands. ``compute_news2`` sums the
seven component scores into a ``News2Result`` and classifies overall risk.

See AGENTS.md section 3 for the authoritative component tables.
"""

from __future__ import annotations

import math
import types
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from astro_brain.contract import VitalsSample

Risk = Literal["low", "low-medium", "medium", "high"]

# (upper_bound_inclusive, score), ascending by upper bound. The last entry's
# upper bound is +inf so every finite value matches some band.
Band = tuple[float, int]

RESP_RATE_BANDS: tuple[Band, ...] = ((8, 3), (11, 1), (20, 0), (24, 2), (math.inf, 3))
SPO2_BANDS: tuple[Band, ...] = ((91, 3), (93, 2), (95, 1), (math.inf, 0))
BP_SYSTOLIC_BANDS: tuple[Band, ...] = ((90, 3), (100, 2), (110, 1), (219, 0), (math.inf, 3))
HR_BANDS: tuple[Band, ...] = ((40, 3), (50, 1), (90, 0), (110, 1), (130, 2), (math.inf, 3))
TEMP_C_BANDS: tuple[Band, ...] = ((35.0, 3), (36.0, 1), (38.0, 0), (39.0, 1), (math.inf, 2))

SUPPLEMENTAL_O2_ON_SCORE = 2
SUPPLEMENTAL_O2_OFF_SCORE = 0
CONSCIOUSNESS_ALERT_SCORE = 0
CONSCIOUSNESS_ALTERED_SCORE = 3

HIGH_RISK_TOTAL = 7
MEDIUM_RISK_TOTAL_LOW = 5
MEDIUM_RISK_TOTAL_HIGH = 6
COMPONENT_THREE_SCORE = 3

COMPONENT_KEYS: tuple[str, ...] = (
    "resp_rate",
    "spo2",
    "supplemental_o2",
    "bp_systolic",
    "hr",
    "consciousness",
    "temp_c",
)


# --------------------------------------------------------------------------- band primitives


def band_index(value: float, bands: Sequence[Band]) -> int:
    """Index of the first band whose upper bound is >= ``value``."""
    for index, (upper, _score) in enumerate(bands):
        if value <= upper:
            return index
    raise ValueError(f"value {value!r} did not match any band (bands must end in +inf)")


def _score_from_bands(value: float, bands: Sequence[Band]) -> int:
    index = band_index(value, bands)
    return bands[index][1]


def nominal_band_index(bands: Sequence[Band]) -> int:
    """Index of the (single) zero-score "nominal" band in ``bands``."""
    for index, (_upper, score) in enumerate(bands):
        if score == 0:
            return index
    raise ValueError("bands have no nominal (score == 0) entry")


# --------------------------------------------------------------------------- per-component scores


def resp_rate_score(resp_rate: float) -> int:
    return _score_from_bands(resp_rate, RESP_RATE_BANDS)


def spo2_score(spo2: float) -> int:
    return _score_from_bands(spo2, SPO2_BANDS)


def supplemental_o2_score(on_supplemental_o2: bool) -> int:
    return SUPPLEMENTAL_O2_ON_SCORE if on_supplemental_o2 else SUPPLEMENTAL_O2_OFF_SCORE


def bp_systolic_score(systolic: float) -> int:
    return _score_from_bands(systolic, BP_SYSTOLIC_BANDS)


def hr_score(hr: float) -> int:
    return _score_from_bands(hr, HR_BANDS)


def consciousness_score(consciousness: str) -> int:
    if consciousness == "altered":
        return CONSCIOUSNESS_ALTERED_SCORE
    return CONSCIOUSNESS_ALERT_SCORE


def temp_c_score(temp_c: float) -> int:
    return _score_from_bands(temp_c, TEMP_C_BANDS)


# --------------------------------------------------------------------------- aggregate result


@dataclass(frozen=True)
class News2Result:
    """Computed NEWS2 score for one sample."""

    total: int
    components: Mapping[str, int]
    any_component_three: bool
    risk: Risk


def _classify_risk(total: int, any_component_three: bool) -> Risk:
    if total >= HIGH_RISK_TOTAL:
        return "high"
    if MEDIUM_RISK_TOTAL_LOW <= total <= MEDIUM_RISK_TOTAL_HIGH:
        return "medium"
    if any_component_three:
        return "low-medium"
    return "low"


def compute_news2(sample: VitalsSample) -> News2Result:
    """Compute the full NEWS2 result for ``sample``."""
    components = {
        "resp_rate": resp_rate_score(sample.resp_rate),
        "spo2": spo2_score(sample.spo2),
        "supplemental_o2": supplemental_o2_score(sample.on_supplemental_o2),
        "bp_systolic": bp_systolic_score(sample.bp.systolic),
        "hr": hr_score(sample.hr),
        "consciousness": consciousness_score(sample.consciousness),
        "temp_c": temp_c_score(sample.temp_c),
    }
    total = sum(components.values())
    any_three = any(score == COMPONENT_THREE_SCORE for score in components.values())
    risk = _classify_risk(total, any_three)
    return News2Result(
        total=total,
        components=types.MappingProxyType(components),
        any_component_three=any_three,
        risk=risk,
    )
