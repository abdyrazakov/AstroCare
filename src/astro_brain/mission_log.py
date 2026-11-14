"""Bounded EMCL-vocabulary mission episode log."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any


def _seconds(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


@dataclass(frozen=True)
class Episode:
    start: str
    end: str | None
    alert_level: str
    flags: tuple[str, ...]
    conditions: tuple[str, ...]
    peak_confidence: float
    resources_suggested: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "start": self.start, "end": self.end, "alertLevel": self.alert_level,
            "flags": list(self.flags), "conditions": list(self.conditions),
            "peakConfidence": self.peak_confidence,
            "resourcesSuggested": list(self.resources_suggested),
        }


class MissionLog:
    """Thread-safe episode store, bounded to 500 episodes per astronaut."""
    def __init__(self, limit: int = 500) -> None:
        self._lock = threading.Lock()
        self._limit = limit
        self._episodes: dict[str, list[Episode]] = {}
        self._last: dict[str, dict[str, Any]] = {}

    def record(self, output: dict[str, Any]) -> None:
        astronaut = str(output["astronautId"])
        timestamp = str(output["timestamp"])
        flags = tuple(sorted(str(item) for item in output.get("activeFlags", ())))
        conditions_data = output.get("likelyConditions", ())
        conditions = tuple(str(item.get("code")) for item in conditions_data if isinstance(item, dict))
        confidence = max((float(item.get("confidence", 0)) for item in conditions_data if isinstance(item, dict)), default=0.0)
        resources: set[str] = set()
        for item in conditions_data:
            if isinstance(item, dict):
                for resource in item.get("resources", ()):
                    if isinstance(resource, dict):
                        resources.add(str(resource.get("code")))
        signature = (str(output.get("alertLevel")), flags)
        with self._lock:
            previous = self._last.get(astronaut)
            episodes = self._episodes.setdefault(astronaut, [])
            if previous and previous["signature"] == signature:
                current = episodes[-1]
                episodes[-1] = Episode(current.start, None, current.alert_level, current.flags, current.conditions, max(current.peak_confidence, confidence), tuple(sorted(set(current.resources_suggested) | resources)))
            else:
                if previous and episodes:
                    current = episodes[-1]
                    episodes[-1] = Episode(current.start, timestamp, current.alert_level, current.flags, current.conditions, current.peak_confidence, current.resources_suggested)
                episodes.append(Episode(timestamp, None, signature[0], flags, conditions, confidence, tuple(sorted(resources))))
                del episodes[:-self._limit]
            self._last[astronaut] = {"signature": signature, "timestamp": timestamp}

    def episodes(self, astronaut_id: str | None = None) -> dict[str, list[dict[str, object]]] | list[dict[str, object]]:
        with self._lock:
            if astronaut_id is not None:
                return [item.to_dict() for item in self._episodes.get(astronaut_id, ())]
            return {key: [item.to_dict() for item in value] for key, value in self._episodes.items()}

    def report(self, astronaut_id: str) -> dict[str, object] | None:
        with self._lock:
            episodes = tuple(self._episodes.get(astronaut_id, ()))
            last = self._last.get(astronaut_id)
        if not episodes or last is None:
            return None
        totals = {"green": 0.0, "yellow": 0.0, "red": 0.0}
        condition_stats: dict[str, dict[str, float]] = {}
        for index, episode in enumerate(episodes):
            end = episode.end or last["timestamp"]
            duration = max(0.0, _seconds(str(end)) - _seconds(episode.start))
            totals[episode.alert_level] = totals.get(episode.alert_level, 0.0) + duration
            for code in episode.conditions:
                row = condition_stats.setdefault(code, {"episodes": 0, "totalSeconds": 0.0})
                row["episodes"] += 1
                row["totalSeconds"] += duration
        conditions = [{"code": code, **{key: round(value, 2) if isinstance(value, float) else value for key, value in row.items()}} for code, row in sorted(condition_stats.items())]
        return {
            "astronautId": astronaut_id, "timeByLevel": {key: round(value, 2) for key, value in totals.items()},
            "episodes": len(episodes), "conditionsSeen": conditions,
            "flagsSeen": sorted({flag for episode in episodes for flag in episode.flags}),
            "note": "IMM/IMPACT feedback: episodes use EMCL/IMM condition vocabulary for comparison with mission-planning assumptions.",
        }

    def report_text(self, astronaut_id: str) -> str | None:
        report = self.report(astronaut_id)
        if report is None:
            return None
        return "SBAR\nSituation: astronaut %s has %s logged episodes.\nBackground: time by level %s.\nAssessment: conditions %s.\nRecommendation: review active flags and contact ground medical for red episodes." % (astronaut_id, report["episodes"], report["timeByLevel"], report["conditionsSeen"])
