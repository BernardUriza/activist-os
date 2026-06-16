# Reuse Map — migration status (completed)

Status: **DONE** — all portable implementation has been ported; discard list never
landed; rewrite-only glue was re-authored fresh on the canonical stack.

This document is preserved as a historical record of what came from the old
standalone and how each piece was classified. It is not an active checklist.

## What was classified and the outcome

### PRESERVED as invariants
The behavioral contracts from the old standalone's test suite became
[docs/CANONICAL_CONTRACT.md](CANONICAL_CONTRACT.md). The 8-step workflow order,
veto/approved indices, SSE terminal semantics, and reporter-as-virtual are all
there with the original test coverage as the spec.

### PORTED (portable implementation)
- Transport layer (`local`, `band`) — ported after contract tests were green
- `workflow_runner.py` — the 8-step loop, ported behind the order/index tests
- `_build_artifacts` — history-artifacts builder, shape locked under a test
- Visual tokens / Safety-Gate presentation — ported into `web/` (Next.js only)

### REWRITTEN (glue / wiring)
- `api/app/main.py` FastAPI routes — re-authored on the template stack
- Agent logic (`api/app/runner/agents/`) — roles/prompts as reference, prompts re-authored
- Azure deploy workflows (`.github/workflows/`) — template's own workflows used
- Next.js routes and app wiring — built fresh in `web/`

### DISCARDED
- `web/*.html` static demo shells — never carried over
- Duplicated API clients
- Local-only scripts and absolute-path config
