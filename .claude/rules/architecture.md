# Architecture — contracts are the law, Band is the road

Deep-dive lives in `docs/ARCHITECTURE.md`. This rule is the doctrine that
governs every implementation decision during the build week.

## The three-layer split

| Layer | Owner | What it owns |
|---|---|---|
| **Coordination** | Band / Codeband | discovery, message transport, handoffs, human-in-the-loop hooks, coordination history |
| **Meaning** | `contracts/*.schema.json` | the structure of every inter-agent payload (the SSOT) |
| **Brains** | fi-runner + agent role prompts | agent loop, guards, provenance, backends |

Keep this repo **thin**: if logic feels reusable (agent loop mechanics,
guard machinery, provenance plumbing), it belongs upstream in
[`fi-runner`](https://github.com/BernardUriza/free-intelligence/tree/main/apps/packages/fi-runner),
not here. This repo adds: agent configs, contracts, Band wiring, a demo UI.

## Rules

1. **Contracts are the source of truth.** Every inter-agent message validates
   against its schema BEFORE it rides a Band message. A handoff that doesn't
   validate doesn't happen. Schema changes are deliberate commits, never
   silent drift inside a prompt.
2. **Band primitive > custom plumbing.** If Band offers discovery, typed
   messaging, request/response, or HITL hooks, use Band's version. Judges
   score Band usage; custom plumbing is risk plus zero points.
3. **The veto loop is sacred.** CAMPAIGN ⇄ SAFETY revision cycling through
   Band request/response is the architectural centerpiece. Whatever gets cut
   when time runs short, this doesn't.
4. **Provenance tiers travel with every claim.** `fetched_fulltext` >
   `news_search` > `company_source`. No claim enters a campaign without its
   sources attached — this is inherited engine behavior from Insult AI, do
   not regress it.
5. **No pipeline theater.** Six prompts called in sequence by one process is
   NOT multi-agent coordination. Agents must exchange context through Band,
   visible in the coordination history. If a judge can't see the handoffs,
   they didn't happen.
6. **Humans hold the send button.** The system assembles campaign packets;
   it never publishes to a real audience on its own. The HITL checkpoint
   before packet release is product, not friction.

## Cut order when the week compresses

UI polish → COORDINATOR agent → REPORTER as separate agent (fold into
backend assembly) → multiple use cases. **Never cut**: the veto loop, the
contracts, provenance tiers, the demo URL.
