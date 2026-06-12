"""
Transport interface — the only abstraction between the workflow engine and the
coordination layer. LocalTransport (in-memory, pre-kickoff) and BandTransport
(Band SDK, post-kickoff) both implement this interface.

Swapping LocalTransport → BandTransport is the only big change when Band
arrives. The agents and the runner never touch this directly — they call
WorkflowRunner.send_handoff() which delegates here.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.models import AgentHandoff, AuditEvent


class Transport(ABC):

    # Agents that coordinate through this transport without being real
    # participants of the coordination layer (see BandTransport).
    virtual_agents: frozenset[str] = frozenset()

    @abstractmethod
    async def send_handoff(self, handoff: AgentHandoff) -> None:
        """Publish a validated AgentHandoff to the coordination layer."""

    @abstractmethod
    async def subscribe(self, run_id: str) -> AsyncIterator[AgentHandoff]:
        """Yield incoming handoffs for a given run (used by SSE endpoint)."""

    @abstractmethod
    async def get_handoffs(self, run_id: str) -> list[AgentHandoff]:
        """Return the full ordered coordination history for a run."""

    @abstractmethod
    async def record_event(self, event: AuditEvent) -> None:
        """Append an immutable audit event for a run."""

    @abstractmethod
    async def get_events(self, run_id: str) -> list[AuditEvent]:
        """Return the full ordered audit trail for a run."""

    @abstractmethod
    async def get_context(self, run_id: str) -> dict:
        """Return the latest shared context for a run (serialized WorkflowRun)."""

    @abstractmethod
    async def set_context(self, run_id: str, context: dict) -> None:
        """Persist the updated shared context for a run."""
