# Architecture — contracts first, implement second

**Behavior is expressed as contracts before implementation.** The order for any
change to this codebase:

```
contract (what must be true) → test → implementation → UI → deploy
```

The behavioral invariants live in [docs/CANONICAL_CONTRACT.md](../../docs/CANONICAL_CONTRACT.md).
No implementation decision is valid if it breaks those invariants.

## Boundaries

| Layer | Location | Rule |
|---|---|---|
| API contract | `docs/CANONICAL_CONTRACT.md` | Never change without updating the contract tests |
| Workflow core | `api/app/` | `app.main:app` is the entrypoint — not `app.app:app` |
| Transport | `api/app/transports/` | `local` (default/demo), `band` (real agents, opt-in) |
| Web surface | `web/` | fi-glass `AgentConversationSurface` is the canonical primary |
| Artifacts rail | `web/components/app/` | Safety Gate / Evidence Brief / Campaign Packet |

## The one rule that never changes

**`/workflow/*` is the source of truth.** The web adapter (`useActivistAgent`)
maps transport events → `ChatMessage[]`; fi-glass renders them. Neither the
backend nor the frontend protocol changes to fit the other's convenience.
