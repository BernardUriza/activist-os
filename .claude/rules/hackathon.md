# Hackathon — Band of Agents (lablab.ai)

Official reference card for prioritization decisions. Source:
[lablab.ai/ai-hackathons/band-of-agents-hackathon](https://lablab.ai/ai-hackathons/band-of-agents-hackathon).
Fetched 2026-06-11 (pre-kickoff). **Re-fetch at kickoff** — judging criteria,
Band docs and starters drop with the stream.

## Rule 0 — Product

The product should feel like an activist toolkit, but behave like
regulated-workflow infrastructure.

- Advocacy is the interface; **governance is the product**. The demo's money
  shot is the SAFETY agent **vetoing** a risky plan through Band, on the record.
- Every public-facing artifact rests on verified evidence with tiered provenance.
- The system assembles packets for humans to execute; it never publishes on
  its own.
- The demo must sell the cause but demonstrate architecture: coordination,
  contracts, veto loop, audit trail, graceful degradation.

## Logistics (verified 2026-06-11)

- **Dates**: online build **June 12–19, 2026**. Kickoff stream Fri Jun 12
  ~9:00 AM Central / 15:00 UTC (registration closes then too).
- **Submissions close**: Fri **Jun 19, 15:00 UTC**. House rule: **submit
  early on the 19th** — no 40-minutes-before-deadline reruns.
- **Prize pool**: $10,000+.
- **Team**: Free Intelligence (Bernard). Project: Activist OS.

## Track

**Regulated & High-Stakes Workflows** (main track, chosen 2026-05-30).
Secondary framing if needed: internal campaign ops for mission-driven orgs
(Internal Enterprise Workflows). Do NOT pitch into Multi-Agent Software
Development — that track is for coding agents.

## Hard requirement

> Build a multi-agent system where **at least 3 agents collaborate through
> Band** across planning, execution, review, decision-making, or task handoff.

Activist OS runs 6 agents through Band; the CAMPAIGN ⇄ SAFETY veto loop is
the clearest "real coordination, not sequential prompts" proof. See `band.md`.

## Judging criteria — ✅ CONFIRMED (fetched 2026-06-11)

Source: verbatim from hackathon page. No re-verification needed at kickoff.

| # | Criterion | Verbatim definition | Map to product surface |
|---|---|---|---|
| 1 | Application of Technology | "How effectively does the solution use Band as the coordination layer between multiple specialized agents? Strong submissions should show agents collaborating through Band with clear task handoffs, shared context, role specialization, task state, and coordination." | The veto loop is the money shot: CAMPAIGN→SAFETY handoff, Safety's verdict with `blocked_items` back to CAMPAIGN — all visible in Band room history |
| 2 | Presentation | "How clearly does the team explain and demonstrate the solution? Strong submissions should make the multi-agent workflow easy to understand, including the problem, agent roles, Band's role in coordination, the flow of context and handoffs, and the value created." | Live demo URL + ≤4 min video. Show the veto rejection, not just the approval. |
| 3 | Business Value | "How clearly does the project solve a real enterprise workflow problem? Strong submissions should address a meaningful business process, reduce manual coordination, improve decision-making, accelerate execution, or make a complex workflow easier to operate." | "The missing ops layer for orgs with no staff" — campaign packet = hours of specialist work, governed and auditable |
| 4 | Originality | "How creatively does the project use multi-agent collaboration? Strong submissions should go beyond a simple chatbot, single-agent assistant, or linear automation, and demonstrate what becomes possible when agents can discover each other, coordinate, divide work, review outputs, escalate issues, or collaborate across frameworks." | Safety-gated advocacy with tiered provenance + veto loop is architecturally novel — not a linear pipeline |

## Priorities when time runs short (in order)

1. The veto loop working through Band (the differentiator).
2. One polished end-to-end case (greenwashing campaign) — never five half-demos.
3. Demo URL the judges can touch.
4. Video + README + submission assets (Jun 18).
