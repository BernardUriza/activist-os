# ADR — Activist OS as fi-glass canary (completed)

Status: **DONE** — `useActivistAgent` + `AgentConversationSurface` live and deployed.
Primary surface: `https://proud-stone-023fae70f.7.azurestaticapps.net/app`

## Decision

Activist OS is a **governed multi-agent workflow** canary for fi-glass — a harder
bar than a conversational app. If fi-glass can render 8 agent handoffs with
explicit identity, a safety veto as a flow interruption, and mandatory revision
before approval, it works for real agentic use cases, not just chat.

## Architecture seam

`ChatMessage.role` is only `user | assistant`. All six-agent identity, @mention
targets, state tags, and severity ride in `metadata`. The `AgentConversationSurface`
render slots (`renderHeader`, `renderBadge`, `messageBubbleClassName`) read it.
No fi-glass fork required.

```ts
// metadata shape (AgentChatMetadata in web/lib/workflow-chat.ts)
{ agent, from, to, tag, virtual, index, severity: 'critical' | 'approved' | 'info' }
```

## Transport adapter

`useActivistAgent` (`web/lib/useActivistAgent.ts`) implements `AgentHook`:
- `send(concern)` → `POST /workflow/start` → opens SSE → on `stream_end` fetches `/history`
- Exposes `messages: ChatMessage[]` (mapped by `workflow-chat.ts`) + `history` for the artifacts rail
- Uses fi-glass ≥1.2.0 `externalMessages` controlled mode — the hook owns the thread, fi-glass renders verbatim

The backend is unchanged: `/workflow/start` + `/workflow/{id}/events` (SSE) +
`/workflow/{id}/history`. No `/chat/stream` adapter needed.

## Canary-driven upstream fix (fi-glass 1.2.0)

The original fold of `1 send → 1 turn` couldn't express 8 agent messages per
concern. Rather than hack the consumer, `useAgentConversation` gained
`externalMessages?: ChatMessage[]` — controlled mode. Activist OS surfaced the
need; fi-glass 1.2.0 shipped the fix. Consumer thinned, E2E green. See
[[framework-canary-consumer]] for the doctrine.

## What was resolved

| Finding | Status |
|---|---|
| Deploy used `app.app:app` (template chat face) | Fixed — `api/entrypoint.sh` runs `app.main:app` (commit `ff481ea`) |
| `useAgentConversation` couldn't model 1→8 messages | Fixed upstream in fi-glass 1.2.0 (`externalMessages`) |
| UI pivot gated on review | Done — `FiGlassPrimary` is the default `/app` surface (commit `54d59e2`) |
| `TRANSPORT=band` crashes on boot in Azure | Band agent config not resolved from `AGENT_CONFIG_YAML_B64` secret; deploy uses `TRANSPORT=local` pending that fix |
