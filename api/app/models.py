"""Domain models for Activist OS + the template's chat request shape.

The Activist OS coordination domain (agents, handoffs, runs) lives here as pure
pydantic + enums — ZERO fi-runner / network imports, so the contract tests can
import it offline. ``ChatRequest`` (the python-bot template's chat surface) is
kept intact below, decoupled from ``app.validation`` so this module never pulls
the fi-runner backend chain.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from .contracts import UserConcern

# ── Activist OS coordination domain ────────────────────────────────────────


class AgentName(str, Enum):
    EVIDENCE = "evidence"
    CAMPAIGN = "campaign"
    SAFETY = "safety"
    OUTREACH = "outreach"
    COORDINATOR = "coordinator"
    REPORTER = "reporter"
    SYSTEM = "system"


VIRTUAL_AGENTS = frozenset({AgentName.REPORTER, AgentName.SYSTEM})


class HandoffType(str, Enum):
    HANDOFF = "handoff"
    SAFETY_VETO = "safety_veto"
    SAFETY_APPROVED = "safety_approved"
    TASKS_READY = "tasks_ready"
    PACKET_READY = "packet_ready"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ERROR = "error"


_EPOCH = datetime(2026, 1, 1, tzinfo=timezone.utc)


def deterministic_timestamp(index: int) -> str:
    """Stable, monotonic, now()-free timestamp so runs are reproducible."""
    return (_EPOCH + timedelta(seconds=index)).isoformat()


class HandoffMetadata(BaseModel):
    band_room_id: str | None = None
    band_message_id: str | None = None
    seat_cap: int | None = None
    virtual: bool = False
    emitted_by: str | None = None
    reason: str | None = None


class Handoff(BaseModel):
    index: int
    from_agent: AgentName
    to_agent: AgentName
    type: HandoffType
    summary: str
    timestamp: str
    payload: dict = Field(default_factory=dict)
    metadata: HandoffMetadata = Field(default_factory=HandoffMetadata)

    @property
    def is_virtual_leg(self) -> bool:
        return self.from_agent in VIRTUAL_AGENTS or self.to_agent in VIRTUAL_AGENTS


class AuditEvent(BaseModel):
    event_type: str
    data: dict = Field(default_factory=dict)


class WorkflowRun(BaseModel):
    run_id: str = Field(default_factory=lambda: uuid4().hex)
    concern: UserConcern
    status: WorkflowStatus = WorkflowStatus.PENDING
    error: str | None = None
    band_room_id: str | None = None
    handoffs: list[Handoff] = Field(default_factory=list)
    audit_events: list[AuditEvent] = Field(default_factory=list)


# ── Template chat surface (python-bot) — kept working, fi-runner-free here ──

REQUEST_TEXT_MAX_CHARS = int(os.getenv("APP_REQUEST_TEXT_MAX_CHARS", "12000"))


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=REQUEST_TEXT_MAX_CHARS)
    backend: str | None = None  # "claude" | "codex" (only claude streams live)
    corpus_id: str | None = Field(default=None, max_length=128)

    class Config:
        extra = "forbid"
