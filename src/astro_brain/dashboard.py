"""Throwaway self-check dashboard for astro-brain (owner-only, zero design).

Runnable as ``.venv/bin/python -m astro_brain.dashboard [--port 8765] [--simulate]
[--crew 1] [--period 2.0] [--seed 42] [--offline]``. Its only job is to let the brain's owner
see with their own eyes that the brain emits sensible output-contract JSON, never
hangs, and switches ``alertLevel`` -- it is NOT for the presentation team and
carries no CSS/JS/charts.

By default the dashboard builds ``Brain()`` with no args, so it exercises the
real Doctor Layer (``ASTRO_OLLAMA_URL`` / ``ASTRO_OLLAMA_MODEL`` /
``ASTRO_DOCTOR_OFFLINE`` env vars, cache / 3s timeout -> fallback / background
upgrade, as implemented in pipeline.py). Pass ``--offline`` to force a disabled
Doctor Layer (rule-based text only, no Ollama calls) instead.

Endpoints (see AGENTS.md section 4 for the base contract; this tool additionally
exposes ``GET /`` and ``GET /history`` as debug aids, and returns a 200 placeholder
rather than a 404 from ``GET /state`` before any data has arrived, so a human
refreshing the page before the first sample sees a clear status instead of an error):

    GET  /         text/plain snapshot: latest output per astronaut, blank line, doctor stats,
                   one-line footer. Nothing else -- no HTML.
    GET  /state    latest output-contract JSON, or {"status": "no data yet"}.
    GET  /state/all  latest outputs by astronautId and count.
    /state and /history accept ?astronaut_id=X to filter by astronaut.
    GET  /history  JSON list of the last ``HISTORY_LIMIT`` outputs.
    POST /ingest    one input-contract JSON sample -> output-contract JSON (200),
                   or 400 on a contract violation / invalid JSON body,
                   or 500 {"error": "<ExceptionType>"} on anything else.
    *              404 JSON for any other method/path.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import types
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

from .contract import ContractError
from .doctor.layer import DoctorLayer
from .doctor.ollama_client import OllamaClient
from .pipeline import Brain
from .adapters.frontend import to_brain_tick
from .ws_server import BrainWebSocketServer
from .mission_log import MissionLog

HISTORY_LIMIT = 50
# Read-only: shared across request threads, so it must never be mutated in place.
NO_DATA = types.MappingProxyType({"status": "no data yet"})
DEFAULT_PORT = 8765
DEFAULT_WS_PORT = 8787
DEFAULT_PERIOD_S = 2.0
DEFAULT_SEED = 42
DEFAULT_CREW = 1
MAX_CREW = 6


class StateStore:
    """Thread-safe holder of the latest output, bounded history and doctor stats.

    The only mutable state owned by this module; guarded by a single lock.
    """

    def __init__(self, history_limit: int = HISTORY_LIMIT) -> None:
        self._lock = threading.Lock()
        self._history_limit = history_limit
        self._latest: dict[str, Any] | None = None
        self._history: deque[dict[str, Any]] = deque(maxlen=history_limit)
        self._latest_by_id: dict[str, dict[str, Any]] = {}
        self._history_by_id: dict[str, deque[dict[str, Any]]] = {}
        self._doctor_stats: dict[str, int] = {}
        self.mission_log = MissionLog()

    def update(self, output: dict[str, Any], doctor_stats: dict[str, int]) -> None:
        astronaut_id = output["astronautId"]
        with self._lock:
            self._latest = output
            self._history.append(output)
            self._latest_by_id[astronaut_id] = output
            history = self._history_by_id.setdefault(
                astronaut_id, deque(maxlen=self._history_limit)
            )
            history.append(output)
            self._doctor_stats = dict(doctor_stats)
            self.mission_log.record(output)

    def latest(self, astronaut_id: str | None = None) -> dict[str, Any] | None:
        with self._lock:
            if astronaut_id is None:
                return self._latest
            return self._latest_by_id.get(astronaut_id)

    def all_latest(self) -> dict[str, Any]:
        with self._lock:
            return {"astronauts": dict(self._latest_by_id), "count": len(self._latest_by_id)}

    def history(self, astronaut_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if astronaut_id is None:
                return list(self._history)
            return list(self._history_by_id.get(astronaut_id, ()))

    def doctor_stats(self) -> dict[str, int]:
        with self._lock:
            return dict(self._doctor_stats)


def _doctor_stats_of(brain: Brain) -> dict[str, int]:
    """Snapshot ``DoctorLayer.stats``; ``Brain`` has no public accessor for it."""
    doctor = getattr(brain, "_doctor", None)
    stats = getattr(doctor, "stats", None)
    return dict(stats) if isinstance(stats, dict) else {}


class _Handler(BaseHTTPRequestHandler):
    brain: Brain
    store: StateStore
    verbose: bool
    ws: BrainWebSocketServer | None
    seq: list[int]
    server_version = "AstroBrainDashboard/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        if self.verbose:
            super().log_message(format, *args)

    def _write(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: Any) -> None:
        self._write(status, json.dumps(payload).encode("utf-8"), "application/json")

    def _send_text(self, status: int, text: str) -> None:
        self._write(status, text.encode("utf-8"), "text/plain; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        routes = {
            "/": self._handle_root, "/state": self._handle_state,
            "/state/all": self._handle_all, "/history": self._handle_history,
            "/log": self._handle_log, "/report": self._handle_report,
        }
        handler = routes.get(urlsplit(self.path).path)
        if handler is None:
            self._send_json(404, {"error": f"not found: {self.path}"})
            return
        handler()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/ingest":
            self._handle_ingest()
            return
        if self.path == "/ask":
            self._handle_ask()
            return
        self._send_json(404, {"error": f"not found: {self.path}"})

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _handle_root(self) -> None:
        astronauts = self.store.all_latest()["astronauts"]
        blocks = [json.dumps(data, indent=2) for data in astronauts.values()]
        text = "\n\n".join(blocks) if blocks else json.dumps(dict(NO_DATA))
        text += f"\n\ndoctorStats: {json.dumps(self.store.doctor_stats(), indent=2)}\n"
        text += f"refresh: curl localhost:{self.server.server_port}/state\n"
        self._send_text(200, text)

    def _astronaut_id(self) -> str | None:
        query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
        return query.get("astronaut_id", [None])[0]

    def _handle_state(self) -> None:
        astronaut_id = self._astronaut_id()
        empty = dict(NO_DATA)
        if astronaut_id is not None:
            empty["astronautId"] = astronaut_id
        self._send_json(200, self.store.latest(astronaut_id) or empty)

    def _handle_all(self) -> None:
        self._send_json(200, self.store.all_latest())

    def _handle_history(self) -> None:
        self._send_json(200, self.store.history(self._astronaut_id()))

    def _handle_log(self) -> None:
        payload = self.store.mission_log.episodes(self._astronaut_id())
        self._send_json(200, payload)

    def _handle_report(self) -> None:
        astronaut_id = self._astronaut_id()
        if astronaut_id is None:
            self._send_json(400, {"error": "astronaut_id is required"})
            return
        report = self.store.mission_log.report(astronaut_id)
        if report is None:
            self._send_json(404, {"error": "no data for astronaut", "astronautId": astronaut_id})
            return
        query = parse_qs(urlsplit(self.path).query)
        if query.get("format", [""])[0] == "text":
            self._send_text(200, self.store.mission_log.report_text(astronaut_id) or "")
        else:
            self._send_json(200, report)

    def _read_json_body(self) -> Any:
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        raw_body = self.rfile.read(length) if length > 0 else b""
        return json.loads(raw_body)

    def _handle_ingest(self) -> None:
        try:
            payload = self._read_json_body()
        except json.JSONDecodeError as exc:
            self._send_json(400, {"error": f"invalid JSON body: {exc}"})
            return

        try:
            output = self.brain.process(payload)
        except ContractError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except Exception as exc:  # noqa: BLE001 - never leak a stack trace
            self._send_json(500, {"error": type(exc).__name__})
            return

        self.store.update(output, _doctor_stats_of(self.brain))
        if self.ws is not None:
            self.ws.broadcast(to_brain_tick(output, payload, self.seq[0])); self.seq[0] += 1
        self._send_json(200, output)

    def _handle_ask(self) -> None:
        try:
            payload = self._read_json_body()
        except json.JSONDecodeError as exc:
            self._send_json(400, {"error": f"invalid JSON body: {exc}"})
            return
        astronaut_id = payload.get("astronaut_id") if isinstance(payload, dict) else None
        question = payload.get("question") if isinstance(payload, dict) else None
        if not isinstance(astronaut_id, str) or not isinstance(question, str):
            self._send_json(400, {"error": "astronaut_id and question are required"})
            return
        question = question[:500].strip()
        if not question:
            self._send_json(400, {"error": "question must not be empty"})
            return
        context = self.store.latest(astronaut_id)
        if context is None:
            self._send_json(404, {"error": "no data for astronaut", "astronautId": astronaut_id})
            return
        doctor = getattr(self.brain, "_doctor", None)
        try:
            timeout_s = float(os.environ.get("ASTRO_ASK_TIMEOUT_S", "30"))
        except ValueError:
            timeout_s = 30.0
        response = doctor.ask(context, question, timeout_s=timeout_s)
        response["contextTimestamp"] = str(context.get("timestamp", ""))
        self._send_json(200, response)


def make_handler(brain: Brain, store: StateStore, *, verbose: bool = False,
                 ws: BrainWebSocketServer | None = None, seq: list[int] | None = None) -> type:
    """Bind one handler class to a server's brain and store."""
    return type("Handler", (_Handler,), {"brain": brain, "store": store, "verbose": verbose,
                                         "ws": ws, "seq": seq or [0]})


