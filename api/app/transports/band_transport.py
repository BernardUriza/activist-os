"""Band transport — one adapter, two client paths behind the same contract.

OFFLINE (default, CI): a fake client is injected via ``client_factory`` — pure
in-process, no network, no SDK. This is what the contract tests exercise.

REAL (opt-in): with no ``client_factory``, the real path lazily wraps the
``thenvoi_rest`` AsyncRestClient (pointed at ``BAND_REST_URL``) and only runs
when Bernard enables it explicitly (``RUN_BAND_SMOKE=1 TRANSPORT=band
AGENT_CONFIG_PATH=…``). Credentials come from the config file / env only — never
the repo. The real path imports the SDK lazily, so the offline path needs none.

Band semantics (identical on both paths):
  - one room per run (``band_room_id`` stamped on every handoff)
  - ``evidence`` owns/initiates; ``campaign, safety, outreach, coordinator`` are
    recruited → 5-seat cap (owner + 4)
  - ``reporter`` / ``system`` are VIRTUAL: never seated; their legs ride as task
    events (``metadata.virtual=True``, ``emitted_by``, ``reason``,
    ``band_message_id=None``)
  - non-virtual handoffs ride as @mention messages sent AS the from-agent,
    stamped with ``band_message_id``
"""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

from ..band_config import BandConfigError, load_agent_config, load_agent_config_from_b64
from ..models import AgentName, Handoff, WorkflowRun
from .base import TransportError

SEAT_CAP = 5
DEFAULT_REST_URL = "https://app.band.ai"

CREATE_PER_RUN = "create_per_run"
REUSE_SINGLE = "reuse_single"
ROOM_STRATEGIES = (CREATE_PER_RUN, REUSE_SINGLE)

OWNER = AgentName.EVIDENCE
SEATED = (AgentName.CAMPAIGN, AgentName.SAFETY, AgentName.OUTREACH, AgentName.COORDINATOR)


class BandTransportError(TransportError):
    """BandTransport could not be constructed or could not reach Band."""


def _real_band_client_factory(api_key: str) -> Any:
    """Wrap the real ``thenvoi_rest`` client behind the fake's duck-typed surface.

    The SDK (and its typed request models) are imported lazily so the offline
    path never touches them.
    """
    try:
        from thenvoi_rest import (
            AsyncRestClient,
            ChatEventRequest,
            ChatMessageRequest,
            ChatMessageRequestMentionsItem,
            ChatRoomRequest,
            ParticipantRequest,
        )
    except ImportError as exc:  # pragma: no cover - only on the real opt-in path
        raise BandTransportError(
            "Band SDK not installed — `pip install band-sdk` (thenvoi_rest) is "
            "required for the real Band path (RUN_BAND_SMOKE)"
        ) from exc

    client = AsyncRestClient(
        api_key=api_key,
        base_url=os.getenv("BAND_REST_URL", DEFAULT_REST_URL),
    )

    async def create_agent_chat(*, chat):
        return await client.agent_api_chats.create_agent_chat(chat=ChatRoomRequest())

    async def add_agent_chat_participant(chat_id, *, participant):
        return await client.agent_api_participants.add_agent_chat_participant(
            chat_id, participant=ParticipantRequest(participant_id=participant.participant_id)
        )

    async def create_agent_chat_message(chat_id, *, message):
        mentions = [
            ChatMessageRequestMentionsItem(id=m.id, name=getattr(m, "name", None))
            for m in message.mentions
        ]
        return await client.agent_api_messages.create_agent_chat_message(
            chat_id, message=ChatMessageRequest(content=message.content, mentions=mentions)
        )

    async def create_agent_chat_event(chat_id, *, event):
        return await client.agent_api_events.create_agent_chat_event(
            chat_id,
            event=ChatEventRequest(content=event.content, message_type=event.message_type),
        )

    return SimpleNamespace(
        agent_api_chats=SimpleNamespace(create_agent_chat=create_agent_chat),
        agent_api_participants=SimpleNamespace(
            add_agent_chat_participant=add_agent_chat_participant
        ),
        agent_api_messages=SimpleNamespace(create_agent_chat_message=create_agent_chat_message),
        agent_api_events=SimpleNamespace(create_agent_chat_event=create_agent_chat_event),
    )


