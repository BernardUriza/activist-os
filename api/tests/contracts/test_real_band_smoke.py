"""Opt-in real-Band smoke — runs ONLY when Bernard enables it explicitly.

Default CI stays offline: this whole module skips unless ``RUN_BAND_SMOKE=1``
AND ``AGENT_CONFIG_PATH`` points at an existing config. When skipped it touches
no network and imports no SDK. Enable with:

    cd api
    RUN_BAND_SMOKE=1 TRANSPORT=band BAND_REST_URL=https://app.band.ai \\
      AGENT_CONFIG_PATH=/path/to/agent_config.yaml \\
      pytest tests/contracts/test_real_band_smoke.py -q

See docs/BAND_REAL_SMOKE.md.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

_CFG = os.getenv("AGENT_CONFIG_PATH", "")
_ENABLED = os.getenv("RUN_BAND_SMOKE") == "1" and bool(_CFG) and Path(_CFG).is_file()

pytestmark = [
    pytest.mark.contract,
    pytest.mark.skipif(
        not _ENABLED,
        reason="real Band smoke is opt-in: set RUN_BAND_SMOKE=1 + AGENT_CONFIG_PATH=<existing file>",
    ),
]


async def test_real_band_smoke_meets_the_canonical_contract():
    from app.contracts import UserConcern
    from app.models import HandoffType, WorkflowRun, WorkflowStatus
    from app.transports import BandTransport
    from app.workflow_runner import CANONICAL_FROM_ORDER, WorkflowRunner

    transport = BandTransport()  # real client_factory; reads BAND_REST_URL + config from env
    runner = WorkflowRunner(transport)
    run = WorkflowRun(
        concern=UserConcern(
            concern="Restaurant X claims 100% compostable packaging the city cannot process.",
        )
    )

    result = await runner.run(run)
    handoffs = await transport.get_handoffs(result.run_id)

    assert result.status == WorkflowStatus.COMPLETED
    assert [h.from_agent for h in handoffs] == CANONICAL_FROM_ORDER

    types = [h.type for h in handoffs]
    assert types.index(HandoffType.SAFETY_VETO) == 2
    assert types.index(HandoffType.SAFETY_APPROVED) == 4

    assert result.band_room_id, "the run must carry a real Band room id"
    for h in handoffs:
        assert h.metadata.band_room_id == result.band_room_id
        if h.is_virtual_leg:
            assert h.metadata.virtual is True
            assert h.metadata.band_message_id is None
            assert h.metadata.reason == "participant_limit_compat"
        else:
            assert h.metadata.band_message_id, f"{h.type} must get a real Band message id"

    # reporter / system never occupy a seat — they only ever appear as virtual legs.
    seated_touch = [
        h for h in handoffs
        if not h.is_virtual_leg and (
            h.from_agent.value in ("reporter", "system")
            or h.to_agent.value in ("reporter", "system")
        )
    ]
    assert not seated_touch


async def test_real_band_history_and_sse_contracts_hold():
    import httpx

    import app.main as main

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=main.app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/workflow/start",
            json={"concern": "Brand Y markets diesel routes as carbon neutral."},
        )
        assert res.status_code == 202
        run_id = res.json()["run_id"]

        hist = await client.get(f"/workflow/{run_id}/history")
        assert hist.status_code == 200
        data = hist.json()
        assert data["transport"] == "band"
        assert data["veto_loop"] == {"observed": True, "veto_index": 2, "approved_index": 4}
        assert data["artifacts"]["safety_review"]["veto_observed"] is True

        events: list[str] = []
        async with client.stream("GET", f"/workflow/{run_id}/events") as stream:
            async for line in stream.aiter_lines():
                if line.startswith("data: "):
                    events.append(line)
        assert events and '"stream_end"' in events[-1]
