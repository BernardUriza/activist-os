"""
Activist OS API — FastAPI entry point.
Port from insult-ai pattern: /health keyless, /workflow/* behind optional API key.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models import HandoffType, UserConcern, WorkflowRun, WorkflowStatus
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
