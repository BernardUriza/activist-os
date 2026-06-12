"""
Transport contract smoke — the same workflow must run on LocalTransport and
BandTransport and produce an equivalent coordination history.

The contract every transport must satisfy:
  - the run completes
  - at least one SAFETY_VETO handoff occurs, followed later by SAFETY_APPROVED
  - the exact from_agent order is:
      evidence, campaign, safety, campaign, safety, outreach, coordinator, reporter

BandTransport is exercised offline against a fake Band REST client (drop-in
proof, no network). The real-Band smoke is opt-in via RUN_BAND_SMOKE=1.
"""
from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from app.models import AgentName, HandoffType, WorkflowRun, WorkflowStatus
from app.models.contracts import UserConcern
from app.runner.transports import (
    BandTransport,
    BandTransportError,
    LocalTransport,
    create_transport,
)
from app.runner.workflow_runner import WorkflowRunner

EXPECTED_FROM_ORDER = [
    AgentName.EVIDENCE,
    AgentName.CAMPAIGN,
    AgentName.SAFETY,
    AgentName.CAMPAIGN,
    AgentName.SAFETY,
    AgentName.OUTREACH,
    AgentName.COORDINATOR,
    AgentName.REPORTER,
]

AGENT_NAMES = ["evidence", "campaign", "safety", "outreach", "coordinator", "reporter"]


def make_concern() -> UserConcern:
    return UserConcern(
        text=(
            "Restaurant X claims 100% compostable packaging, "
            "but local waste systems do not process it."
        ),
        location="Local city",
        category="greenwashing",
    )


async def run_workflow(transport):
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=make_concern())
    result = await runner.run(run)
    handoffs = await transport.get_handoffs(result.run_id)
    return result, handoffs


def assert_coordination_contract(result, handoffs):
    assert result.status == WorkflowStatus.COMPLETED, (
        f"Run status: {result.status}, error: {result.error}"
    )
    types = [h.type for h in handoffs]
    assert HandoffType.SAFETY_VETO in types, "Coordination history must contain a Safety VETO"
    veto_idx = types.index(HandoffType.SAFETY_VETO)
    assert HandoffType.SAFETY_APPROVED in types[veto_idx + 1:], (
        "Safety APPROVED must come after the veto"
    )
    assert [h.from_agent for h in handoffs] == EXPECTED_FROM_ORDER, (
        f"Agent order broke the contract: {[h.from_agent.value for h in handoffs]}"
    )


# ── Fake Band REST client (offline drop-in proof) ──────────────────────────


class FakeBandStore:
    """Enforces the real platform cap: 5 participants per room (owner included)."""

    MAX_PARTICIPANTS = 5

    def __init__(self) -> None:
        self.next_room = 0
        self.next_msg = 0
        self.rooms: list[tuple[str, str]] = []  # (api_key, chat_id)
        self.participants: list[tuple[str, str, str]] = []  # (api_key, chat_id, participant_id)
        self.messages: list[SimpleNamespace] = []
        self.events: list[SimpleNamespace] = []

    def room_size(self, chat_id: str) -> int:
        # the owner counts as the first participant
        return 1 + sum(1 for p in self.participants if p[1] == chat_id)


class FakeBandClient:
    """Mimics the thenvoi_rest AsyncRestClient surface BandTransport touches."""

    def __init__(self, api_key: str, store: FakeBandStore) -> None:
        async def create_agent_chat(*, chat):
            store.next_room += 1
            chat_id = f"room-{store.next_room}"
            store.rooms.append((api_key, chat_id))
            return SimpleNamespace(data=SimpleNamespace(id=chat_id))

        async def add_agent_chat_participant(chat_id, *, participant):
            if store.room_size(chat_id) >= store.MAX_PARTICIPANTS:
                raise RuntimeError(
                    "403 limit_reached: max_chat_room_participants=5"
                )
            store.participants.append((api_key, chat_id, participant.participant_id))
            return SimpleNamespace(data=None)

        async def create_agent_chat_message(chat_id, *, message):
            store.next_msg += 1
            msg_id = f"msg-{store.next_msg}"
            store.messages.append(SimpleNamespace(
                api_key=api_key, chat_id=chat_id, id=msg_id,
                content=message.content, mentions=message.mentions,
            ))
            return SimpleNamespace(data=SimpleNamespace(id=msg_id, recipients=[], success=True))

        async def create_agent_chat_event(chat_id, *, event):
            store.events.append(SimpleNamespace(
                api_key=api_key, chat_id=chat_id,
                content=event.content, message_type=event.message_type,
            ))
            return SimpleNamespace(data=None)

        self.agent_api_chats = SimpleNamespace(create_agent_chat=create_agent_chat)
        self.agent_api_participants = SimpleNamespace(
            add_agent_chat_participant=add_agent_chat_participant)
        self.agent_api_messages = SimpleNamespace(
            create_agent_chat_message=create_agent_chat_message)
        self.agent_api_events = SimpleNamespace(
            create_agent_chat_event=create_agent_chat_event)


