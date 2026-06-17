"""
Band room-reuse contract — Paso 8A.

The default ``create_per_run`` strategy mints one Band room per workflow run.
On a capped account that exhausts ``max_chat_rooms`` before the judges ever run
the demo. ``reuse_single`` keeps a single stable room alive across many runs:
it creates NO room and NO participants, sends the 6 real @mention messages and
2 virtual backend events into ``BAND_REUSE_ROOM_ID``, and stamps that same id on
every handoff (so ``/history.band.room_id`` is honest). Messages carry a
``[run <short>]`` prefix so concurrent runs don't blur together in one room.

The canonical 8-handoff order and the veto loop are UNCHANGED — reuse only
swaps room provisioning, never the coordination contract.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.contracts import UserConcern
from app.models import AgentName, WorkflowRun, WorkflowStatus
from app.transports import BandTransport, BandTransportError, LocalTransport
from app.workflow_runner import WorkflowRunner

pytestmark = pytest.mark.contract

AGENT_NAMES = ["evidence", "campaign", "safety", "outreach", "coordinator", "reporter"]
REUSE_ROOM_ID = "stable-room-abc123"


class FakeBandStore:
    MAX_PARTICIPANTS = 5

    def __init__(self) -> None:
        self.next_room = 0
        self.next_msg = 0
        self.rooms: list[tuple[str, str]] = []
        self.participants: list[tuple[str, str, str]] = []
        self.messages: list[SimpleNamespace] = []
        self.events: list[SimpleNamespace] = []

    def room_size(self, chat_id: str) -> int:
        return 1 + sum(1 for p in self.participants if p[1] == chat_id)


class FakeBandClient:
    def __init__(self, api_key: str, store: FakeBandStore) -> None:
        async def create_agent_chat(*, chat):
            store.next_room += 1
            chat_id = f"room-{store.next_room}"
            store.rooms.append((api_key, chat_id))
            return SimpleNamespace(data=SimpleNamespace(id=chat_id))

        async def add_agent_chat_participant(chat_id, *, participant):
            if store.room_size(chat_id) >= store.MAX_PARTICIPANTS:
                raise RuntimeError("403 limit_reached: max_chat_room_participants=5")
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
    lines = [f'{n}:\n  agent_id: "id-{n}"\n  api_key: "key-{n}"\n' for n in AGENT_NAMES]
    path = tmp_path / "agent_config.yaml"
    path.write_text("".join(lines))
    return path


def _make_transport(fake_config, store, **kwargs):
    return BandTransport(
        config_path=fake_config,
        client_factory=lambda api_key: FakeBandClient(api_key, store),
        **kwargs,
    )


def make_concern() -> UserConcern:
    return UserConcern(
        text="Restaurant X claims 100% compostable packaging, "
             "but local waste systems do not process it.",
        location="Local city",
        category="greenwashing",
    )


async def run_workflow(transport):
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=make_concern())
    result = await runner.run(run)
    handoffs = await transport.get_handoffs(result.run_id)
    return result, handoffs


# 1. default create_per_run crea room
async def test_default_strategy_creates_one_room(fake_config):
    store = FakeBandStore()
    transport = _make_transport(fake_config, store)
    result, handoffs = await run_workflow(transport)

    assert result.status == WorkflowStatus.COMPLETED
    assert len(store.rooms) == 1
    assert all(h.metadata.band_room_id == store.rooms[0][1] for h in handoffs)


# 2. reuse_single NO crea room
async def test_reuse_single_creates_no_room(fake_config):
    store = FakeBandStore()
    transport = _make_transport(
        fake_config, store, room_strategy="reuse_single", reuse_room_id=REUSE_ROOM_ID
    )
    result, handoffs = await run_workflow(transport)

    assert result.status == WorkflowStatus.COMPLETED
    assert store.rooms == [], "reuse_single must never create a Band room"
    assert all(h.metadata.band_room_id == REUSE_ROOM_ID for h in handoffs)


# 3. reuse_single NO crea participants
async def test_reuse_single_creates_no_participants(fake_config):
    store = FakeBandStore()
    transport = _make_transport(
        fake_config, store, room_strategy="reuse_single", reuse_room_id=REUSE_ROOM_ID
    )
    await run_workflow(transport)

    assert store.participants == [], "reuse_single must never seat participants"


# 4. reuse_single envía 6 messages al room_id configurado
async def test_reuse_single_sends_six_messages_to_configured_room(fake_config):
    store = FakeBandStore()
    transport = _make_transport(
        fake_config, store, room_strategy="reuse_single", reuse_room_id=REUSE_ROOM_ID
    )
    await run_workflow(transport)

    assert len(store.messages) == 6
    assert all(m.chat_id == REUSE_ROOM_ID for m in store.messages)


# 5. reuse_single conserva 2 virtual events
async def test_reuse_single_keeps_two_virtual_events(fake_config):
    store = FakeBandStore()
    transport = _make_transport(
        fake_config, store, room_strategy="reuse_single", reuse_room_id=REUSE_ROOM_ID
    )
    await run_workflow(transport)

    task_events = [e for e in store.events if e.message_type == "task"]
    assert len(task_events) == 2
    assert all(e.chat_id == REUSE_ROOM_ID for e in store.events)


# 6. /history.band.room_id = BAND_REUSE_ROOM_ID
async def test_history_band_room_id_is_the_reused_room(band_reuse_app):
    import httpx

    import app.main as main

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/workflow/start",
            json={"concern": "Brand Z labels diesel freight as carbon neutral."},
        )
        run_id = res.json()["run_id"]
        data = (await client.get(f"/workflow/{run_id}/history")).json()

    assert data["transport"] == "band"
    assert data["band"]["room_id"] == band_reuse_app.reuse_room_id
    assert data["band"]["messages_sent"] == 6
    assert data["band"]["virtual_events"] == 2
    assert band_reuse_app.store.rooms == []


# 7. falta BAND_REUSE_ROOM_ID con reuse_single → error claro de configuración
def test_reuse_single_without_room_id_is_a_clear_config_error(fake_config):
    with pytest.raises(BandTransportError, match="BAND_REUSE_ROOM_ID"):
        BandTransport(config_path=fake_config, room_strategy="reuse_single")


def test_unknown_room_strategy_is_a_clear_config_error(fake_config):
    with pytest.raises(BandTransportError, match="carrier-pigeon"):
        BandTransport(config_path=fake_config, room_strategy="carrier-pigeon")


# 8. local transport intacto
async def test_local_transport_unaffected_by_strategy_env(monkeypatch):
    monkeypatch.setenv("BAND_ROOM_STRATEGY", "reuse_single")
    monkeypatch.setenv("BAND_REUSE_ROOM_ID", REUSE_ROOM_ID)
    result, handoffs = await run_workflow(LocalTransport())

    assert result.status == WorkflowStatus.COMPLETED
    assert all(h.metadata.band_room_id is None for h in handoffs)
    assert handoffs[-1].from_agent == AgentName.REPORTER


# criterio 6 — mensajes llevan run prefix
async def test_messages_carry_run_short_id_prefix(fake_config):
    store = FakeBandStore()
    transport = _make_transport(
        fake_config, store, room_strategy="reuse_single", reuse_room_id=REUSE_ROOM_ID
    )
    result, _ = await run_workflow(transport)

    prefix = f"[run {result.run_id[:8]}]"
    assert store.messages, "expected real @mention messages"
    assert all(m.content.startswith(prefix) for m in store.messages)
    assert all(e.content.startswith(prefix) for e in store.events)
