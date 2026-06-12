"""
Activist OS API — FastAPI entry point.
Port from insult-ai pattern: /health keyless, /workflow/* behind optional API key.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models import AgentHandoff, HandoffType, UserConcern, WorkflowRun, WorkflowStatus
from app.runner.transports import BandTransport, create_transport
from app.runner.workflow_runner import WorkflowRunner

# ── App state ──────────────────────────────────────────────────────────────

transport = create_transport()  # TRANSPORT=local|band (default: local)
runner = WorkflowRunner(transport)
_runs: dict[str, WorkflowRun] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Activist OS API",
    version="0.1.0",
    description="Multi-agent workflow for safe, evidence-backed civic advocacy.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health (keyless — required for Container Apps liveness probe) ──────────

@app.get("/health")
async def health():
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/health/full")
async def health_full():
    return {
        "status": "ok",
        "ts": datetime.now(timezone.utc).isoformat(),
        "active_runs": len(_runs),
        "transport": type(transport).__name__,
    }


# ── Workflow ───────────────────────────────────────────────────────────────

class StartWorkflowRequest(BaseModel):
    concern: str
    location: str | None = None
    category: str | None = None


@app.post("/workflow/start", status_code=202)
async def start_workflow(req: StartWorkflowRequest):
    concern = UserConcern(text=req.concern, location=req.location, category=req.category)
    run = WorkflowRun(concern=concern)
    _runs[run.run_id] = run
    asyncio.create_task(_execute(run))
    return {"run_id": run.run_id, "status": run.status}


async def _execute(run: WorkflowRun) -> None:
    try:
        completed = await runner.run(run)
        _runs[run.run_id] = completed
    except Exception as exc:
        run.status = WorkflowStatus.ERROR
        run.error = str(exc)
        _runs[run.run_id] = run


@app.get("/workflow/{run_id}")
async def get_workflow(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run.model_dump(mode="json")


def _first_text(*values: object, fallback: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _build_artifacts(handoffs: list[AgentHandoff], virtual_agents: frozenset[str]) -> dict:
    """Demo card artifacts derived from the real handoff payloads.

    Everything here comes from the coordination history — when a payload field
    is missing the summary degrades to a conservative derived line, never to
    hand-written campaign copy.
    """
    by_type: dict[HandoffType, list[dict]] = defaultdict(list)
    for h in handoffs:
        by_type[h.type].append(h.payload)

    evidence = (by_type[HandoffType.EVIDENCE_COMPLETE] or [{}])[0]
    claims = [c for c in (evidence.get("claims") or []) if isinstance(c, dict)]
    sources_count = sum(len(c.get("sources") or []) for c in claims)
    usable_count = sum(1 for c in claims if c.get("usable_in_campaign"))

    plans = by_type[HandoffType.SAFETY_REQUEST]
    first_plan = plans[0] if plans else {}
    last_plan = plans[-1] if plans else {}
    vetoes = by_type[HandoffType.SAFETY_VETO]
    last_veto = vetoes[-1] if vetoes else {}
    blocked = [b for b in (last_veto.get("blocked_items") or []) if isinstance(b, dict)]
    veto_reason = _first_text(
        "; ".join(
            f"{b.get('check', 'check')}: {b.get('description', '')}".strip(": ")
            for b in blocked
        ),
        last_veto.get("reviewer_notes"),
        fallback="No veto was recorded in this run's history.",
    )

    outreach = (by_type[HandoffType.OUTREACH_READY] or [{}])[0]
    tasks = (by_type[HandoffType.TASKS_READY] or [{}])[0]
    packet = (by_type[HandoffType.PACKET_READY] or [{}])[0]

    concern = _first_text(evidence.get("concern"), fallback="Community concern")
    approved = bool(by_type[HandoffType.SAFETY_APPROVED])

    return {
        "evidence_brief": {
            "title": concern,
            "summary": (
                f"{len(claims)} claims verified — {usable_count} usable in campaign, "
                f"{sources_count} sources with provenance tiers attached."
                if claims else "No evidence brief in this run's history."
            ),
            "claims_count": len(claims),
            "sources_count": sources_count,
        },
        "safety_review": {
            "draft_text": _first_text(
                first_plan.get("narrative"), first_plan.get("key_message"),
                fallback="No campaign draft in this run's history.",
            ),
            "veto_reason": veto_reason,
            "rewritten_text": _first_text(
                last_plan.get("narrative") if len(plans) > 1 else None,
                fallback="No revision was required.",
            ),
            "approved": approved,
            "veto_observed": bool(vetoes),
        },
        "campaign_packet": {
            "title": _first_text(packet.get("title"), fallback=f"Campaign packet — {concern}"),
            "summary": (
                f"Assembled from {len(handoffs)} coordinated handoffs; "
                f"safety audit log included ({'approved' if approved else 'not approved'})."
            ),
            "outreach_assets_count": len(outreach.get("assets") or []),
            "volunteer_tasks_count": len(tasks.get("tasks") or []),
            "provenance_items_count": sources_count,
            "reporter_virtual": "reporter" in virtual_agents,
        },
    }


@app.get("/workflow/{run_id}/history")
async def get_history(run_id: str):
    """Canonical coordination history for a run — what the demo shell renders."""
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")

    handoffs = await transport.get_handoffs(run_id)
    virtual = transport.virtual_agents
    types = [h.type for h in handoffs]
    veto_index = types.index(HandoffType.SAFETY_VETO) if HandoffType.SAFETY_VETO in types else None
    approved_index = (
        types.index(HandoffType.SAFETY_APPROVED)
        if HandoffType.SAFETY_APPROVED in types else None
    )

    return {
        "run_id": run_id,
        "status": run.status,
        "transport": "band" if isinstance(transport, BandTransport) else "local",
        "veto_loop": {
            "observed": veto_index is not None,
            "veto_index": veto_index,
            "approved_index": approved_index,
        },
        "artifacts": _build_artifacts(handoffs, frozenset(virtual)),
        "handoffs": [
            {
                "index": i,
                "from_agent": h.from_agent.value,
                "to_agent": h.to_agent.value,
                "type": h.type.value,
                "summary": f"{h.from_agent.value} → {h.to_agent.value}: {h.type.value}",
                "virtual": h.from_agent.value in virtual or h.to_agent.value in virtual,
                "band_room_id": h.metadata.band_room_id,
                "band_message_id": h.metadata.band_message_id,
                "timestamp": h.sent_at.isoformat(),
            }
            for i, h in enumerate(handoffs)
        ],
    }


@app.get("/workflow/{run_id}/events")
async def stream_events(run_id: str):
    """Server-Sent Events stream of audit events for a run."""
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")

    async def _generate():
        for event in run.audit_events:
            yield f"data: {event.model_dump_json()}\n\n"
        # Stream new events as they arrive (poll every 0.5s for LocalTransport)
        seen = len(run.audit_events)
        while run.status not in (WorkflowStatus.COMPLETED, WorkflowStatus.BLOCKED, WorkflowStatus.ERROR):
            await asyncio.sleep(0.5)
            new_events = run.audit_events[seen:]
            for event in new_events:
                yield f"data: {event.model_dump_json()}\n\n"
            seen += len(new_events)
        yield "data: {\"event_type\": \"stream_end\"}\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")
