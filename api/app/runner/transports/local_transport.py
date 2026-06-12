"""
LocalTransport — in-memory transport for pre-kickoff development and smoke tests.
No external dependencies, runs entirely in-process.

Replace with BandTransport at kickoff: swap the import in workflow_runner.py.
The agent code, runner logic, and API endpoints don't change.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator

from app.models import AgentHandoff, AuditEvent
from .base import Transport


class LocalTransport(Transport):

    def __init__(self) -> None:
        # run_id → ordered list of handoffs
        self._handoffs: dict[str, list[AgentHandoff]] = defaultdict(list)
        # run_id → ordered audit log
        self._events: dict[str, list[AuditEvent]] = defaultdict(list)
        # run_id → latest serialized WorkflowRun
        self._context: dict[str, dict] = {}
        # run_id → asyncio.Queue for live subscribers
        self._queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def send_handoff(self, handoff: AgentHandoff) -> None:
        self._handoffs[handoff.run_id].append(handoff)
        await self._queues[handoff.run_id].put(handoff)

    async def subscribe(self, run_id: str) -> AsyncIterator[AgentHandoff]:
        q = self._queues[run_id]
        # Replay already-queued handoffs first
        for h in self._handoffs[run_id]:
            yield h
        # Then stream new ones
        while True:
            handoff = await q.get()
            yield handoff

    async def get_handoffs(self, run_id: str) -> list[AgentHandoff]:
        return list(self._handoffs[run_id])

    async def record_event(self, event: AuditEvent) -> None:
        self._events[event.run_id].append(event)

    async def get_events(self, run_id: str) -> list[AuditEvent]:
        return list(self._events[run_id])

    async def get_context(self, run_id: str) -> dict:
        return self._context.get(run_id, {})

    async def set_context(self, run_id: str, context: dict) -> None:
        self._context[run_id] = context
