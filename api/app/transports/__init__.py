"""Coordination transports + the env-driven selector."""
from __future__ import annotations

import os

from .band_transport import BandTransport, BandTransportError
from .base import Transport, TransportError
from .local_transport import LocalTransport

__all__ = [
    "Transport",
    "TransportError",
    "LocalTransport",
    "BandTransport",
    "BandTransportError",
    "create_transport",
]


def create_transport() -> Transport:
    """Select the transport from the ``TRANSPORT`` env var (default: local)."""
    mode = os.getenv("TRANSPORT", "local").lower()
    if mode == "local":
        return LocalTransport()
    if mode == "band":
        return BandTransport()
    raise ValueError(f"unknown TRANSPORT={mode!r} (expected 'local' or 'band')")
