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

from app.models import UserConcern, WorkflowRun, WorkflowStatus
from app.runner.transports.local_transport import LocalTransport
from app.runner.workflow_runner import WorkflowRunner

# ── App state ──────────────────────────────────────────────────────────────

transport = LocalTransport()
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
        "transport": "LocalTransport",
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
