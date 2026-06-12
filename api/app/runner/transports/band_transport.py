"""
BandTransport — publishes the coordination history to a Band chat room.

One room per workflow run. Every handoff is sent AS the from_agent
(authenticated with that agent's Band API key) and @mentions the to_agent,
so the room history at app.band.ai shows the real agent-to-agent exchange —
including the CAMPAIGN ⇄ SAFETY veto loop.

Primitive mapping (from .claude/rules/band.md):
  room per run            → agent_api_chats.create_agent_chat
  typed message + mention → agent_api_messages.create_agent_chat_message
  audit events            → agent_api_events.create_agent_chat_event
  recruit agents to room  → agent_api_participants.add_agent_chat_participant

Local mirrors of handoffs/events/context are kept in-process so subscribe()
and the SSE endpoint behave exactly like LocalTransport (drop-in contract).
Band's /context endpoint is read-only room context, so set_context persists
locally; the authoritative coordination history lives in the Band room.

Credentials come from agent_config.yaml (path overridable via
AGENT_CONFIG_PATH) — agent IDs are never hardcoded here.
"""
from __future__ import annotations

import asyncio
import os
from collections import defaultdict
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

from app.models import AgentHandoff, AuditEvent, EventType
from .base import Transport

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "agent_config.yaml"
# The thenvoi_rest DEFAULT environment points at a dev host that does not even
# resolve; the band SDK itself always passes the platform URL explicitly.
DEFAULT_REST_URL = "https://app.band.ai"
# Band caps rooms at 5 participants on the current plan; Reporter rides as a
# virtual/backend agent by default — its handoffs land as room events, so the
# canonical 8-step coordination history survives the cap. Override with
# BAND_VIRTUAL_AGENTS (comma-separated, empty string = everyone is real).
DEFAULT_VIRTUAL_AGENTS = "reporter"


class BandTransportError(RuntimeError):
    """Band coordination failed — the message says what, where, and for which run."""


def _default_client_factory(api_key: str):
    try:
        from thenvoi_rest import AsyncRestClient
    except ImportError as exc:  # pragma: no cover
        raise BandTransportError(
            "Band SDK not installed — run: pip install 'band-sdk[anthropic]' "
            "(BandTransport needs the thenvoi_rest client it bundles)"
        ) from exc
    return AsyncRestClient(
        api_key=api_key,
        base_url=os.getenv("BAND_REST_URL", DEFAULT_REST_URL),
    )


