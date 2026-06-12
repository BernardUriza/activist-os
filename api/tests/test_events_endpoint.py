"""
GET /workflow/{run_id}/events — the SSE audit stream a live demo shell would
consume. Must speak text/event-stream over real HTTP, replay the events a
completed run already recorded (handoffs through WORKFLOW_COMPLETED), and
close with the stream_end sentinel. Unknown runs get a 404, same contract as
/history.
"""
import json

import httpx
import pytest

import app.main as main
from app.models import WorkflowRun
from app.models.contracts import UserConcern


def _client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=main.app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def _collect_stream(client: httpx.AsyncClient, run_id: str) -> tuple[httpx.Response, list[dict]]:
    events: list[dict] = []
    async with client.stream("GET", f"/workflow/{run_id}/events") as res:
        async for line in res.aiter_lines():
            if line.startswith("data: "):
                events.append(json.loads(line[len("data: "):]))
        return res, events


@pytest.mark.asyncio
async def test_events_stream_replays_completed_run():
    concern = UserConcern(
        text=(
            "Brand Y markets its delivery fleet as carbon neutral "
            "while running diesel-only routes."
        ),
        location="Local city",
        category="greenwashing",
    )
    run = WorkflowRun(concern=concern)
    main._runs[run.run_id] = await main.runner.run(run)

    async with _client() as client:
        res, events = await _collect_stream(client, run.run_id)

    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]

    event_types = [e.get("event_type") for e in events]
    assert "handoff_sent" in event_types
    assert "workflow_completed" in event_types
    assert event_types[-1] == "stream_end"

    # Replay is complete: every audit event the run recorded rides the stream.
    assert len(events) == len(main._runs[run.run_id].audit_events) + 1  # + stream_end


@pytest.mark.asyncio
async def test_events_stream_from_workflow_start():
    async with _client() as client:
        res = await client.post(
            "/workflow/start",
            json={"concern": "Market Z sells 'local honey' imported in bulk."},
        )
        assert res.status_code == 202
        run_id = res.json()["run_id"]

        res, events = await _collect_stream(client, run_id)

    assert res.status_code == 200
    event_types = [e.get("event_type") for e in events]
    assert event_types[0] == "workflow_started"
    assert "workflow_completed" in event_types
    assert event_types[-1] == "stream_end"


@pytest.mark.asyncio
async def test_events_404_for_unknown_run():
    async with _client() as client:
        res = await client.get("/workflow/no-such-run/events")
    assert res.status_code == 404
