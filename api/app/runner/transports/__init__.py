import os

from .band_transport import BandTransport, BandTransportError
from .base import Transport
from .local_transport import LocalTransport

__all__ = [
    "BandTransport",
    "BandTransportError",
    "LocalTransport",
    "Transport",
    "create_transport",
]


def create_transport(kind: str | None = None) -> Transport:
    """Build the transport selected by `kind` or the TRANSPORT env var (local|band)."""
    kind = (kind or os.getenv("TRANSPORT") or "local").strip().lower()
    if kind == "local":
        return LocalTransport()
    if kind == "band":
        return BandTransport()
    raise ValueError(f"Unknown TRANSPORT '{kind}' — expected 'local' or 'band'")