class BandTransport(Transport):

    def __init__(
        self,
        config_path: str | Path | None = None,
        client_factory: Callable[[str], Any] | None = None,
        virtual_agents: set[str] | None = None,
    ) -> None:
        self._config_path = Path(
            config_path or os.getenv("AGENT_CONFIG_PATH") or DEFAULT_CONFIG_PATH
        )
        self._client_factory = client_factory or _default_client_factory
        self._agents = self._load_agent_config(self._config_path)
        if virtual_agents is None:
            raw = os.getenv("BAND_VIRTUAL_AGENTS", DEFAULT_VIRTUAL_AGENTS)
            virtual_agents = {name.strip() for name in raw.split(",") if name.strip()}
        self._virtual_agents = virtual_agents
        self.virtual_agents = frozenset(virtual_agents)
        # Room creator: first configured agent that actually joins the room
        try:
            self._owner_agent = next(
                name for name in self._agents if name not in self._virtual_agents
            )
        except StopIteration:
            raise BandTransportError(
                f"All agents in {self._config_path} are marked virtual "
                "(BAND_VIRTUAL_AGENTS) — at least one must join the Band room"
            ) from None
        self._clients: dict[str, Any] = {}
        # Same in-process bookkeeping as LocalTransport (drop-in contract)
        self._handoffs: dict[str, list[AgentHandoff]] = defaultdict(list)
        self._events: dict[str, list[AuditEvent]] = defaultdict(list)
        self._context: dict[str, dict] = {}
        self._queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        # run_id → Band chat room id
        self._rooms: dict[str, str] = {}
        self._room_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    @staticmethod
    def _load_agent_config(path: Path) -> dict[str, dict]:
        if not path.exists():
            raise BandTransportError(
                f"Band agent config not found at {path} — register the agents at "
                "app.band.ai/agents and write agent_config.yaml (see .claude/rules/band.md), "
                "or point AGENT_CONFIG_PATH at it"
            )
        import yaml

        raw = yaml.safe_load(path.read_text()) or {}
        agents: dict[str, dict] = {}
        for name, creds in raw.items():
            if not isinstance(creds, dict) or "agent_id" not in creds or "api_key" not in creds:
                raise BandTransportError(
                    f"agent_config.yaml entry '{name}' is missing agent_id/api_key ({path})"
                )
            agents[name] = {"agent_id": creds["agent_id"], "api_key": creds["api_key"]}
        if not agents:
            raise BandTransportError(f"agent_config.yaml at {path} defines no agents")
        return agents

    def _client(self, agent_name: str) -> Any:
        if agent_name not in self._clients:
            self._clients[agent_name] = self._client_factory(self._agents[agent_name]["api_key"])
        return self._clients[agent_name]

    async def _ensure_room(self, run_id: str) -> str:
        async with self._room_locks[run_id]:
            if run_id in self._rooms:
                return self._rooms[run_id]
            from thenvoi_rest import ChatRoomRequest, ParticipantRequest

            owner_client = self._client(self._owner_agent)
            try:
                resp = await owner_client.agent_api_chats.create_agent_chat(chat=ChatRoomRequest())
                chat_id = resp.data.id
            except Exception as exc:
                raise BandTransportError(
                    f"Band room creation failed for run {run_id} "
                    f"(as agent '{self._owner_agent}'): {type(exc).__name__}: {exc}"
                ) from exc
            for name, creds in self._agents.items():
                if name == self._owner_agent or name in self._virtual_agents:
                    continue
                try:
                    await owner_client.agent_api_participants.add_agent_chat_participant(
                        chat_id, participant=ParticipantRequest(participant_id=creds["agent_id"])
                    )
                except Exception as exc:
                    raise BandTransportError(
                        f"Band add-participant '{name}' to room {chat_id} failed "
                        f"(run {run_id}): {type(exc).__name__}: {exc}"
                    ) from exc
            self._rooms[run_id] = chat_id
            return chat_id

    async def send_handoff(self, handoff: AgentHandoff) -> None:
        from thenvoi_rest import ChatEventRequest, ChatMessageRequest, ChatMessageRequestMentionsItem

        chat_id = await self._ensure_room(handoff.run_id)
        sender = handoff.from_agent.value
        recipient = handoff.to_agent.value
        if sender not in self._agents and sender not in self._virtual_agents:
            raise BandTransportError(
                f"Handoff from '{sender}' has no Band identity in {self._config_path} "
                f"(run {handoff.run_id})"
            )
        sender_in_room = sender in self._agents and sender not in self._virtual_agents
        recipient_in_room = recipient in self._agents and recipient not in self._virtual_agents
        body = handoff.model_dump_json(include={"handoff_id", "run_id", "type", "payload"})

        try:
            if sender_in_room and recipient_in_room:
                display = recipient.capitalize()
                resp = await self._client(sender).agent_api_messages.create_agent_chat_message(
                    chat_id,
                    message=ChatMessageRequest(
                        content=f"@{display} {handoff.type.value.upper()}\n{body}",
                        mentions=[
                            ChatMessageRequestMentionsItem(
                                id=self._agents[recipient]["agent_id"],
                                name=display,
                            )
                        ],
                    ),
                )
                handoff.metadata.band_message_id = resp.data.id
            else:
                # Virtual agents and SYSTEM are not room participants — their
                # handoffs land as task events (no mention needed), posted by
                # the sender if it sits in the room, else by the room owner.
                poster = sender if sender_in_room else self._owner_agent
                await self._client(poster).agent_api_events.create_agent_chat_event(
                    chat_id,
                    event=ChatEventRequest(
                        content=f"{sender} → {recipient} {handoff.type.value.upper()}\n{body}",
                        message_type="task",
                    ),
                )
        except BandTransportError:
            raise
        except Exception as exc:
            raise BandTransportError(
                f"Band send failed: {sender} → {recipient} ({handoff.type.value}) "
                f"in room {chat_id}, run {handoff.run_id}: {type(exc).__name__}: {exc}"
            ) from exc

        handoff.metadata.band_room_id = chat_id
        self._handoffs[handoff.run_id].append(handoff)
        await self._queues[handoff.run_id].put(handoff)

    async def subscribe(self, run_id: str) -> AsyncIterator[AgentHandoff]:
        q = self._queues[run_id]
        for h in self._handoffs[run_id]:
            yield h
        while True:
            handoff = await q.get()
            yield handoff

    async def get_handoffs(self, run_id: str) -> list[AgentHandoff]:
        return list(self._handoffs[run_id])

    async def record_event(self, event: AuditEvent) -> None:
        from thenvoi_rest import ChatEventRequest

        self._events[event.run_id].append(event)
        chat_id = await self._ensure_room(event.run_id)
        sender = event.agent.value
        if sender not in self._agents or sender in self._virtual_agents:
            sender = self._owner_agent
        message_type = "error" if event.event_type == EventType.ERROR else "thought"
        try:
            await self._client(sender).agent_api_events.create_agent_chat_event(
                chat_id,
                event=ChatEventRequest(
                    content=f"[{event.event_type.value}] {event.summary}",
                    message_type=message_type,
                ),
            )
        except Exception as exc:
            raise BandTransportError(
                f"Band event publish failed ({event.event_type.value}, agent '{sender}') "
                f"in room {chat_id}, run {event.run_id}: {type(exc).__name__}: {exc}"
            ) from exc

    async def get_events(self, run_id: str) -> list[AuditEvent]:
        return list(self._events[run_id])

    async def get_context(self, run_id: str) -> dict:
        return self._context.get(run_id, {})

    async def set_context(self, run_id: str, context: dict) -> None:
        self._context[run_id] = context