class BandTransport:
    name = "band"

    def __init__(
        self,
        config_path: str | Path | None = None,
        client_factory: Callable[[str], object] | None = None,
        room_strategy: str | None = None,
        reuse_room_id: str | None = None,
    ) -> None:
        self._strategy = (room_strategy or os.getenv("BAND_ROOM_STRATEGY") or CREATE_PER_RUN).lower()
        self._reuse_room_id = (
            reuse_room_id if reuse_room_id is not None else os.getenv("BAND_REUSE_ROOM_ID", "")
        ).strip()
        if self._strategy not in ROOM_STRATEGIES:
            raise BandTransportError(
                f"unknown BAND_ROOM_STRATEGY={self._strategy!r} "
                f"(expected {CREATE_PER_RUN!r} or {REUSE_SINGLE!r})"
            )
        if self._strategy == REUSE_SINGLE and not self._reuse_room_id:
            raise BandTransportError(
                f"BAND_ROOM_STRATEGY={REUSE_SINGLE} requires BAND_REUSE_ROOM_ID "
                "(the stable Band room uuid to reuse across runs)"
            )
        env_path = os.getenv("AGENT_CONFIG_PATH", "")
        path = Path(config_path) if config_path else (Path(env_path) if env_path else None)
        b64 = os.getenv("AGENT_CONFIG_YAML_B64", "")
        try:
            if path is not None:
                self._configs = load_agent_config(path)
            elif b64:
                self._configs = load_agent_config_from_b64(b64)
            else:
                raise BandConfigError(
                    "no agent config: set AGENT_CONFIG_PATH (file) or AGENT_CONFIG_YAML_B64 (inline)"
                )
        except BandConfigError as exc:
            raise BandTransportError(str(exc)) from exc
        self._config_path = path
        self._client_factory = client_factory or _real_band_client_factory
        self._handoffs: dict[str, list[Handoff]] = {}
        self._room_id: str | None = None

    def _client_for(self, agent: AgentName) -> Any:
        return self._client_factory(self._configs[agent.value]["api_key"])

    def _agent_id(self, agent: AgentName) -> str:
        return self._configs[agent.value]["agent_id"]

    async def open(self, run: WorkflowRun) -> None:
        self._handoffs[run.run_id] = []
        if self._strategy == REUSE_SINGLE:
            self._room_id = self._reuse_room_id
            run.band_room_id = self._room_id
            return
        owner = self._client_for(OWNER)
        resp = await owner.agent_api_chats.create_agent_chat(
            chat=SimpleNamespace(title=f"Activist OS run {run.run_id}")
        )
        self._room_id = resp.data.id
        run.band_room_id = self._room_id
        for agent in SEATED:
            participant = SimpleNamespace(participant_id=self._agent_id(agent))
            await owner.agent_api_participants.add_agent_chat_participant(
                self._room_id, participant=participant
            )

    async def deliver(self, run: WorkflowRun, handoff: Handoff) -> Handoff:
        handoff.metadata.band_room_id = self._room_id
        handoff.metadata.seat_cap = SEAT_CAP
        prefix = f"[run {run.run_id[:8]}] "

        if handoff.is_virtual_leg:
            poster = handoff.from_agent if handoff.from_agent in SEATED else OWNER
            handoff.metadata.virtual = True
            handoff.metadata.emitted_by = poster.value
            handoff.metadata.reason = "participant_limit_compat"
            content = (
                f"{prefix}{handoff.type.name} from={handoff.from_agent.value} "
                f"to={handoff.to_agent.value}: {handoff.summary}"
            )
            await self._client_for(poster).agent_api_events.create_agent_chat_event(
                self._room_id,
                event=SimpleNamespace(content=content, message_type="task"),
            )
        else:
            mention = SimpleNamespace(
                id=self._agent_id(handoff.to_agent),
                name=handoff.to_agent.value.capitalize(),
            )
            message = SimpleNamespace(
                content=f"{prefix}{handoff.type.name}: {handoff.summary}",
                mentions=[mention],
            )
            resp = await self._client_for(handoff.from_agent).agent_api_messages.create_agent_chat_message(
                self._room_id, message=message
            )
            handoff.metadata.band_message_id = resp.data.id

        self._handoffs[run.run_id].append(handoff)
        return handoff

    async def get_handoffs(self, run_id: str) -> list[Handoff]:
        return list(self._handoffs.get(run_id, []))
