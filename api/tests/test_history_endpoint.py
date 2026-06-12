"""
GET /workflow/{run_id}/history — the canonical coordination history the demo
shell renders. Must expose the 8-step order, the veto loop indices, and the
virtual flag without leaking transport internals.
"""
import pytest
from fastapi import HTTPException

import app.main as main
from app.models import WorkflowRun
from app.models.contracts import UserConcern

EXPECTED_ORDER = [
    "evidence", "campaign", "safety", "campaign",
    "safety", "outreach", "coordinator", "reporter",
]


@pytest.mark.asyncio
async def test_history_endpoint_returns_canonical_run():
    concern = UserConcern(
        text=(
            "Restaurant X claims 100% compostable packaging, "
            "but local waste systems do not process it."
        ),
        location="Local city",
        category="greenwashing",
    )
    run = WorkflowRun(concern=concern)
    main._runs[run.run_id] = await main.runner.run(run)

    data = await main.get_history(run.run_id)

    assert data["run_id"] == run.run_id
    assert data["transport"] in ("local", "band")
    assert [h["from_agent"] for h in data["handoffs"]] == EXPECTED_ORDER
    assert [h["index"] for h in data["handoffs"]] == list(range(8))

    veto = data["veto_loop"]
    assert veto["observed"] is True
    assert veto["veto_index"] is not None and veto["approved_index"] is not None
    assert veto["veto_index"] < veto["approved_index"]

    for h in data["handoffs"]:
        assert h["summary"] and h["timestamp"]
        assert isinstance(h["virtual"], bool)


@pytest.mark.asyncio
async def test_history_endpoint_404_for_unknown_run():
    with pytest.raises(HTTPException) as exc:
        await main.get_history("no-such-run")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_history_artifacts_derive_from_real_payloads():
    """artifacts must come from handoff payloads — no copy hardcoded in the API."""
    concern = UserConcern(
        text=(
            "Cafe Verde advertises zero-waste cups but ships them "
            "to a landfill-only district."
        ),
        location="Other city",
        category="greenwashing",
    )
    run = WorkflowRun(concern=concern)
    main._runs[run.run_id] = await main.runner.run(run)

    data = await main.get_history(run.run_id)

    assert "artifacts" in data
    artifacts = data["artifacts"]

    safety = artifacts["safety_review"]
    assert safety["veto_observed"] is True
    assert safety["approved"] is True
    assert safety["draft_text"] and safety["veto_reason"] and safety["rewritten_text"]
    assert safety["draft_text"] != safety["rewritten_text"]

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
