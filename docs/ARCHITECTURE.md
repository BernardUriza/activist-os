# Architecture

## The flow, end to end

A user submits a community concern, e.g.:

> "Help us organize a campaign against greenwashing by a local restaurant chain."

### 1. EVIDENCE agent — the investigator
Receives the concern. Researches public sources, fetches full text where possible, and produces an **`evidence_brief`**: each claim tagged `supported / partial / unsupported`, with tiered provenance per source. Unsupported claims never silently disappear — they are carried forward as *blocked for use*.

### 2. CAMPAIGN agent — the strategist
Consumes the evidence brief. Designs objective, narrative, audience and concrete actions, producing a **`campaign_plan`**. May only build narrative on `supported` (or explicitly-caveated `partial`) claims; every narrative element references the evidence item it stands on.

### 3. SAFETY agent — the gate (veto power)
Reviews the campaign plan and produces a **`safety_verdict`** with explicit checks:

- defamation risk (claims vs evidence strength)
- doxxing (personal data of private individuals)
- harassment dynamics (targeting people vs targeting patterns)
- unsupported accusations
- unsafe escalation (anything beyond lawful, nonviolent action)

Verdicts: `approved` · `needs_revision` (back to CAMPAIGN with notes) · `blocked`. Every verdict — including rejections — lands in the audit log. **Nothing reaches outreach without approval.**

### 4. OUTREACH agent — the writer
Only runs on an approved plan. Produces the **`outreach_pack`**: emails, social posts, flyer copy — each item traceable to the approved narrative.

### 5. COORDINATOR agent — the organizer
Converts the approved plan into a **`task_board`**: discrete volunteer tasks with skill tags, time estimates and dependencies. Designed for groups with zero technical staff.

### 6. REPORTER agent — the archivist
Assembles the **`campaign_packet`**: evidence brief + approved plan + outreach pack + task board + provenance report + the complete safety audit log. This is the deliverable a community group actually executes.

## Where Band comes in (event work)

Band provides the coordination layer between the agents:

| Need | Band primitive (to map during kickoff) |
|---|---|
| Agents discover each other | agent registry / discovery |
| Structured context handoff | message exchange with typed payloads (our JSON contracts) |
| SAFETY veto + revision loop | request/response between CAMPAIGN ↔ SAFETY |
| Human checkpoint before packet release | human-in-the-loop hook |
| Audit trail of who-said-what | conversation/coordination history |

Design rule: **our contracts ride inside Band messages**. Band owns the transport, discovery and coordination; the schemas in `contracts/` own the meaning. If a Band primitive can replace a custom piece, the Band primitive wins (judges score Band usage, and less plumbing is less risk).

## Failure modes we design against

- **Hallucinated evidence** → provenance tiers + EVIDENCE agent never asserts beyond its sources.
- **Activist liability** → SAFETY gate with veto + audit log; "legal-risk-aware by design", never "legal immunity" (no system grants that).
- **Pipeline theater** (sequential prompts dressed as agents) → real handoffs through Band, revision loops, and an audit trail proving coordination.
- **Scope creep** → one polished use case (greenwashing campaign, end to end) beats five half-demos.
