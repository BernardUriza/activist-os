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

## To map at kickoff (Jun 12) — fill this table from the real docs

| Need | Band primitive | Status |
|---|---|---|
| Agent identity / discovery | ? | ⬜ |
| Typed message exchange (our JSON contracts) | ? | ⬜ |
| Request/response (CAMPAIGN ⇄ SAFETY veto loop) | ? | ⬜ |
| Long-running workflow state | ? | ⬜ |
| Human-in-the-loop checkpoint | ? | ⬜ |
| Coordination history / audit visibility | ? | ⬜ |
| Codeband's role vs Band (what is each for?) | ? | ⬜ |

Process: at kickoff, pull docs/starters/boilerplates from the event's AI
Tech pages, fill the table, THEN write transport code. No integration code
before the table is filled — guessing an SDK's shape wastes the scarcest
resource (build days).

## Fallback posture

If a Band primitive is missing or broken mid-week, degrade gracefully:
keep the contract-validated handoff, implement the thinnest possible
custom bridge, and **document the gap honestly in the README** — judges
reward honest engineering over silent hacks.
