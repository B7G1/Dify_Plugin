"""Probe network and dmPython connectivity from the Dify plugin container."""

from __future__ import annotations

import socket
import sys


host, port_text, username, password = sys.argv[1:5]
port = int(port_text)
with socket.create_connection((host, port), timeout=5) as probe:
    print(f"TCP PASS peer={probe.getpeername()}")

import dmPython  # noqa: E402

connection = dmPython.connect(
    user=username,
    password=password,
    server=host,
    port=port,
    connection_timeout=10,
    local_code=1,
)
try:
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print(f"DM PASS result={cursor.fetchone()[0]}")
finally:
    connection.close()
