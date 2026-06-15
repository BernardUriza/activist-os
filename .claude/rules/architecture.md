# Architecture — contracts first, classify before copy

**Behavior is ported as CONTRACTS first, implementation second.** The order for
this whole build (coagent, 2026-06-14):

```
rules → contracts → tests → implementation → UI → deploy
```

No "worked fast, then we'll see." The contract + its executable test exist before
the implementation that satisfies it.

## Before copying any code from the old repo, classify it

Every piece of the old standalone activist-os falls in exactly one bucket
(see `docs/REUSE_MAP.md` for the full classification):

1. **Invariant** — a behavioral contract that must be PRESERVED exactly
   (the 8-step workflow order, the veto-loop indices, the SSE terminal
   semantics…). These become `docs/CANONICAL_CONTRACT.md` + executable tests.
2. **Portable implementation** — copy only AFTER it's been inspected and shown to
   satisfy the canonical architecture (transport tests, SSE tests, artifact
   builder, BandTransport, visual tokens).
3. **Rewrite-only glue** — re-author on the canonical stack, do not copy
   (integration glue, app wiring, deployment workflows, Next routes).
4. **Discard / archive** — never carried over (static HTML product app,
   duplicated API clients, local-only scripts, absolute-path config).

**Never copy old implementation directly unless it satisfies the canonical
architecture.** A green test against an invariant is the license to port; a
"it's already written" is not.
