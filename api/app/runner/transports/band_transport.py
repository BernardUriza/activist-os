"""
BandTransport — placeholder for Band SDK integration.

At kickoff (Jun 12 15:00 UTC), open the Band SDK docs, fill the primitive
table in .claude/rules/band.md, then implement this class.

The interface contract is defined in base.py. Only this file changes
when Band arrives — not the agents, not the runner, not the API.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from app.models import AgentHandoff, AuditEvent
from .base import Transport


class BandTransport(Transport):
    """
    TODO at kickoff:
    1. Install Band SDK
    2. Implement agent registration / room creation
    3. Map HandoffType → Band message type
    4. Map AgentHandoff.metadata fields to Band message envelope
    5. Implement real-time subscribe() via Band's event stream
    6. Populate handoff.metadata.band_message_id and band_room_id on send
    """

    async def send_handoff(self, handoff: AgentHandoff) -> None:
        raise NotImplementedError("BandTransport: implement after SDK drops at kickoff")

    async def subscribe(self, run_id: str) -> AsyncIterator[AgentHandoff]:
        raise NotImplementedError("BandTransport: implement after SDK drops at kickoff")
        yield  # make it an async generator

    async def record_event(self, event: AuditEvent) -> None:
        raise NotImplementedError("BandTransport: implement after SDK drops at kickoff")

    async def get_events(self, run_id: str) -> list[AuditEvent]:
        raise NotImplementedError("BandTransport: implement after SDK drops at kickoff")

    async def get_context(self, run_id: str) -> dict:
        raise NotImplementedError("BandTransport: implement after SDK drops at kickoff")

    async def set_context(self, run_id: str, context: dict) -> None:
        raise NotImplementedError("BandTransport: implement after SDK drops at kickoff")
