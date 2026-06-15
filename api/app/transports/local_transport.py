"""In-memory transport — the single-process default.

Records handoffs as-is. Does NOT mark the reporter virtual and assigns no
band_room_id; those are Band-mode concerns.
"""
from __future__ import annotations

from ..models import Handoff, WorkflowRun


class LocalTransport:
    name = "local"

    def __init__(self) -> None:
        self._handoffs: dict[str, list[Handoff]] = {}

    async def open(self, run: WorkflowRun) -> None:
        self._handoffs.setdefault(run.run_id, [])

    async def deliver(self, run: WorkflowRun, handoff: Handoff) -> Handoff:
        self._handoffs.setdefault(run.run_id, []).append(handoff)
        return handoff

    async def get_handoffs(self, run_id: str) -> list[Handoff]:
        return list(self._handoffs.get(run_id, []))
