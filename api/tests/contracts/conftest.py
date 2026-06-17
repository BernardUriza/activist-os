"""Shared contract-test fixtures.

``band_app`` swaps the live ``app.main`` transport for a BandTransport backed by
an offline fake Band REST client, so black-box HTTP tests can exercise the
``transport=band`` branch (e.g. the ``/history`` ``band`` provenance block)
without a network or real credentials.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import app.main as main
from app.transports import BandTransport
from app.workflow_runner import WorkflowRunner

AGENT_NAMES = ["evidence", "campaign", "safety", "outreach", "coordinator", "reporter"]


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
def band_app(tmp_path, monkeypatch):
    lines = [f'{n}:\n  agent_id: "id-{n}"\n  api_key: "key-{n}"\n' for n in AGENT_NAMES]
    cfg = tmp_path / "agent_config.yaml"
    cfg.write_text("".join(lines))

    store = FakeBandStore()
    transport = BandTransport(
        config_path=cfg,
        client_factory=lambda api_key: FakeBandClient(api_key, store),
    )
    monkeypatch.setattr(main, "_transport", transport)
    monkeypatch.setattr(main, "_runner", WorkflowRunner(transport))
    return store
