# Canonical Contract — the invariants (PRESERVE exactly)

These are the behavioral invariants of Activist OS, lifted verbatim from the old
standalone's executable tests (`/tmp/aos-legacy/api/tests/test_transport_contract.py`,
`test_events_endpoint.py`) — the test IS the spec. The fresh build must satisfy
these; they become executable contract tests in Step 2 (before any implementation).

## 1. The 8-step workflow order (handoff `from_agent` sequence)

A complete demo run produces **exactly 8 handoffs**, in this `from_agent` order:

```
index:  0         1         2        3         4        5         6            7
agent:  evidence  campaign  safety   campaign  safety   outreach  coordinator  reporter
type:   EVIDENCE_ SAFETY_   SAFETY_  SAFETY_   SAFETY_  OUTREACH_ TASKS_       PACKET_
        COMPLETE  REQUEST   VETO     REQUEST   APPROVED READY     READY        READY
```

- **`veto_index = 2`** — Safety vetoes the first plan.
- **`approved_index = 4`** — Safety approves the revised plan.
- Invariant: at least one `SAFETY_VETO`, and a `SAFETY_APPROVED` strictly after it.
- The canonical demo is exactly one veto → one revision → approval (the money shot).

## 2. Reporter is virtual (Band mode)

In Band mode the room recruits **4 real agents** and stays at the **5-seat cap**;
`reporter` and `system` are **virtual** (no room seat — they never occupy a Band
participant slot). `evidence` initiates and is not counted among the recruited.
Every handoff is stamped with the run's `band_room_id` (one room per run).

## 3. SSE terminal semantics — `GET /workflow/{run_id}/events`

- `Content-Type: text/event-stream`.
- Replays a completed run's recorded events: `event_type` includes `handoff_sent`
  and `workflow_completed`.
- **The last event is always `stream_end`** (the sentinel).
- Sequence shape: `workflow_started → handoff_sent…(×8) → workflow_completed → stream_end`.
- Unknown `run_id` → `404` (same contract as `GET /workflow/{id}`).

## 4. History artifacts shape

`GET /workflow/{run_id}/history` projects the recorded handoffs into the demo
artifacts (evidence brief, the veto/approval pair, outreach pack, task board,
campaign packet + the full safety audit incl. the rejected revision). Exact shape
to be locked from the old `_build_artifacts` when it's inspected for porting.

## 5. Safety Gate presentation model

The veto is the product: the demo surfaces the structured `SAFETY_VETO` verdict
(`needs_revision`, `blocked_items[].check`, reviewer note) and the subsequent
`SAFETY_APPROVED` — both on the record. Governance shows rejections, not only
approvals. (Presentation lives only in the Next `web/` per [[ui]].)
