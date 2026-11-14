"""Feed ASTRALIS JSONL or live simulation ticks into AstroBrain."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from .adapters.astralis import stream_tick_to_input
from .pipeline import Brain


def _send(raw: dict[str, Any], args: argparse.Namespace, brain: Brain | None) -> None:
    try:
        if args.inprocess:
            output = brain.process(raw) if brain else Brain().process(raw)
            print(json.dumps({"alertLevel": output["alertLevel"], "flags": output["activeFlags"],
                              "conditions": output.get("likelyConditions", [])}, separators=(",", ":")))
            return
        request = Request(args.url, data=json.dumps(raw).encode(), headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=2) as response: response.read()
    except Exception as exc:
        print(f"tick error ({type(exc).__name__}): {exc}", file=sys.stderr)


def _jsonl(path: str, daily_path: str | None, args: argparse.Namespace) -> None:
    daily = {}
    if daily_path:
        for line in Path(daily_path).read_text().splitlines():
            item = json.loads(line); daily[(item.get("astronaut_id"), item.get("mission_day"))] = item
    brain = Brain() if args.inprocess else None
    for line in Path(path).read_text().splitlines():
        try:
            tick = json.loads(line); key = (tick.get("astronaut_id"), tick.get("mission_day"))
            _send(stream_tick_to_input(tick, daily.get(key)), args, brain)
        except Exception as exc: print(f"tick error: {exc}", file=sys.stderr)
        time.sleep(args.period / max(args.speed, 0.01))


def _live(args: argparse.Namespace) -> None:
    sys.path.insert(0, str(Path(args.astralis_path).resolve()))
    from simulation_engine.controller import SimulationController
    controller = SimulationController(random_seed=42)
    controller.create_mission()
    for scenario in args.scenario: controller.inject_scenario(scenario)
    controller.start(); brain = Brain() if args.inprocess else None
    deadline = time.monotonic() + args.duration_seconds if args.duration_seconds else None
    for tick in controller.iter_live():
        if deadline and time.monotonic() >= deadline: break
        try: _send(stream_tick_to_input(tick), args, brain)
        except Exception as exc: print(f"tick error: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="astro_brain.feed_astralis")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--jsonl"); source.add_argument("--live", action="store_true")
    parser.add_argument("--daily"); parser.add_argument("--period", type=float, default=1.0)
    parser.add_argument("--speed", type=float, default=1.0); parser.add_argument("--url", default="http://localhost:8765/ingest")
    parser.add_argument("--inprocess", action="store_true"); parser.add_argument("--astralis-path", default="/tmp/astralis")
    parser.add_argument("--scenario", action="append", default=[]); parser.add_argument("--duration-seconds", type=float, default=0)
    args = parser.parse_args(argv)
    _live(args) if args.live else _jsonl(args.jsonl, args.daily, args)


if __name__ == "__main__": main()
