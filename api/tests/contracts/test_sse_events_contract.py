"""
SSE audit-stream contract — ``GET /workflow/{run_id}/events`` — lifted from the
old standalone's ``test_events_endpoint.py`` and re-authored as a BLACK-BOX HTTP
contract against the canonical build (no ``_runs`` internals; the new wiring is
re-authored per ``docs/REUSE_MAP.md`` bucket 3). See ``docs/CANONICAL_CONTRACT.md`` §3.

Invariants:
  - ``Content-Type: text/event-stream``
  - replays a completed run's recorded events; ``event_type`` includes
    ``workflow_started``, ``handoff_sent`` (×8) and ``workflow_completed``
  - the LAST event is always ``stream_end`` (the sentinel)
  - sequence shape: ``workflow_started → handoff_sent…(×8) → workflow_completed → stream_end``
  - unknown ``run_id`` → ``404`` (same contract as ``/history``)

RED until Step 3 wires the ``/workflow/*`` routes onto ``app.main``.
"""
from __future__ import annotations

import json

import httpx
import pytest

import app.main as main

pytestmark = pytest.mark.contract

EXPECTED_HANDOFF_COUNT = 8


def _client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=main.app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def _collect_stream(
    client: httpx.AsyncClient, run_id: str
) -> tuple[httpx.Response, list[dict]]:
    events: list[dict] = []
    async with client.stream("GET", f"/workflow/{run_id}/events") as res:
        async for line in res.aiter_lines():
            if line.startswith("data: "):
                events.append(json.loads(line[len("data: "):]))
        return res, events


async def _start_run(client: httpx.AsyncClient) -> str:
    res = await client.post(
        "/workflow/start",
        json={"concern": "Market Z sells 'local honey' imported in bulk."},
    )
    assert res.status_code == 202, f"start must accept the run (202), got {res.status_code}"
    return res.json()["run_id"]


async def test_events_stream_is_event_stream_and_terminates_with_sentinel():
    async with _client() as client:
        run_id = await _start_run(client)
        res, events = await _collect_stream(client, run_id)

    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]

    event_types = [e.get("event_type") for e in events]
    assert event_types[0] == "workflow_started"
    assert "handoff_sent" in event_types
    assert "workflow_completed" in event_types
    assert event_types[-1] == "stream_end", "the last event is always the stream_end sentinel"


async def test_events_stream_replays_the_full_eight_step_run():
    async with _client() as client:
        run_id = await _start_run(client)
        _, events = await _collect_stream(client, run_id)

    handoffs = [e for e in events if e.get("event_type") == "handoff_sent"]
    assert len(handoffs) == EXPECTED_HANDOFF_COUNT, (
        f"a complete run streams exactly {EXPECTED_HANDOFF_COUNT} handoff_sent events"
    )

    # workflow_completed precedes the sentinel; nothing rides after stream_end.
    types = [e.get("event_type") for e in events]
    assert types.index("workflow_completed") < types.index("stream_end")
    assert types.count("stream_end") == 1


async def test_events_404_for_unknown_run():
    async with _client() as client:
        res = await client.get("/workflow/no-such-run/events")
    assert res.status_code == 404