@pytest.fixture
def fake_config(tmp_path):
    lines = []
    for name in AGENT_NAMES:
        lines.append(f'{name}:\n  agent_id: "id-{name}"\n  api_key: "key-{name}"\n')
    path = tmp_path / "agent_config.yaml"
    path.write_text("".join(lines))
    return path


@pytest.fixture
def fake_band(fake_config):
    store = FakeBandStore()
    transport = BandTransport(
        config_path=fake_config,
        client_factory=lambda api_key: FakeBandClient(api_key, store),
    )
    return transport, store


# ── The contract, per transport ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_local_transport_meets_contract():
    result, handoffs = await run_workflow(LocalTransport())
    assert_coordination_contract(result, handoffs)


@pytest.mark.asyncio
async def test_band_transport_meets_contract(fake_band):
    transport, _ = fake_band
    result, handoffs = await run_workflow(transport)
    assert_coordination_contract(result, handoffs)


@pytest.mark.asyncio
async def test_band_publishes_coordination_history(fake_band):
    transport, store = fake_band
    result, handoffs = await run_workflow(transport)

    # One room per run, every handoff stamped with it
    assert len(store.rooms) == 1
    room_id = store.rooms[0][1]
    assert all(h.metadata.band_room_id == room_id for h in handoffs)

    # 4 agents recruited — reporter is virtual, so the room stays at the 5-seat cap
    assert {p[2] for p in store.participants} == {
        f"id-{n}" for n in AGENT_NAMES if n not in ("evidence", "reporter")
    }

    # Handoffs between room participants ride as @mention messages AS the from_agent
    virtual = {"reporter", "system"}
    sent = {m.id: m for m in store.messages}
    for h in handoffs:
        if h.from_agent.value in virtual or h.to_agent.value in virtual:
            continue
        assert h.metadata.band_message_id in sent, f"{h.type} never reached Band"
        msg = sent[h.metadata.band_message_id]
        assert msg.api_key == f"key-{h.from_agent.value}", "sender identity mismatch"
        assert len(msg.mentions) >= 1
        assert msg.mentions[0].id == f"id-{h.to_agent.value}"

    # The veto is visible in the room history, sent by Safety
    veto_msgs = [m for m in store.messages if "SAFETY_VETO" in m.content]
    assert veto_msgs and all(m.api_key == "key-safety" for m in veto_msgs)

    # Virtual-reporter legs land as task events: coordinator→reporter and reporter→system
    task_events = [e for e in store.events if e.message_type == "task"]
    assert any("TASKS_READY" in e.content and "reporter" in e.content for e in task_events)
    assert any("PACKET_READY" in e.content for e in task_events)


@pytest.mark.asyncio
async def test_band_virtual_reporter_not_added_as_participant(fake_band):
    transport, store = fake_band
    result, handoffs = await run_workflow(transport)

    assert all(p[2] != "id-reporter" for p in store.participants), (
        "virtual reporter must never be added to the Band room"
    )
    assert store.room_size(store.rooms[0][1]) <= store.MAX_PARTICIPANTS
    # ...but the canonical history still ends with the reporter handoff
    assert handoffs[-1].from_agent == AgentName.REPORTER


@pytest.mark.asyncio
async def test_local_and_band_histories_equivalent(fake_band):
    transport, _ = fake_band
    _, local_handoffs = await run_workflow(LocalTransport())
    _, band_handoffs = await run_workflow(transport)

    signature = lambda hs: [(h.from_agent, h.to_agent, h.type) for h in hs]  # noqa: E731
    assert signature(local_handoffs) == signature(band_handoffs)


# ── Config switch + failure traceability ───────────────────────────────────


def test_create_transport_switch(monkeypatch, fake_config):
    monkeypatch.setenv("TRANSPORT", "local")
    assert isinstance(create_transport(), LocalTransport)

    monkeypatch.setenv("TRANSPORT", "band")
    monkeypatch.setenv("AGENT_CONFIG_PATH", str(fake_config))
    assert isinstance(create_transport(), BandTransport)

    monkeypatch.setenv("TRANSPORT", "carrier-pigeon")
    with pytest.raises(ValueError, match="carrier-pigeon"):
        create_transport()


def test_band_missing_config_error_is_traceable(tmp_path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(BandTransportError, match=str(missing)):
        BandTransport(config_path=missing)


# ── Real Band smoke (network) — opt-in ─────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.getenv("RUN_BAND_SMOKE") != "1",
    reason="real Band smoke is network-bound — set RUN_BAND_SMOKE=1 to run",
)
async def test_real_band_smoke():
    result, handoffs = await run_workflow(BandTransport())
    assert_coordination_contract(result, handoffs)
    assert all(h.metadata.band_room_id for h in handoffs), (
        "every handoff must carry the real Band room id"
    )