def build_server(port: int, brain: Brain, store: StateStore, *, verbose: bool = False,
                 ws: BrainWebSocketServer | None = None, seq: list[int] | None = None) -> ThreadingHTTPServer:
    """Build a ``ThreadingHTTPServer`` bound to ``localhost:port`` (``port=0`` picks a free one)."""
    handler_cls = make_handler(brain, store, verbose=verbose, ws=ws, seq=seq)
    return ThreadingHTTPServer(("localhost", port), handler_cls)


def build_brain(*, offline: bool = False) -> Brain:
    """Build the ``Brain`` the dashboard runs against.

    ``offline=True`` forces a disabled Doctor Layer (rule-based text only, no
    network). Otherwise defers to ``Brain()``'s own env-driven default
    (``ASTRO_OLLAMA_URL`` / ``ASTRO_OLLAMA_MODEL`` / ``ASTRO_DOCTOR_OFFLINE``,
    see pipeline.py), so by default the dashboard exercises the real Doctor
    Layer (cache / 3s timeout -> fallback / background upgrade) now that
    Ollama is installed.
    """
    if offline:
        return Brain(doctor=DoctorLayer(OllamaClient(), enabled=False))
    return Brain()


def _doctor_is_enabled(brain: Brain) -> bool:
    doctor = getattr(brain, "_doctor", None)
    return bool(getattr(doctor, "_enabled", True))


