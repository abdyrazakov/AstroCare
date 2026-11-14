"""Clinical flags and alert-level aggregation.

A ``Flag`` is one detected condition (e.g. ``SLEEP_DEFICIT``). The overall
``alertLevel`` in the output contract is the worst severity among active flags:
any red flag -> ``"red"``; otherwise any flag -> ``"yellow"``; no flags -> ``"green"``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, get_args

Severity = Literal["yellow", "red"]
AlertLevel = Literal["green", "yellow", "red"]

_VALID_SEVERITIES: frozenset[str] = frozenset(get_args(Severity))

FlagValue = float | int | str | None


@dataclass(frozen=True)
class Flag:
    """One active clinical/operational flag, serialisable to the output contract."""

    code: str
    severity: Severity
    message: str
    value: FlagValue = None
    threshold: FlagValue = None

    def __post_init__(self) -> None:
        if self.severity not in _VALID_SEVERITIES:
            allowed = ", ".join(sorted(_VALID_SEVERITIES))
            raise ValueError(
                f"Flag {self.code!r}: invalid severity {self.severity!r} (allowed: {allowed})"
            )

    def to_dict(self) -> dict[str, FlagValue]:
        """Return the ``flagDetails`` entry shape of the output contract."""
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
        }


def alert_level_from_flags(flags: tuple[Flag, ...]) -> AlertLevel:
    """Worst severity among ``flags``: red > yellow > green (no flags)."""
    if any(flag.severity == "red" for flag in flags):
        return "red"
    if flags:
        return "yellow"
    return "green"
