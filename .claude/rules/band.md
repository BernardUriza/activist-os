# Band / Codeband — the hard requirement

Analog of insult-ai's `bright-data.md`: the sponsor tech is not decoration,
it is the graded surface.

## The requirement (verbatim from the event page)

> Build a multi-agent system where **at least 3 agents collaborate through
> Band** across planning, execution, review, decision-making, or task handoff.

Activist OS commits to 6 agents through Band. The minimum demonstrable bar
if everything burns: EVIDENCE → CAMPAIGN ⇄ SAFETY (3 agents, including a
review loop — the strongest possible "real coordination" proof).

## Integration doctrine

- **Our contracts ride inside Band messages.** Band owns transport,
  discovery and coordination; `contracts/*.schema.json` owns meaning.
  Validate payloads against the schema before sending and after receiving.
- **Prefer Band primitives over custom plumbing** (architecture rule #2).
  Anything Band does natively that we hand-roll is negative points twice.
- **Coordination must be visible.** The demo shows Band's message/handoff
  history, not a narrated claim that "agents talked".

## What we know pre-kickoff (fetched 2026-06-11)

**Band is TWO different things** — do not confuse them:

- **Band platform / API** — the "shared interaction layer for AI agents": chat rooms,
  Band Agent API, Band SDK. This is what Activist OS uses. **Track 3.**
- **Codeband / getband.app** — open-source IDE for coding agents (git worktrees,
  dispatch to Claude Code/Codex/OpenCode). Track 2 reference impl. NOT our concern.

Known Band platform primitives (confirmed from hackathon page):
- **Agent chat rooms** — the core coordination primitive. Agents join rooms, share
  structured context, hand off tasks.
- **Band Agent API** — connect autonomous agents, recruit peers into rooms,
  participate in agent-to-agent workflows.
- **Band SDK** — install to configure and connect agents to the platform.

**SDK/API docs, access codes, and onboarding details DROP AT KICKOFF** (Jun 12,
9 AM CST). Source: hackathon page — "Account setup, onboarding instructions, API
access details, and any special hackathon access codes will be shared before or
during the Kick-off stream."

## To map at kickoff (Jun 12) — fill this table from the real docs

| Need | Band primitive | Status |
|---|---|---|
| Agent identity / discovery | Band Agent API (confirm) | ⬜ |
| Typed message exchange (our JSON contracts) | Agent chat rooms (confirm) | ⬜ |
| Request/response (CAMPAIGN ⇄ SAFETY veto loop) | Chat room turn-taking? (confirm) | ⬜ |
| Long-running workflow state | Room state / context (confirm) | ⬜ |
| Human-in-the-loop checkpoint | Room HITL hook? (confirm) | ⬜ |
| Coordination history / audit visibility | Room message history (confirm) | ⬜ |
| Band SDK install + auth | Band SDK Setup guide (drops at kickoff) | ⬜ |

Process: at kickoff, open Band SDK Setup + Band Hacker Guide from the hackathon
AI Tech pages, fill the table, THEN write transport code. No integration code
before the table is filled — guessing an SDK's shape wastes the scarcest
resource (build days).

## Fallback posture

If a Band primitive is missing or broken mid-week, degrade gracefully:
keep the contract-validated handoff, implement the thinnest possible
custom bridge, and **document the gap honestly in the README** — judges
reward honest engineering over silent hacks.
