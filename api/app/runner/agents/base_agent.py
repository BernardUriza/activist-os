from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from app.models import AgentName, AuditEvent, EventType, WorkflowRun


class BaseAgent(ABC):
    name: AgentName

    def _event(self, run: WorkflowRun, event_type: EventType, summary: str, detail: dict | None = None) -> AuditEvent:
        return AuditEvent(
            run_id=run.run_id,
            event_type=event_type,
            agent=self.name,
            summary=summary,
            detail=detail,
            occurred_at=datetime.now(timezone.utc),
        )

    @abstractmethod
    async def run(self, run: WorkflowRun) -> WorkflowRun:
        """Execute this agent's role and return the updated WorkflowRun."""
