"""Activist OS HTTP face — the coordination API the demo shell consumes.

Self-contained FastAPI app (separate from the python-bot template's chat
``app.app``). Runs the deterministic workflow synchronously, keeps runs
in-memory, and exposes the canonical history + SSE audit stream.
"""
from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .auth import limiter, verify_api_key
from .contracts import UserConcern
from .models import HandoffType, VIRTUAL_AGENTS, WorkflowRun
from .observability import request_observability_middleware
from .transports import create_transport
from .workflow_runner import WorkflowRunner

# Cable app.* logs into uvicorn's stdout — without this, info() calls vanish in
# the Container App. Idempotent on --reload. (Mirrors the template's app.app;
# this is the DEPLOYED app now, so the cabling has to live here.)
_root_log = logging.getLogger()
if not _root_log.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
logging.getLogger("app").setLevel(logging.INFO)

app = FastAPI(title="activist-os", version="0.1.0")

# Per-request id + timing + one access log per request (total-instrumentation
# doctrine). Same middleware the template's app.app uses.
app.middleware("http")(request_observability_middleware)

# CORS — the Next app calls these endpoints cross-origin. Same pattern the
# template's app.app uses: lock to CORS_ALLOW_ORIGINS in prod, wide-open in dev.
_cors_env = (os.getenv("CORS_ALLOW_ORIGINS") or "").strip()
_cors_origins = (
    [o.strip() for o in _cors_env.split(",") if o.strip()] if _cors_env else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Server-Timing"],
)

# Per-IP rate limit — the cost-control floor. /workflow/start can spawn the real
# band of agents (band transport), so a casual crawler hitting it must not drain
# the agent budget. Same limiter the template gates /chat/stream with.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_transport = create_transport()
_runner = WorkflowRunner(_transport)
_runs: dict[str, WorkflowRun] = {}
_STARTED_AT = time.time()


def _require_run(run_id: str) -> WorkflowRun:
    run = _runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"unknown run_id: {run_id}")
    return run


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/health/full")
async def health_full() -> dict:
    return {
        "status": "ok",
        "transport": _transport.name,
        "runs": len(_runs),
        "uptime_s": round(time.time() - _STARTED_AT, 1),
    }


@app.post("/workflow/start", status_code=202, dependencies=[Depends(verify_api_key)])
@limiter.limit("30/hour")
async def start_workflow(request: Request, concern: UserConcern) -> dict:
    run = WorkflowRun(concern=concern)
    await _runner.run(run)
    _runs[run.run_id] = run
    return {"run_id": run.run_id, "status": run.status.value}


def _veto_loop(run: WorkflowRun) -> dict:
    types = [h.type for h in run.handoffs]
    veto_index = types.index(HandoffType.SAFETY_VETO) if HandoffType.SAFETY_VETO in types else None
    approved_index = (
        types.index(HandoffType.SAFETY_APPROVED)
        if HandoffType.SAFETY_APPROVED in types
        else None
    )
    return {
        "observed": veto_index is not None and approved_index is not None,
        "veto_index": veto_index,
        "approved_index": approved_index,
    }


def _is_virtual(handoff) -> bool:
    return _transport.name == "band" and (
        handoff.from_agent in VIRTUAL_AGENTS or handoff.to_agent in VIRTUAL_AGENTS
    )


def _build_artifacts(run: WorkflowRun) -> dict:
    by_index = {h.index: h for h in run.handoffs}
    evidence = by_index[0].payload
    draft_v1 = by_index[1].payload
    veto = by_index[2].payload
    approved = by_index[4].payload
    outreach = by_index[5].payload
    coordinator = by_index[6].payload
    reporter = by_index[7].payload

    types = [h.type for h in run.handoffs]
    return {
        "evidence_brief": {
            "title": evidence["title"],
            "summary": evidence["summary"],
            "claims_count": len(evidence["claims"]),
            "sources_count": len(evidence["sources"]),
        },
        "safety_review": {
            "veto_observed": HandoffType.SAFETY_VETO in types,
            "approved": HandoffType.SAFETY_APPROVED in types,
            "draft_text": draft_v1["draft_text"],
            "veto_reason": veto["veto_reason"],
            "rewritten_text": approved["rewritten_text"],
        },
        "campaign_packet": {
            "reporter_virtual": any(
                h.to_agent.value == "reporter" and _is_virtual(h)
                for h in run.handoffs
            ),
            "outreach_assets_count": len(outreach["assets"]),
            "volunteer_tasks_count": len(coordinator["tasks"]),
            "provenance_items_count": len(reporter["provenance"]),
            "title": reporter["title"],
            "summary": reporter["summary"],
        },
    }


@app.get("/workflow/{run_id}/history")
async def get_history(run_id: str) -> dict:
    run = _require_run(run_id)
    return {
        "run_id": run.run_id,
        "status": run.status.value,
        "transport": _transport.name,
        "handoffs": [
            {
                "index": h.index,
                "from_agent": h.from_agent.value,
                "to_agent": h.to_agent.value,
                "type": h.type.value,
                "summary": h.summary,
                "timestamp": h.timestamp,
                "virtual": _is_virtual(h),
            }
            for h in run.handoffs
        ],
        "veto_loop": _veto_loop(run),
        "artifacts": _build_artifacts(run),
    }


def _sse_payloads(run: WorkflowRun) -> list[dict]:
    events = [{"event_type": ev.event_type, **ev.data} for ev in run.audit_events]
    events.append({"event_type": "stream_end", "run_id": run.run_id})
    return events


@app.get("/workflow/{run_id}/events")
async def get_events(run_id: str) -> StreamingResponse:
    run = _require_run(run_id)

    async def _gen() -> AsyncIterator[str]:
        for payload in _sse_payloads(run):
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(_gen(), media_type="text/event-stream")
