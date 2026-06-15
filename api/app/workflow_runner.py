"""Deterministic Activist OS coordination loop.

Produces exactly the canonical 8 handoffs (one veto → one revision → approval)
from a ``UserConcern``, with payloads rich enough to derive the demo artifacts.
Pure and deterministic — no LLM, no network. The transport decides how those
handoffs are published (in-memory vs Band room).
"""
from __future__ import annotations

from .contracts import UserConcern
from .models import (
    AgentName,
    AuditEvent,
    Handoff,
    HandoffType,
    WorkflowRun,
    WorkflowStatus,
    deterministic_timestamp,
)
from .transports.base import Transport

A = AgentName
H = HandoffType

CANONICAL_STEPS: list[tuple[AgentName, AgentName, HandoffType]] = [
    (A.EVIDENCE, A.CAMPAIGN, H.HANDOFF),
    (A.CAMPAIGN, A.SAFETY, H.HANDOFF),
    (A.SAFETY, A.CAMPAIGN, H.SAFETY_VETO),
    (A.CAMPAIGN, A.SAFETY, H.HANDOFF),
    (A.SAFETY, A.OUTREACH, H.SAFETY_APPROVED),
    (A.OUTREACH, A.COORDINATOR, H.HANDOFF),
    (A.COORDINATOR, A.REPORTER, H.TASKS_READY),
    (A.REPORTER, A.SYSTEM, H.PACKET_READY),
]

CANONICAL_FROM_ORDER = [frm for frm, _, _ in CANONICAL_STEPS]


def _draft_v1(c: str) -> str:
    return f"DRAFT v1 — public call-out: {c}"


def _draft_v2(c: str) -> str:
    return f"DRAFT v2 — evidenced concern, sourced and qualified: {c}"


def build_payload(index: int, concern: UserConcern) -> tuple[str, dict]:
    """Return (summary, payload) for the handoff at ``index``."""
    c = concern.concern
    frm, to, typ = CANONICAL_STEPS[index]
    summary = f"{typ.value.replace('_', ' ')}: {frm.value} → {to.value}"

    if index == 0:  # evidence → campaign
        return summary, {
            "title": c,
            "summary": f"Evidence brief on: {c}",
            "claims": [
                f"Claimed: {c}",
                "Independent corroboration of the claim is required",
            ],
            "sources": [
                "src://news/local-bulletin",
                "src://registry/public-record",
                "src://archive/prior-coverage",
            ],
        }
    if index == 1:  # campaign → safety (first draft)
        return summary, {"draft_text": _draft_v1(c)}
    if index == 2:  # safety → campaign (VETO)
        return summary, {
            "veto_reason": "Draft v1 states an unverified accusatory claim as fact.",
            "blocked_items": [{"check": "unverified_claim", "severity": "high"}],
            "requested_revision": "Qualify the claim and cite the evidence brief.",
        }
    if index == 3:  # campaign → safety (revised draft)
        return summary, {"draft_text": _draft_v2(c)}
    if index == 4:  # safety → outreach (APPROVED)
        return summary, {
            "approved_text": _draft_v2(c),
            "rewritten_text": _draft_v2(c),
        }
    if index == 5:  # outreach → coordinator
        return summary, {
            "assets": [
                f"email-blast: {c}",
                f"social-post: {c}",
                f"poster: {c}",
            ]
        }
    if index == 6:  # coordinator → reporter (tasks)
        return summary, {
            "tasks": [
                "Assign canvassers to the affected district",
                "Schedule the volunteer briefing",
                "Collect petition signatures",
                "Log provenance for every published claim",
            ]
        }
    # index == 7: reporter → system (packet)
    return summary, {
        "title": f"Campaign packet: {c}",
        "summary": f"Full coordination record for: {c}",
        "provenance": [
            "Evidence brief with sources",
            "Safety audit: veto + approved revision",
        ],
    }


class WorkflowRunner:
    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        await self.transport.open(run)
        run.status = WorkflowStatus.RUNNING
        run.audit_events.append(
            AuditEvent(event_type="workflow_started", data={"run_id": run.run_id})
        )

        for index, (frm, to, typ) in enumerate(CANONICAL_STEPS):
            summary, payload = build_payload(index, run.concern)
            handoff = Handoff(
                index=index,
                from_agent=frm,
                to_agent=to,
                type=typ,
                summary=summary,
                timestamp=deterministic_timestamp(index),
                payload=payload,
            )
            handoff = await self.transport.deliver(run, handoff)
            run.handoffs.append(handoff)
            run.audit_events.append(
                AuditEvent(
                    event_type="handoff_sent",
                    data={
                        "index": index,
                        "from_agent": frm.value,
                        "to_agent": to.value,
                        "type": typ.value,
                    },
                )
            )

        run.status = WorkflowStatus.COMPLETED
        run.audit_events.append(
            AuditEvent(
                event_type="workflow_completed",
                data={"run_id": run.run_id, "handoffs": len(run.handoffs)},
            )
        )
        return run
