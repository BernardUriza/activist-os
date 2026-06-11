# CLAUDE.md — Activist OS

Project context for Claude Code. Read this before touching anything.

## What this is

**Activist OS** is a multi-agent workflow for **safe, evidence-backed civic
advocacy**: a community concern goes in; an evidence-verified,
safety-reviewed campaign packet comes out. Built for the **Band of Agents
Hackathon** (lablab.ai, June 12–19 2026), track **Regulated & High-Stakes
Workflows**, team **Free Intelligence**.

The pitch in three lines:

> Band coordinates the agents.
> FI preserves memory and provenance.
> Safety gates every public action.

This repo is a **thin consumer** of
[`fi-runner`](https://github.com/BernardUriza/free-intelligence/tree/main/apps/packages/fi-runner)
(agent loop, guards, provenance, backends live upstream) plus **Band**
(coordination layer). This repo only adds: agent specs/configs, inter-agent
contracts, Band wiring, and a demo UI. **Keep it thin** — reusable logic
belongs upstream, not here.

## Layout

```
contracts/      📜 JSON Schema contracts — the SSOT for every inter-agent handoff
agents/         🤖 one SPEC.md per agent (evidence/campaign/safety/outreach/coordinator/reporter)
docs/           📐 ARCHITECTURE.md (flow + Band mapping) · DEMO_SCRIPT.md (the 4-min demo)
.claude/rules/  📏 the rules below — read them before acting
```

## The agent flow

EVIDENCE → CAMPAIGN ⇄ SAFETY (veto loop) → OUTREACH + COORDINATOR → REPORTER

The CAMPAIGN ⇄ SAFETY veto loop through Band is the architectural
centerpiece and the demo's money shot. It never gets cut.

## Rules index (.claude/rules/)

| Rule | What it governs |
|---|---|
| `hackathon.md` | dates, track, hard requirement, judging map, cut priorities |
| `architecture.md` | three-layer split, contracts-as-law, no pipeline theater |
| `band.md` | Band integration doctrine + primitive mapping table (fill at kickoff) |
| `safety.md` | the five checks, veto semantics, audit-log completeness |
| `pitch.md` | one-liners, framing order, forbidden vocabulary |
| `language.md` | English chrome; campaigns speak the community's language |
| `git.md` | multi-session safety — never lose a parallel agent's work |
| `working-style.md` | use tools before "no sé"; no permission for trivial fixes; pbcopy for external posts |

## Status & key dates

- 🚧 Pre-hackathon scaffold (legit prep). **Band/Codeband integration is
  event work** — starts at kickoff (Fri Jun 12, 15:00 UTC) once docs drop.
- First task at kickoff: fill the primitive table in `band.md` from the real
  Band docs BEFORE writing transport code.
- **Submit early on Jun 19** (closes 15:00 UTC). Non-negotiable house rule.

## Lineage

The engine doctrine (tiered provenance, plan-before-act, clinical
guardrails) is inherited from [Insult AI](https://github.com/BernardUriza/insult-ai)
(Bright Data hackathon, May 2026). *Insult AI cross-examined claims;
Activist OS coordinates evidence-backed action.*
