# Reuse Map — old standalone activist-os → fresh canonical build

Every piece of the old standalone (`BernardUriza/activist-os`, read from
`/tmp/aos-legacy`) classified into the four buckets (per [[architecture]]). Nothing
is copied until it's classified and — for code — shown to satisfy the canonical
architecture via a passing contract test.

## 1. PRESERVE as invariant → `docs/CANONICAL_CONTRACT.md` + tests
| Old source | Invariant |
|---|---|
| `api/tests/test_transport_contract.py` | 8-step `from_agent` order; `veto_index=2`, `approved_index=4`; veto-before-approve |
| `api/tests/test_events_endpoint.py` | SSE `text/event-stream`; `handoff_sent` + `workflow_completed`; `stream_end` last; 404 on unknown |
| transport_contract Band assertions | reporter/system virtual; 5-seat cap; `band_room_id` per run |
| `contracts/*.schema.json` (10) + `api/app/models/contracts.py` | the typed contract shapes |
| `docs/DEMO_SCRIPT.md` | Safety-Gate-as-money-shot presentation model |

## 2. PORTABLE implementation → copy ONLY after inspection + green contract test
| Old source | Note |
|---|---|
| `api/app/runner/transports/{base,local,band}_transport.py` | port after the transport-parity contract test is green |
| `api/app/runner/workflow_runner.py` | the 8-step loop logic — port behind the order/index test |
| `api/app/main.py::_build_artifacts` | history-artifacts builder — lock its shape under a test first |
| `api/band_agents/*` + `oauth_adapter.py` | BandTransport side — port after the SSE/parity tests |
| `web/` visual tokens / Safety-Gate presentation | port INTO the Next `web/` only (never the static HTML) |

## 3. REWRITE-only glue → re-author on the canonical stack, do NOT copy
- `api/app/runner/agents/*` — agent logic (prompts/roles are reference; re-author against the contracts)
- `api/app/main.py` FastAPI wiring + routes — re-author on the template's `app/` layout
- deployment workflows (`infra/`, Makefile targets) — the template ships its own Azure workflows
- Next routes / app wiring — built fresh in `web/`

## 4. DISCARD / archive → never carried over
- `web/*.html` (`demo.html`, `index.html`, `checklist.html`) — static HTML product app ([[ui]])
- duplicated API clients
- local-only scripts (`run_band_agents.sh`, ad-hoc Makefile targets)
- absolute-path config (`/Users/...` hardcoded anything)

**Source of truth for the old code: the GitHub archive `BernardUriza/activist-os`
(temporarily at `/tmp/aos-legacy` for this inspection). Never re-cloned to
`~/Documents` as live code** — see memory `activist-os-build-fresh-never-resurrect`.
