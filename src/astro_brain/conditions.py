"""IMM-lite: rank plausible medical conditions from the brain's active flags.

Prototype adaptation of the ExMC Integrated Medical Model (IMM) and the
Exploration Medical Condition List (EMCL, JSC-65722) vocabulary. It reuses the
condition names NASA uses for exploration medical risk, but deliberately does
NOT reimplement IMM's Monte Carlo model: risk is a transparent, deterministic
evidence score over the brain's own validated flags.

The output is differential support ("conditions to watch"), never a diagnosis.
``confidence`` is an evidence-strength score in [0, 1], not a calibrated
probability. See ``AGENTS.md`` section 3 and ``docs/EVIDENCE.md``.
"""

from __future__ import annotations

from dataclasses import dataclass

from astro_brain.evidence import CONDITION_EVIDENCE_BY_CODE
from astro_brain.flags import Flag

MIN_CONFIDENCE = 0.25
MAX_CONDITIONS = 3


@dataclass(frozen=True)
class ConditionRule:
    """One condition and the weighted flag evidence that supports it."""

    code: str
    label: str
    saturation: float
    weights: tuple[tuple[str, float], ...]
    min_drivers: int = 1


@dataclass(frozen=True)
class LikelyCondition:
    """One ranked condition candidate, serialisable to the output contract."""

    code: str
    label: str
    confidence: float
    drivers: tuple[str, ...]
    evidence: str

    def to_dict(self) -> dict[str, object]:
        """Return the ``likelyConditions`` entry shape of the output contract."""
        return {
            "code": self.code,
            "label": self.label,
            "confidence": round(self.confidence, 2),
            "drivers": list(self.drivers),
            "evidenceRef": self.evidence,
        }


# Weights and saturation are prototype design decisions (docs/EVIDENCE.md).
# ``drivers`` order follows the tuple order; ``min_drivers`` suppresses weak
# single-signal guesses for conditions that need a constellation of findings.
CONDITION_RULES: tuple[ConditionRule, ...] = (
    ConditionRule(
        code="HYPOVOLEMIA",
        label="Hypovolemia / volume depletion",
        saturation=0.9,
        weights=(
            ("BP_LOW", 0.45),
            ("HR_HIGH", 0.30),
            ("RESP_HIGH", 0.10),
            ("CONSCIOUSNESS_ALTERED", 0.15),
        ),
    ),
    ConditionRule(
        code="SEPSIS",
        label="Sepsis",
        saturation=0.9,
        weights=(
            ("TEMP_HIGH", 0.40),
            ("TEMP_LOW", 0.20),
            ("HR_HIGH", 0.20),
            ("RESP_HIGH", 0.15),
            ("BP_LOW", 0.25),
            ("SPO2_LOW", 0.10),
        ),
        min_drivers=2,
    ),
    ConditionRule(
        code="HYPOXEMIA",
        label="Hypoxemia / hypoxia",
        saturation=0.8,
        weights=(
            ("SPO2_LOW", 0.65),
            ("RESP_HIGH", 0.15),
            ("RESP_LOW", 0.10),
            ("CONSCIOUSNESS_ALTERED", 0.10),
        ),
    ),
    ConditionRule(
        code="ACUTE_RADIATION_SYNDROME",
        label="Acute radiation syndrome / radiation sickness",
        saturation=0.8,
        weights=(
            ("RADIATION_CRITICAL", 0.55),
            ("RADIATION_30DAY_LIMIT", 0.30),
            ("RADIATION_CAREER_LIMIT", 0.20),
            ("RADIATION_ELEVATED", 0.15),
            ("TEMP_HIGH", 0.10),
        ),
    ),
    ConditionRule(
        code="CARDIAC_ARRHYTHMIA",
        label="De novo cardiac arrhythmia",
        saturation=0.8,
        weights=(
            ("HR_HIGH", 0.55),
            ("HR_LOW", 0.55),
            ("BP_LOW", 0.15),
            ("CONSCIOUSNESS_ALTERED", 0.15),
        ),
    ),
    ConditionRule(
        code="SLEEP_DISORDER",
        label="Sleep disorder",
        saturation=0.8,
        weights=(("SLEEP_DEFICIT", 0.70), ("LOW_MOOD", 0.15)),
    ),
    ConditionRule(
        code="DEPRESSION",
        label="Depression / behavioral health concern",
        saturation=0.9,
        weights=(
            ("LOW_MOOD", 0.65),
            ("SLEEP_DEFICIT", 0.20),
            ("EXERCISE_DEFICIT", 0.10),
        ),
    ),
    ConditionRule(
        code="NUTRITIONAL_DEFICIT",
        label="Nutritional deficiency",
        saturation=0.8,
        weights=(("CALORIC_DEFICIT", 0.70), ("EXERCISE_DEFICIT", 0.10)),
    ),
)


def _score(rule: ConditionRule, active: frozenset[str]) -> LikelyCondition | None:
    drivers = tuple(code for code, _weight in rule.weights if code in active)
    if len(drivers) < rule.min_drivers:
        return None
    total = sum(weight for code, weight in rule.weights if code in active)
    confidence = min(1.0, total / rule.saturation)
    if confidence < MIN_CONFIDENCE:
        return None
    return LikelyCondition(
        code=rule.code,
        label=rule.label,
        confidence=confidence,
        drivers=drivers,
        evidence=CONDITION_EVIDENCE_BY_CODE[rule.code],
    )


def likely_conditions(flags: tuple[Flag, ...]) -> tuple[LikelyCondition, ...]:
    """Rank at most ``MAX_CONDITIONS`` condition candidates supported by ``flags``.

    Pure and deterministic: same flags -> same ranking. Ties break by code.
    """
    active = frozenset(flag.code for flag in flags)
    ranked = [condition for rule in CONDITION_RULES if (condition := _score(rule, active)) is not None]
    ranked.sort(key=lambda condition: (-condition.confidence, condition.code))
    return tuple(ranked[:MAX_CONDITIONS])
