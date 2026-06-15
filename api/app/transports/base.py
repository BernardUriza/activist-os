"""Transport interface every coordination backend must satisfy."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import Handoff, WorkflowRun


@runtime_checkable
class Transport(Protocol):
    name: str

    async def open(self, run: WorkflowRun) -> None:
        """Prepare any backend resources for the run (e.g. a Band room)."""
        ...

    async def deliver(self, run: WorkflowRun, handoff: Handoff) -> Handoff:
        """Publish one handoff; return it stamped with any backend metadata."""
        ...

    async def get_handoffs(self, run_id: str) -> list[Handoff]:
        """The recorded coordination history for a run."""
        ...


class TransportError(RuntimeError):
    """Base class for transport-construction / runtime failures."""