def _ollama_up_down(brain: Brain) -> str:
    """Probe the brain's own configured client; never called when offline/in tests."""
    client = getattr(getattr(brain, "_doctor", None), "_client", None)
    probe = getattr(client, "is_available", None)
    return "up" if callable(probe) and probe() else "down"


def _simulate_loop(
    brain: Brain, store: StateStore, seed: int, period_s: float, *,
    ws: BrainWebSocketServer | None = None, seq: list[int] | None = None,
    verbose: bool = False, astronaut_ids: tuple[str, ...] = ("ASTRO-01",),
) -> None:
    """Daemon-thread target: feed ``mock.stream`` samples into ``store`` via ``brain`` forever.

    ``astro_brain.mock`` is owned by a parallel agent and imported lazily here (only on
    the ``--simulate`` path) so importing this module never depends on its presence.
    A malformed mock sample is skipped rather than killing the feed thread; a sample
    the brain cannot otherwise process is likewise skipped so the demo keeps running.
    With ``verbose``, each skip is reported to stderr -- the one other allowed
    diagnostic print besides the startup line -- instead of vanishing silently.
    """
    from . import mock  # lazy: see docstring

    for raw in mock.stream(seed=seed, period_s=period_s, astronaut_ids=astronaut_ids):
        try:
            output = brain.process(raw)
        except Exception as exc:  # noqa: BLE001 - a bad/unscoreable sample must not kill the feed
            if verbose:
                print(f"simulate: skipped sample: {exc!r}", file=sys.stderr)
            continue
        store.update(output, _doctor_stats_of(brain))
        if ws is not None and seq is not None:
            ws.broadcast(to_brain_tick(output, raw, seq[0])); seq[0] += 1


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="astro_brain.dashboard",
        description="Throwaway self-check dashboard for astro-brain (owner-only).",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--crew", type=int, choices=range(1, MAX_CREW + 1), default=DEFAULT_CREW)
    parser.add_argument("--period", type=float, default=DEFAULT_PERIOD_S)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--ws-port", type=int, default=DEFAULT_WS_PORT)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force a disabled Doctor Layer (rule-based text only, no Ollama calls).",
    )
    return parser.parse_args(argv)


def _startup_line(server: ThreadingHTTPServer, brain: Brain, simulate: bool, ws: BrainWebSocketServer | None) -> str:
    doctor_label = "live" if _doctor_is_enabled(brain) else "offline"
    status = [f"simulate={simulate}", f"doctor={doctor_label}"]
    if doctor_label == "live":
        status.append(f"ollama={_ollama_up_down(brain)}")
    ws_text = f" ws=ws://localhost:{ws.port}" if ws is not None else ""
    return f"astro-brain dashboard listening on http://localhost:{server.server_port}{ws_text} ({' '.join(status)})"


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    brain = build_brain(offline=args.offline)
    store = StateStore()
    ws = BrainWebSocketServer(port=args.ws_port) if args.ws_port else None
    if ws is not None: ws.start()
    seq = [0]
    server = build_server(args.port, brain, store, verbose=args.verbose, ws=ws, seq=seq)

    if args.simulate:
        thread = threading.Thread(
            target=_simulate_loop,
            args=(brain, store, args.seed, args.period),
            kwargs={"verbose": args.verbose,
                    "ws": ws, "seq": seq,
                    "astronaut_ids": tuple(f"ASTRO-{i:02d}" for i in range(1, args.crew + 1))},
            daemon=True,
        )
        thread.start()

    print(_startup_line(server, brain, args.simulate, ws), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
        if ws is not None: ws.close()


if __name__ == "__main__":
    main()
