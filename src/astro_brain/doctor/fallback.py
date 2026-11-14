"""Deterministic, rule-based recommendation text used when the LLM is unavailable.

``build_fallback`` never raises and never calls the network; it is the safety net
behind the Ollama-backed path in ``layer.py``. Composition rule:

1. A lead sentence chosen by ``alert_level`` (or ``NOMINAL_TEXT`` alone when green
   with no active flags).
2. One advice sentence per active flag, red flags first (in their original order),
   then the rest (in their original order), capped at ``_MAX_FLAGS_IN_TEXT``.
3. A closing line chosen by ``alert_level``.
"""

from __future__ import annotations

from typing import Final, Protocol

_MAX_FLAGS_IN_TEXT: Final[int] = 4

NOMINAL_TEXT: Final[str] = (
    "All monitored parameters nominal. No action needed; continue the normal schedule."
)

_LEAD_BY_ALERT_LEVEL: Final[dict[str, str]] = {
    "red": "IMMEDIATE ACTION REQUIRED.",
    "yellow": "Attention required.",
}

_CLOSING_BY_ALERT_LEVEL: Final[dict[str, str]] = {
    "red": "Contact ground medical now.",
    "yellow": "Re-check in 15 minutes; contact ground medical if it persists.",
}

# One actionable sentence for every flag code in AGENTS.md section 3 (20 codes).
FLAG_ADVICE: Final[dict[str, str]] = {
    "HR_HIGH": "Heart rate is high; have the astronaut rest and avoid exertion until it normalizes.",
    "HR_LOW": "Heart rate is low; monitor closely and avoid sudden exertion.",
    "SPO2_LOW": "Oxygen saturation is low; check life support and consider supplemental oxygen.",
    "BP_LOW": "Blood pressure is low; have the astronaut sit or lie down and recheck shortly.",
    "BP_HIGH": "Blood pressure is high; have the astronaut rest calmly and recheck shortly.",
    "TEMP_HIGH": "Core temperature is elevated; move to a cooler area and increase fluids.",
    "TEMP_LOW": "Core temperature is low; warm the astronaut and check suit thermal systems.",
    "RESP_HIGH": "Respiratory rate is elevated; have the astronaut slow breathing and rest.",
    "RESP_LOW": "Respiratory rate is low; monitor airway and breathing closely.",
    "CONSCIOUSNESS_ALTERED": (
        "Consciousness is altered; keep the astronaut under direct supervision and prepare "
        "to assist."
    ),
    "NEWS2_MEDIUM": "Overall NEWS2 score is moderately elevated; increase monitoring frequency.",
    "NEWS2_HIGH": "Overall NEWS2 score is critically elevated; treat as a medical emergency.",
    "RADIATION_ELEVATED": "Radiation dose rate is elevated; move to a shielded area until it drops.",
    "RADIATION_CRITICAL": "Radiation dose rate is critical; move to the most shielded area immediately.",
    "RADIATION_30DAY_LIMIT": (
        "Accumulated radiation dose over the last month is elevated; review the exposure "
        "record and shielding plan with ground medical."
    ),
    "RADIATION_CAREER_LIMIT": (
        "Accumulated career radiation dose requires review; consult ground medical "
        "before planning further exposure."
    ),
    "EXERCISE_DEFICIT": "Exercise today is below target; schedule the remaining time if feasible.",
    "CALORIC_DEFICIT": "Caloric intake is below target; increase food intake at the next meal.",
    "SLEEP_DEFICIT": "Sleep was below 6 hours; schedule a rest period before demanding tasks.",
    "LOW_MOOD": "Mood score is low; check in with the astronaut and consider a support break.",
}


class _FlagLike(Protocol):
    code: str
    severity: str


class _AssessmentLike(Protocol):
    alert_level: str
    flags: tuple[_FlagLike, ...]


def _generic_advice(code: str) -> str:
    return f"Monitor the active {code} condition and follow standard mission protocol."


def _advice_for(flag: _FlagLike) -> str:
    return FLAG_ADVICE.get(flag.code, _generic_advice(flag.code))


def _ordered_flags(flags: tuple[_FlagLike, ...]) -> list[_FlagLike]:
    # Stable sort: red flags first, each group keeping its original relative order.
    return sorted(flags, key=lambda flag: 0 if flag.severity == "red" else 1)


def build_fallback(assessment: _AssessmentLike) -> str:
    """Deterministic recommendation text; never raises, never touches the network."""
    flags = assessment.flags
    if assessment.alert_level == "green" and not flags:
        return NOMINAL_TEXT

    lead = _LEAD_BY_ALERT_LEVEL.get(assessment.alert_level, _LEAD_BY_ALERT_LEVEL["yellow"])
    closing = _CLOSING_BY_ALERT_LEVEL.get(
        assessment.alert_level, _CLOSING_BY_ALERT_LEVEL["yellow"]
    )
    selected = _ordered_flags(flags)[:_MAX_FLAGS_IN_TEXT]
    advice_sentences = [_advice_for(flag) for flag in selected]

    return " ".join([lead, *advice_sentences, closing])
