"""Raw RFC6455 smoke tests for the dependency-free broadcaster."""

import base64
import json
import socket

from astro_brain.ws_server import BrainWebSocketServer


def _connect(server):
    client = socket.create_connection(("localhost", server.port), timeout=2)
    key = base64.b64encode(b"0123456789abcdef").decode()
    client.sendall(("GET / HTTP/1.1\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                    f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
    assert b"101 Switching Protocols" in client.recv(512)
    return client


def _read_frame(client):
    header = client.recv(2); length = header[1] & 0x7F
    if length == 126: length = int.from_bytes(client.recv(2), "big")
    if length == 127: length = int.from_bytes(client.recv(8), "big")
    data = b""
    while len(data) < length: data += client.recv(length - len(data))
    return data


def test_broadcast_handshake_and_text_frame():
    server = BrainWebSocketServer(port=0); server.start(); client = _connect(server)
    try:
        server.broadcast({"ok": True})
        assert json.loads(_read_frame(client)) == {"ok": True}
    finally:
        client.close(); server.close()


def test_broadcast_supports_large_payload():
    server = BrainWebSocketServer(port=0); server.start(); client = _connect(server)
    try:
        text = "x" * 70000; server.broadcast(text)
        assert _read_frame(client).decode() == text
    finally:
        client.close(); server.close()
