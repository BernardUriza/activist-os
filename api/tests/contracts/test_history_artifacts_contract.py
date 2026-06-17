"""
History-artifacts contract — ``GET /workflow/{run_id}/history`` — lifted from the
old standalone's ``test_history_endpoint.py`` and re-authored as a BLACK-BOX HTTP
contract against the canonical build. See ``docs/CANONICAL_CONTRACT.md`` §4–5.

The history is the coordination record the demo shell renders. It must expose the
8-step order, the veto-loop indices, the per-handoff ``virtual`` flag, and the
demo artifacts — all DERIVED from the recorded handoff payloads, never hardcoded
in the API. Unknown runs get a ``404`` (same contract as ``/events``).

RED until Step 3 wires the ``/workflow/*`` routes + the artifact builder.
"""
from __future__ import annotations

import httpx
import pytest

import app.main as main

pytestmark = pytest.mark.contract

EXPECTED_ORDER = [
    "evidence", "campaign", "safety", "campaign",
    "safety", "outreach", "coordinator", "reporter",
]


def _client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=main.app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def _start_and_get_history(client: httpx.AsyncClient, concern: str) -> dict:
    res = await client.post("/workflow/start", json={"concern": concern})
    assert res.status_code == 202
    run_id = res.json()["run_id"]
    res = await client.get(f"/workflow/{run_id}/history")
    assert res.status_code == 200
    data = res.json()
    assert data["run_id"] == run_id
    return data


async def test_history_returns_the_canonical_eight_step_run():
    async with _client() as client:
        data = await _start_and_get_history(
            client,
            "Restaurant X claims 100% compostable packaging, "
            "but local waste systems do not process it.",
        )

    assert data["transport"] in ("local", "band")
    assert [h["from_agent"] for h in data["handoffs"]] == EXPECTED_ORDER
    assert [h["index"] for h in data["handoffs"]] == list(range(8))

    for h in data["handoffs"]:
        assert h["summary"] and h["timestamp"]
        assert isinstance(h["virtual"], bool)


async def test_history_exposes_the_veto_loop():
    async with _client() as client:
        data = await _start_and_get_history(
            client, "Brand Y markets diesel routes as carbon neutral."
        )

    veto = data["veto_loop"]
    assert veto["observed"] is True
    assert veto["veto_index"] is not None and veto["approved_index"] is not None
    assert veto["veto_index"] < veto["approved_index"]


async def test_history_artifacts_derive_from_real_payloads():
    """artifacts must come from handoff payloads — no copy hardcoded in the API."""
    async with _client() as client:
        data = await _start_and_get_history(
            client,
            "Cafe Verde advertises zero-waste cups but ships them "
            "to a landfill-only district.",
        )

    artifacts = data["artifacts"]

    safety = artifacts["safety_review"]
    assert safety["veto_observed"] is True
    assert safety["approved"] is True
    assert safety["draft_text"] and safety["veto_reason"] and safety["rewritten_text"]
    assert safety["draft_text"] != safety["rewritten_text"], (
        "the rewrite must differ from the vetoed draft"
    )

    evidence = artifacts["evidence_brief"]
    assert evidence["claims_count"] >= 1
    assert evidence["sources_count"] >= 1
    assert evidence["title"] and evidence["summary"]

    packet = artifacts["campaign_packet"]
    assert isinstance(packet["reporter_virtual"], bool)
    assert packet["outreach_assets_count"] >= 1
    assert packet["volunteer_tasks_count"] >= 1
    assert packet["provenance_items_count"] >= 1
    assert packet["title"] and packet["summary"]


async def test_history_404_for_unknown_run():
    async with _client() as client:
        res = await client.get("/workflow/no-such-run/history")
    assert res.status_code == 404


async def test_history_omits_band_block_for_local_transport():
    """The default (local) demo run must NOT carry a band provenance block."""
    async with _client() as client:
        data = await _start_and_get_history(
            client, "Local Co overstates recycling rates in its annual report."
        )

    assert data["transport"] == "local"
    assert data.get("band") is None


async def test_history_exposes_band_provenance_when_transport_is_band(band_app):
    """transport=band → /history carries room_id + real message/virtual counts,
    DERIVED from the run state (band_message_id / virtual flags), never hardcoded."""
    async with _client() as client:
        data = await _start_and_get_history(
            client, "Brand Z labels diesel freight as carbon neutral."
        )

    assert data["transport"] == "band"
    band = data["band"]
    assert band["room_id"] and band["room_id"] == band_app.rooms[0][1]
    assert band["messages_sent"] == 6
    assert band["virtual_events"] == 2
    assert band["messages_sent"] + band["virtual_events"] == len(data["handoffs"])
