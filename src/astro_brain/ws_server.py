"""Small dependency-free RFC 6455 text WebSocket broadcaster."""

from __future__ import annotations

import base64
import hashlib
import json
import socket
import struct
import threading
from collections.abc import Mapping


def _frame(payload: bytes) -> bytes:
    size = len(payload)
    if size < 126: header = bytes((0x81, size))
    elif size < 65536: header = bytes((0x81, 126)) + struct.pack("!H", size)
    else: header = bytes((0x81, 127)) + struct.pack("!Q", size)
    return header + payload


class BrainWebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8787) -> None:
        self.host, self.port = host, port
        self._server: socket.socket | None = None
        self._clients: set[socket.socket] = set()
        self._lock = threading.Lock()
        self._closed = threading.Event()

    def start(self) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.host, self.port)); self._server.listen()
        self.port = self._server.getsockname()[1]
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self) -> None:
        assert self._server is not None
        while not self._closed.is_set():
            try: client, _ = self._server.accept()
            except OSError: break
            threading.Thread(target=self._client_loop, args=(client,), daemon=True).start()

    def _client_loop(self, client: socket.socket) -> None:
        try:
            request = client.recv(4096).decode("latin1")
            key = next((line.split(":", 1)[1].strip() for line in request.split("\r\n")
                        if line.lower().startswith("sec-websocket-key:")), "")
            accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
            client.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                            f"Sec-WebSocket-Accept: {accept}\r\n\r\n").encode())
            with self._lock: self._clients.add(client)
            while not self._closed.is_set():
                header = client.recv(2)
                if not header: break
                length = header[1] & 0x7F
                if length == 126: length = struct.unpack("!H", client.recv(2))[0]
                elif length == 127: length = struct.unpack("!Q", client.recv(8))[0]
                masked = header[1] & 0x80
                mask = client.recv(4) if masked else b""
                data = bytearray(client.recv(length))
                if masked:
                    for i in range(length): data[i] ^= mask[i % 4]
                opcode = header[0] & 0x0F
                if opcode == 8: break
                if opcode == 9: client.sendall(bytes((0x8A, len(data))) + data)
        except OSError: pass
        finally:
            with self._lock: self._clients.discard(client)
            client.close()

    def broadcast(self, payload: Mapping[str, object] | str) -> None:
        text = payload if isinstance(payload, str) else json.dumps(payload, separators=(",", ":"))
        packet = _frame(text.encode())
        with self._lock: clients = tuple(self._clients)
        for client in clients:
            try: client.sendall(packet)
            except OSError:
                with self._lock: self._clients.discard(client)

    def close(self) -> None:
        self._closed.set()
        if self._server is not None: self._server.close()
        with self._lock: clients = tuple(self._clients); self._clients.clear()
        for client in clients: client.close()
