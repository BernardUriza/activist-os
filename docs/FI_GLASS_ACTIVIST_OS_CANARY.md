# Activist OS — the high-stakes fi-glass canary

This document is the **adapter contract** for turning Activist OS into an
AgentChat-oriented experience on top of [`fi-glass`](https://www.npmjs.com/package/fi-glass),
without changing the canonical `/workflow` backend. It is written from the
**real, inspected** fi-glass / `@free-intelligence/core` exports — not assumptions.

Status: **canary adapter built + live-smoked (Paso 5B / 5B-S)**. The UI pivot has
NOT happened yet; `/app` is still the dashboard console and the fi-glass canary is
opt-in behind `/app?fi_glass_canary=1`. See [Live smoke findings](#live-smoke-findings).

## 1. Why Activist OS is a fi-glass canary

`og118` proves fi-glass on a **conversational** experience. Activist OS proves it
on a **governed multi-agent workflow** — a much harder bar. It forces fi-glass to
express things a linear chat never stresses:

1. Six agents with **semantic identity** (Evidence / Campaign / Safety / Outreach
   / Coordinator / Reporter), not just `user ↔ assistant`.
2. Explicit **handoffs** between agents, with **@mentions** (`Safety → Campaign`).
3. A **safety veto** as a flow interruption (not a tool error).
4. A **mandatory revision** before approval (the CAMPAIGN ⇄ SAFETY loop).
5. **Artifacts** attached to messages: evidence brief, safety review, campaign packet.
6. Visible **provenance**.
7. Honest **mock / live / deep-link** states.
8. **local / Band** transports with honest virtualization (a virtual reporter is
   marked virtual only when the real handoff says so).
9. **Human-in-the-loop**: the system assembles, it never publishes.

If fi-glass can render Activist OS, it works for real agentic workflows — not just
chat. That is the canary's value.

## 2. Real fi-glass exports (inspected, not assumed)

From `fi-glass/agent` (`dist/agent/index.d.ts`):

- `useAgentConversation(agent: AgentHook, options?: UseAgentConversationOptions): AgentConversation`
  — **the hook consumes an `AgentHook`, NOT a URL.** It is **not** hardcoded to
  `/chat/stream`. The app supplies the transport via the `AgentHook` it passes in.
  (The template's `useTemplateAgent` is one such `AgentHook`, wired to the
  template's `/chat/stream` — that is a template detail, not a fi-glass constraint.)
- `AgentConversationSurface({ conversation, renderHeader, renderBadge, renderActions, messageBubbleClassName, agentPanelProps, emptyState, aboveComposer, ... })`
  — the chat surface. Heavily slot-driven: `renderHeader(message)`, `renderBadge(message)`,
  `renderActions(message)`, and `messageBubbleClassName(message)` are **per-`ChatMessage`**,
  so agent identity, @mentions, state tags, and veto styling are all expressible.
- Also exports `AgentPanel` (Plan + Steps + Sources), `PlanChecklist`, `StepsPanel`,
  `SourcesPanel`, tool-classification helpers, and an injectable `AgentIconSet`.

From `@free-intelligence/core`:

```ts
interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';        // only two roles — agent identity goes in metadata
  content: string;
  thinking?: string | null;
  timestamp: string;
  metadata?: Record<string, unknown>; // ← the adapter seam
}

interface AgentHook {
  turn: AgentTurnState;
  isStreaming: boolean;
  send: (message: string, metadata?: object) => Promise<void>;
  abort?: () => void;
  reset?: () => void;
}
```

**The seam:** `ChatMessage.role` is only `user | assistant`. The six-agent identity,
target, state tag, severity and attachments ride in `metadata`, and the
`AgentConversationSurface` render slots read it. We never need to fork fi-glass.

## 3. Backend decision

**Keep the canonical backend. Build a frontend adapter.**

- DO NOT adapt the backend to `/chat/stream` first. `/workflow/start` +
  `/workflow/{id}/events` (SSE) + `/workflow/{id}/history` already express the
  high-stakes contract — that is the source of truth.
- Build a custom **`AgentHook`** (`useActivistAgent`) whose `send(concern)` POSTs
  `/workflow/start`, opens the events SSE, and folds the handoffs into the turn;
  plus a pure mapper `workflow history/events → ChatMessage[]`.
- Only if fi-glass later *requires* a chat-stream endpoint do we add a thin
  **facade** `/chat/activist-os/stream` that wraps `/workflow/*` — a wrapper, never
  a new source of truth.

## 4. Mapping — the 8 handoffs → `ChatMessage[]`

Each handoff becomes a `ChatMessage` (`role: 'assistant'`) carrying metadata:

```ts
metadata: {
  agent: AgentName,        // speaker — Evidence / Campaign / Safety / …
  target: AgentName,       // @mention target
  tag: string,             // EVIDENCE_COMPLETE / SAFETY_VETO / REVISION_READY / …
  severity?: 'critical' | 'approved',
  virtual?: boolean,       // ONLY from real handoff metadata
  attachment?: 'blocked_reason' | 'approved_rewrite' | 'evidence_brief' | 'campaign_packet',
}
```

| # | agent → target | tag | notes |
|---|---|---|---|
| 0 | Evidence → Campaign | `EVIDENCE_COMPLETE` | attaches evidence brief |
| 1 | Campaign → Safety | `SAFETY_REQUEST` | campaign draft for review |
| 2 | Safety → Campaign | `SAFETY_VETO` | **severity: critical** · attaches blocked reason + draft |
| 3 | Campaign → Safety | `REVISION_READY` | revised language |
| 4 | Safety → Outreach | `SAFETY_APPROVED` | **severity: approved** · attaches approved rewrite |
| 5 | Outreach → Coordinator | `OUTREACH_READY` | |
| 6 | Coordinator → Reporter | `TASKS_READY` | `virtual` only if the handoff says so |
| 7 | Reporter → System | `PACKET_READY` | `virtual` only if the handoff says so · attaches packet |

The **cold-open mock** (`MOCK_WORKFLOW_HISTORY`) and the **live** run both feed this
mapper — mode label stays honest (`MOCK FALLBACK` vs `LIVE`).

## 5. The money-shot inside the chat

The CAMPAIGN ⇄ SAFETY veto loop must survive — but as **inline rich messages**,
not a competing dashboard panel:

```
Campaign draft message
   ↓
Safety VETO message  (severity critical, red bubble, blocked-reason attachment)
   ↓
Campaign revision message
   ↓
Safety APPROVED message  (severity approved, green bubble, rewrite attachment)
```

Acceptable forms: inline rich message, a pinned safety card above the transcript,
or an artifact attachment inside the Safety messages. It must no longer feel like a
separate panel competing with the chat.

## 6. Risks to hold

- Do **not** lose artifacts (evidence brief / safety review / campaign packet).
- Do **not** lose provenance.
- Do **not** fake the virtual reporter — `virtual` comes only from real handoff metadata.
- Do **not** hide the safety veto — it is the differentiator; it stays loud.

## Live smoke findings

Verified end-to-end against the **real** local `/workflow/*` backend
(`TRANSPORT=local`), driving the canary in a real browser at
`/app?fi_glass_canary=1` — not via proxy. ~8 distinct live runs.

- `AgentConversationSurface` works as the canonical surface. Agent identity,
  @mention target, and VETO/APPROVED severity all expressed through its
  per-message slots (`renderHeader` / `renderBadge` / `messageBubbleClassName`).
- **`useAgentConversation` does NOT model `1 send → 8+ handoff messages`.** It
  folds one `send` into one assistant turn (`foldAssistantTurn`). A governed
  workflow emits 8+ agent messages per concern, which the fold would collapse
  into a single bubble.
- Activist OS needs either **multi-message agent turns** or an **external /
  controlled transcript mode** for workflow adapters (the consumer supplies
  `messages`, the surface renders them).
- **RESOLVED UPSTREAM (fi-glass 1.2.0):** rather than hack the consumer,
  `useAgentConversation` gained a `externalMessages?: ChatMessage[]` controlled
  mode — when provided, the consumer owns the visible thread (no optimistic push,
  no fold), while `send`/`turn`/`turnError`/`retry`/`newConversation` machinery
  stays. Fully backward-compatible (undefined = unchanged). The canary now
  consumes it as a **thin** wrapper:
  `useAgentConversation(agent, { externalMessages: agent.messages })` — the
  hand-rolled `AgentConversation` object is gone. This is the canary-driven
  upstream loop: a real framework limit fixed in `free-intelligence`, the
  consumer thinned, the E2E green.
- Backend used: `POST /workflow/start`, `GET /workflow/{id}/events` (SSE),
  `GET /workflow/{id}/history`. **No `/chat/stream`.** `stream_end` closes the
  `EventSource`, then `/history` replaces/enriches the transcript.
- Render-loop fixed at the root: `useActivistAgent.send` is stable across a run
  (mode read via a ref), so the `AgentConversation` object does not churn during
  the local-transport burst. Console is clean across repeated runs.

## Deploy blocker observed

- `api/Dockerfile` + `api/entrypoint.sh` start **`app.app:app`** (the template's
  chat face, `POST /chat/stream`) — **not `app.main:app`** (the Activist OS
  workflow API exposing `/workflow/*`). If deploy uses `app.app:app`, production
  will **not** expose `/workflow/*` and the web app's `startWorkflow` will 404.
  Needs verification before any deploy. NOT fixed here (no backend/deploy changes).
- Health: the local API exposes **`/health`**, not `/health/full`. Treat `/health`
  as the current observed truth unless the `/health/full` contract is restored.

## Next

**Pivot (gated on Bernard's review)** — design the pivot as fi-glass chat as the
primary surface + an artifacts rail, NOT a blind deletion of the dashboard. The
visual replacement is the big move; Bernard sees the canary first, then it is
designed. The `useAgentConversation` multi-message enhancement and the deploy
blocker are tracked above as follow-ups.
