"""Top-level pure scoring entry point: ``assess``.

Combines NEWS2, vitals flags, radiation flags and lifestyle flags into one
immutable ``Assessment``. No I/O.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from astro_brain.conditions import LikelyCondition, likely_conditions
from astro_brain.contract import VitalsSample
from astro_brain.flags import AlertLevel, Flag, alert_level_from_flags
from astro_brain.lifestyle import lifestyle_flags
from astro_brain.news2 import compute_news2
from astro_brain.radiation import radiation_flags
from astro_brain.vitals_flags import vitals_flags
from astro_brain.environment import cabin_co2_flags
from astro_brain.neuro import neuro_flags


@dataclass(frozen=True)
class Assessment:
    """Pure result of scoring one ``VitalsSample``."""

    timestamp: str
    astronaut_id: str
    alert_level: AlertLevel
    news2_total: int
    news2_components: Mapping[str, int]
    flags: tuple[Flag, ...]
    likely_conditions: tuple[LikelyCondition, ...]

    def flag_codes(self) -> tuple[str, ...]:
        """Sorted, unique codes of all active flags."""
        return tuple(sorted({flag.code for flag in self.flags}))

    def condition_codes(self) -> tuple[str, ...]:
        """Condition codes in ranked order (most likely first)."""
        return tuple(condition.code for condition in self.likely_conditions)


def assess(sample: VitalsSample) -> Assessment:
    """Score ``sample``: NEWS2 -> vitals/radiation/lifestyle flags -> IMM-lite conditions."""
    news2 = compute_news2(sample)
    flags = (vitals_flags(news2, sample) + radiation_flags(sample) +
             cabin_co2_flags(sample) + neuro_flags(sample) + lifestyle_flags(sample))
    return Assessment(
        timestamp=sample.timestamp,
        astronaut_id=sample.astronaut_id,
        alert_level=alert_level_from_flags(flags),
        news2_total=news2.total,
        news2_components=news2.components,
        flags=flags,
        likely_conditions=likely_conditions(flags),
    )
