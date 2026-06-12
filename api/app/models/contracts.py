"""
Pydantic models mirroring contracts/*.schema.json — the single source of
truth for every inter-agent payload. Keep these in sync with the JSON schemas.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────

class ProvenanceTier(str, Enum):
    FETCHED_FULLTEXT = "fetched_fulltext"
    NEWS_SEARCH = "news_search"
    COMPANY_SOURCE = "company_source"


class ClaimVerdict(str, Enum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"


class SafetyStatus(str, Enum):
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    BLOCKED = "blocked"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    EVIDENCE_RUNNING = "evidence_running"
    CAMPAIGN_RUNNING = "campaign_running"
    SAFETY_REVIEW = "safety_review"
    SAFETY_REVISION = "safety_revision"
    OUTREACH_RUNNING = "outreach_running"
    COORDINATOR_RUNNING = "coordinator_running"
    REPORTER_RUNNING = "reporter_running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ERROR = "error"


class AgentName(str, Enum):
    EVIDENCE = "evidence"
    CAMPAIGN = "campaign"
    SAFETY = "safety"
    OUTREACH = "outreach"
    COORDINATOR = "coordinator"
    REPORTER = "reporter"
    SYSTEM = "system"


class HandoffType(str, Enum):
    EVIDENCE_COMPLETE = "evidence_complete"
    CAMPAIGN_DRAFT_READY = "campaign_draft_ready"
    SAFETY_REQUEST = "safety_request"
    SAFETY_VETO = "safety_veto"
    SAFETY_APPROVED = "safety_approved"
    OUTREACH_READY = "outreach_ready"
    TASKS_READY = "tasks_ready"
    PACKET_READY = "packet_ready"
    ERROR = "error"


class EventType(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    HANDOFF_SENT = "handoff_sent"
    HANDOFF_RECEIVED = "handoff_received"
    SAFETY_VETO = "safety_veto"
    SAFETY_APPROVED = "safety_approved"
    SAFETY_REVISION_REQUESTED = "safety_revision_requested"
    CAMPAIGN_REWRITTEN = "campaign_rewritten"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_BLOCKED = "workflow_blocked"
    ERROR = "error"


# ── UserConcern ────────────────────────────────────────────────────────────

class UserConcern(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(min_length=10)
    location: str | None = None
    category: str | None = None
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_by: str | None = None


# ── EvidenceBrief ─────────────────────────────────────────────────────────

class EvidenceSource(BaseModel):
    url: str
    title: str | None = None
    provenance_tier: ProvenanceTier
    quote: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceClaim(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str
    verdict: ClaimVerdict
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[EvidenceSource]
    usable_in_campaign: bool = True


class EvidenceBrief(BaseModel):
    concern: str
    claims: list[EvidenceClaim] = Field(min_length=1)
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── CampaignPlan ──────────────────────────────────────────────────────────

class CampaignAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    channel: str
    target_audience: str | None = None


class CampaignPlan(BaseModel):
    run_id: str
    narrative: str
    key_message: str
    actions: list[CampaignAction]
    revision: int = Field(default=0, description="Incremented on each Safety-requested rewrite")
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── SafetyVerdict ─────────────────────────────────────────────────────────

class BlockedItem(BaseModel):
    check: str  # defamation | doxxing | harassment | unsupported_claims | escalation
    description: str
    target: str | None = None


class SafetyVerdict(BaseModel):
    run_id: str
    status: SafetyStatus
    blocked_items: list[BlockedItem] = Field(default_factory=list)
    reviewer_notes: str | None = None
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── OutreachPack ──────────────────────────────────────────────────────────

class OutreachAsset(BaseModel):
    asset_type: str  # social_post | email | flyer | press_release
    channel: str | None = None
    language: str
    content: str


class OutreachPack(BaseModel):
    run_id: str
    assets: list[OutreachAsset]
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── TaskBoard ─────────────────────────────────────────────────────────────

class VolunteerTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    channel: str | None = None
    estimated_hours: float | None = None
    materials_needed: list[str] = Field(default_factory=list)


class TaskBoard(BaseModel):
    run_id: str
    tasks: list[VolunteerTask]
    produced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── CampaignPacket ────────────────────────────────────────────────────────

class CampaignPacket(BaseModel):
    run_id: str
    concern: str
    evidence_brief: EvidenceBrief
    campaign_plan: CampaignPlan
    safety_verdict: SafetyVerdict
    outreach_pack: OutreachPack
    task_board: TaskBoard
    audit_events: list[AuditEvent] = Field(default_factory=list)
    assembled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── AuditEvent ────────────────────────────────────────────────────────────

class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str
    event_type: EventType
    agent: AgentName
    summary: str
    detail: dict[str, Any] | None = None
    handoff_ref: str | None = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── AgentHandoff ──────────────────────────────────────────────────────────

class HandoffMetadata(BaseModel):
    band_message_id: str | None = None
    band_room_id: str | None = None
    sequence: int | None = None


class AgentHandoff(BaseModel):
    handoff_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str
    from_agent: AgentName
    to_agent: AgentName
    type: HandoffType
    payload: dict[str, Any]
    metadata: HandoffMetadata = Field(default_factory=HandoffMetadata)
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    received_at: datetime | None = None


# ── WorkflowRun ───────────────────────────────────────────────────────────

class WorkflowRun(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concern: UserConcern
    status: WorkflowStatus = WorkflowStatus.PENDING
    veto_count: int = 0
    evidence_brief: EvidenceBrief | None = None
    campaign_plan: CampaignPlan | None = None
    safety_verdict: SafetyVerdict | None = None
    outreach_pack: OutreachPack | None = None
    task_board: TaskBoard | None = None
    campaign_packet: CampaignPacket | None = None
    audit_events: list[AuditEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    error: str | None = None

    def add_event(self, event: AuditEvent) -> None:
        self.audit_events.append(event)
        self.updated_at = datetime.now(timezone.utc)

    def set_status(self, status: WorkflowStatus) -> None:
        self.status = status
        self.updated_at = datetime.now(timezone.utc)


# Forward reference resolution
CampaignPacket.model_rebuild()
