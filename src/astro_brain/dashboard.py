"""Throwaway self-check dashboard for astro-brain (owner-only, zero design).

Runnable as ``.venv/bin/python -m astro_brain.dashboard [--port 8765] [--simulate]
[--period 2.0] [--seed 42] [--offline]``. Its only job is to let the brain's owner
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

    GET  /         text/plain snapshot: latest output, blank line, doctor stats,
                   one-line footer. Nothing else -- no HTML.
    GET  /state    latest output-contract JSON, or {"status": "no data yet"}.
    GET  /history  JSON list of the last ``HISTORY_LIMIT`` outputs.
    POST /ingest    one input-contract JSON sample -> output-contract JSON (200),
                   or 400 on a contract violation / invalid JSON body,
                   or 500 {"error": "<ExceptionType>"} on anything else.
    *              404 JSON for any other method/path.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import types
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .contract import ContractError
from .doctor.layer import DoctorLayer
from .doctor.ollama_client import OllamaClient
from .pipeline import Brain

HISTORY_LIMIT = 50
# Read-only: shared across request threads, so it must never be mutated in place.
NO_DATA = types.MappingProxyType({"status": "no data yet"})
DEFAULT_PORT = 8765
DEFAULT_PERIOD_S = 2.0
DEFAULT_SEED = 42


class StateStore:
    """Thread-safe holder of the latest output, bounded history and doctor stats.

    The only mutable state owned by this module; guarded by a single lock.
    """

    def __init__(self, history_limit: int = HISTORY_LIMIT) -> None:
        self._lock = threading.Lock()
        self._history_limit = history_limit
        self._latest: dict[str, Any] | None = None
        self._history: list[dict[str, Any]] = []
        self._doctor_stats: dict[str, int] = {}

    def update(self, output: dict[str, Any], doctor_stats: dict[str, int]) -> None:
        with self._lock:
            self._latest = output
            self._history.append(output)
            overflow = len(self._history) - self._history_limit
            if overflow > 0:
                del self._history[:overflow]
            self._doctor_stats = dict(doctor_stats)

    def latest(self) -> dict[str, Any] | None:
        with self._lock:
            return self._latest

    def history(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._history)

    def doctor_stats(self) -> dict[str, int]:
        with self._lock:
            return dict(self._doctor_stats)


def _doctor_stats_of(brain: Brain) -> dict[str, int]:
    """Snapshot ``DoctorLayer.stats``; ``Brain`` has no public accessor for it."""
    doctor = getattr(brain, "_doctor", None)
    stats = getattr(doctor, "stats", None)
    return dict(stats) if isinstance(stats, dict) else {}


def make_handler(brain: Brain, store: StateStore, *, verbose: bool = False) -> type:
    """Build a ``BaseHTTPRequestHandler`` subclass closed over ``brain``/``store``."""

    class Handler(BaseHTTPRequestHandler):
        server_version = "AstroBrainDashboard/0.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            if verbose:
                super().log_message(format, *args)

        def _write(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, payload: Any) -> None:
            self._write(status, json.dumps(payload).encode("utf-8"), "application/json")

        def _send_text(self, status: int, text: str) -> None:
            self._write(status, text.encode("utf-8"), "text/plain; charset=utf-8")

        def do_GET(self) -> None:  # noqa: N802
            routes = {"/": self._handle_root, "/state": self._handle_state, "/history": self._handle_history}
            handler = routes.get(self.path)
            if handler is None:
                self._send_json(404, {"error": f"not found: {self.path}"})
                return
            handler()

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/ingest":
                self._handle_ingest()
                return
            self._send_json(404, {"error": f"not found: {self.path}"})

        def _handle_root(self) -> None:
            data = store.latest() or dict(NO_DATA)
            doctor_stats = store.doctor_stats()
            port = self.server.server_port
            text = (
                f"{json.dumps(data, indent=2)}\n"
                "\n"
                f"{json.dumps(doctor_stats, indent=2)}\n"
                f"refresh: curl localhost:{port}/state\n"
            )
            self._send_text(200, text)

        def _handle_state(self) -> None:
            self._send_json(200, store.latest() or dict(NO_DATA))

        def _handle_history(self) -> None:
            self._send_json(200, store.history())

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
                output = brain.process(payload)
            except ContractError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            except Exception as exc:  # noqa: BLE001 - never leak a stack trace
                self._send_json(500, {"error": type(exc).__name__})
                return

            store.update(output, _doctor_stats_of(brain))
            self._send_json(200, output)

    return Handler


def build_server(port: int, brain: Brain, store: StateStore, *, verbose: bool = False) -> ThreadingHTTPServer:
    """Build a ``ThreadingHTTPServer`` bound to ``localhost:port`` (``port=0`` picks a free one)."""
    handler_cls = make_handler(brain, store, verbose=verbose)
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
    brain: Brain, store: StateStore, seed: int, period_s: float, *, verbose: bool = False
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

    for raw in mock.stream(seed=seed, period_s=period_s):
        try:
            output = brain.process(raw)
        except Exception as exc:  # noqa: BLE001 - a bad/unscoreable sample must not kill the feed
            if verbose:
                print(f"simulate: skipped sample: {exc!r}", file=sys.stderr)
            continue
        store.update(output, _doctor_stats_of(brain))


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="astro_brain.dashboard",
        description="Throwaway self-check dashboard for astro-brain (owner-only).",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--period", type=float, default=DEFAULT_PERIOD_S)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force a disabled Doctor Layer (rule-based text only, no Ollama calls).",
    )
    return parser.parse_args(argv)


def _startup_line(server: ThreadingHTTPServer, brain: Brain, simulate: bool) -> str:
    doctor_label = "live" if _doctor_is_enabled(brain) else "offline"
    status = [f"simulate={simulate}", f"doctor={doctor_label}"]
    if doctor_label == "live":
        status.append(f"ollama={_ollama_up_down(brain)}")
    return f"astro-brain dashboard listening on http://localhost:{server.server_port} ({' '.join(status)})"


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    brain = build_brain(offline=args.offline)
    store = StateStore()
    server = build_server(args.port, brain, store, verbose=args.verbose)

    if args.simulate:
        thread = threading.Thread(
            target=_simulate_loop,
            args=(brain, store, args.seed, args.period),
            kwargs={"verbose": args.verbose},
            daemon=True,
        )
        thread.start()

    print(_startup_line(server, brain, args.simulate), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
