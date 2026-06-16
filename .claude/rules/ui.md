# UI — single source of truth

**The ONLY product-UI source of truth is `web/`.** (Next.js 16 + fi-glass +
`@free-intelligence/core`.)

No UI feature, visual change, API client, SSE behavior, or branding may be
implemented anywhere else. A parallel surface outside `web/` is a violation, not
a convenience.

## Primary surface — `/app`

`/app` uses `FiGlassPrimary`: the canonical `AgentConversationSurface` from
fi-glass as the main column (1 concern → 8 handoffs, veto/approved severity),
plus an artifacts rail (Safety Gate, Evidence Brief, Campaign Packet) fed from the
same `useActivistAgent` run. The legacy 3-column dashboard is preserved at
`/app?dashboard=1` until parity is proven; do NOT delete `DashboardClient`.

## fi-glass contract

- Use `externalMessages` controlled mode (fi-glass ≥1.2.0) — `useActivistAgent`
  owns the thread; fi-glass renders it verbatim.
- Never hand-roll an `AgentConversation` object. Let `useAgentConversation` supply
  the send/retry/newConversation machinery.
- Bubble styling via `messageBubbleClassName(m)` resolver — role=user gets
  `glass-chat-bubble-user`, severity=critical gets `glass-chat-bubble-veto`,
  severity=approved gets `glass-chat-bubble-approved`.

## Component ownership

| Component | Role |
|---|---|
| `FiGlassConversation` | Presentational — canonical surface config, shared by Primary and Canary |
| `FiGlassPrimary` | Chrome + chat + artifacts rail. DEFAULT /app surface. |
| `FiGlassConversationCanary` | Thin wrapper for opt-in preview (`?fi_glass_canary=1`) |
| `DashboardClient` | Legacy 3-column dashboard, reachable via `?dashboard=1` only |
| `AppClient` | Brancher — mounts exactly ONE surface (one SSE stream) |
