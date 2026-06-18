# Extract the HTTP/workflow transport from `web/lib/api.ts` upstream to fi-core

Status: Proposed
Proposed: 2026-06-18 by Bernard (canary finding, relayed through the orchestrator coagent)

## What it is

`web/lib/api.ts` (~200 lines) mixes two layers that the framework-canary-consumer
doctrine says must live apart. The cut is **envelope/protocol vs. payload/domain**,
not export-by-export:

**Belongs in fi-core** (generic transport every python-bot + Next.js consumer
re-implements byte-for-byte; fi-core's TS surface today ships conversation /
agent-turn / theme types but has **no HTTP or workflow client at all**):

- `createFiApiClient({ baseUrl, apiKey })` wrapping `normalizeApiUrl`, `apiUrl`,
  `apiHeaders` (public `X-API-Key` gate + `X-Client-Request-ID`),
  `newClientRequestId`, dev fail-open, build-time `NEXT_PUBLIC_*` inlining.
- The `/workflow/*` client — `startWorkflow`, `getWorkflowHistory`,
  `getWorkflowEventsUrl`, `WorkflowNotFoundError`. `/workflow/*` is the fi-runner
  protocol (see [architecture.md](../rules/architecture.md)), so its TS client is
  framework-owned.
- Generic parameterized shapes: `StreamEvent`, `HandoffView<TAgent, TType>`,
  `WorkflowHistory<TArtifacts>`; the timeout/limit constants as configurable
  defaults.

**Stays in the consumer** (Activist OS payload = the domain vocabulary, the money
shot): `AgentName` (the 6 Band agents), `HandoffType` (`safety_veto` /
`safety_approved` / …), `VetoLoop`, `EvidenceBrief`, `SafetyReview`,
`CampaignPacket`, `BandProvenance` — these are the type-args plugged into the
fi-core generics.

Outcome: `lib/api.ts` shrinks ~200 → ~50 lines (domain unions + one
`createFiApiClient` instantiation); fi-core gains a `workflow-client` level the
next canary inherits for free.

## Canonical path to reuse (Art. 6)

Add the capability as a **new opt-in level** in `~/Documents/free-intelligence`
(fi-core TS), driven by that repo's `CLAUDE.md` — never hacked into the consumer.
Existing consumers keep working; the framework grows strictly more capable. Then
re-thin `web/lib/api.ts` to consume it and delete the local scaffolding. Per
[[framework-canary-consumer]]: not done until the consumer's E2E is green against
the improved framework with a thinner wrapper.

## The decision that's the owner's

Timing only — the boundary itself is agreed (Claude + coagent converged).
- Excluded from `fi-ts-v1.3.0` / PR #247 — that tag stays frozen as the
  reproducible package for the demo video.
- Probable landing: **fi-core 1.4.0** (a minor, not 1.3.1 — it introduces new
  public surface), as a post-video / post-hackathon follow-up.

## Status / next step

Not built yet. Demo-crunch rule (Jun 18, 2026): do NOT touch `lib/api.ts`, the
fi-core publish chain, or introduce any dependency migration before the final
video. Reproducibility + video first; thin the consumer after.

The coagent suggested capturing this as `docs/FI_CORE_WORKFLOW_CLIENT_PROPOSAL.md`;
it lives here instead because [[backlog-handling]] is the canonical home for a
canary→upstream roadmap increment.
