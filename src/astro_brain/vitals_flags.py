"""Per-component and aggregate NEWS2 flags.

For every NEWS2 component scoring >= 2, emit one directional yellow flag
(``supplemental_o2`` contributes to the score but has no flag of its own).
Then add the aggregate ``NEWS2_MEDIUM``/``NEWS2_HIGH`` flag, which are
mutually exclusive.

``threshold`` on a directional flag is the NEWS2 band edge the measured value
crossed to reach its current score (the upper bound of the next-less-extreme
band), giving a precise, score-specific edge rather than one fixed number per
flag code.
"""

from __future__ import annotations

from astro_brain.contract import VitalsSample
from astro_brain.evidence import EVIDENCE_BY_CODE
from astro_brain.flags import Flag
from astro_brain.news2 import (
    BP_SYSTOLIC_BANDS,
    COMPONENT_THREE_SCORE,
    HIGH_RISK_TOTAL,
    HR_BANDS,
    MEDIUM_RISK_TOTAL_HIGH,
    MEDIUM_RISK_TOTAL_LOW,
    RESP_RATE_BANDS,
    SPO2_BANDS,
    TEMP_C_BANDS,
    Band,
    News2Result,
    band_index,
    nominal_band_index,
)

# Design choice for flag emission; NEWS2 source bands are unchanged.
# https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf (Charts 1–2)
FLAGGED_MIN_SCORE = 2


def _edge_crossed(value: float, bands: tuple[Band, ...]) -> float:
    index = band_index(value, bands)
    if index == 0:
        return bands[0][0]
    return bands[index - 1][0]


def _two_sided_flag(
    score: int,
    value: float,
    bands: tuple[Band, ...],
    low_code: str,
    high_code: str,
    label: str,
    unit: str,
) -> Flag | None:
    if score < FLAGGED_MIN_SCORE:
        return None
    index = band_index(value, bands)
    nominal = nominal_band_index(bands)
    threshold = _edge_crossed(value, bands)
    if index < nominal:
        code, direction = low_code, "low"
    else:
        code, direction = high_code, "high"
    message = f"{label} {value:g}{unit} is {direction} (crossed {threshold:g}{unit})."
    return Flag(
        code=code, evidence=EVIDENCE_BY_CODE[code],
        severity="yellow", message=message, value=value,
        threshold=threshold
    )


def _spo2_flag(score: int, spo2: float) -> Flag | None:
    if score < FLAGGED_MIN_SCORE:
        return None
    threshold = _edge_crossed(spo2, SPO2_BANDS)
    message = f"SpO2 {spo2:g}% is low (crossed {threshold:g}%)."
    return Flag(
        code="SPO2_LOW", evidence=EVIDENCE_BY_CODE["SPO2_LOW"],
        severity="yellow", message=message, value=spo2,
        threshold=threshold
    )


def _consciousness_flag(score: int) -> Flag | None:
    if score < FLAGGED_MIN_SCORE:
        return None
    return Flag(
        code="CONSCIOUSNESS_ALTERED", evidence=EVIDENCE_BY_CODE["CONSCIOUSNESS_ALTERED"],
        severity="yellow",
        message="Consciousness is altered.",
        value=None,
        threshold=None,
    )


def _components_scoring_three(news2: News2Result) -> tuple[str, ...]:
    return tuple(
        name for name in news2.components if news2.components[name] == COMPONENT_THREE_SCORE
    )


def _medium_total_flag(total: int) -> Flag:
    message = f"NEWS2 total {total} is medium risk."
    return Flag(
        code="NEWS2_MEDIUM", evidence=EVIDENCE_BY_CODE["NEWS2_MEDIUM"],
        severity="yellow",
        message=message,
        value=total,
        threshold=MEDIUM_RISK_TOTAL_LOW,
    )


def _medium_single_parameter_flag(news2: News2Result) -> Flag:
    components = ", ".join(_components_scoring_three(news2))
    message = (
        f"NEWS2 single parameter at maximum score ({COMPONENT_THREE_SCORE}) — {components} "
        "— urgent re-check required."
    )
    return Flag(
        code="NEWS2_MEDIUM", evidence=EVIDENCE_BY_CODE["NEWS2_MEDIUM"],
        severity="yellow",
        message=message,
        value=COMPONENT_THREE_SCORE,
        threshold=COMPONENT_THREE_SCORE,
    )


def _aggregate_flag(news2: News2Result) -> Flag | None:
    if news2.total >= HIGH_RISK_TOTAL:
        message = f"NEWS2 total {news2.total} is high risk (>= {HIGH_RISK_TOTAL})."
        return Flag(
            code="NEWS2_HIGH", evidence=EVIDENCE_BY_CODE["NEWS2_HIGH"],
            severity="red", message=message, value=news2.total,
            threshold=HIGH_RISK_TOTAL,
        )
    is_medium_total = MEDIUM_RISK_TOTAL_LOW <= news2.total <= MEDIUM_RISK_TOTAL_HIGH
    if is_medium_total:
        return _medium_total_flag(news2.total)
    if news2.any_component_three:
        return _medium_single_parameter_flag(news2)
    return None


def vitals_flags(news2: News2Result, sample: VitalsSample) -> tuple[Flag, ...]:
    """Directional component flags plus the aggregate NEWS2 flag."""
    candidates = (
        _two_sided_flag(
            news2.components["resp_rate"], sample.resp_rate, RESP_RATE_BANDS,
            "RESP_LOW", "RESP_HIGH", "Respiratory rate", "/min",
        ),
        _spo2_flag(news2.components["spo2"], sample.spo2),
        _two_sided_flag(
            news2.components["bp_systolic"], sample.bp.systolic, BP_SYSTOLIC_BANDS,
            "BP_LOW", "BP_HIGH", "Systolic BP", " mmHg",
        ),
        _two_sided_flag(
            news2.components["hr"], sample.hr, HR_BANDS,
            "HR_LOW", "HR_HIGH", "Heart rate", " bpm",
        ),
        _consciousness_flag(news2.components["consciousness"]),
        _two_sided_flag(
            news2.components["temp_c"], sample.temp_c, TEMP_C_BANDS,
            "TEMP_LOW", "TEMP_HIGH", "Temperature", " C",
        ),
        _aggregate_flag(news2),
    )
    return tuple(flag for flag in candidates if flag is not None)
