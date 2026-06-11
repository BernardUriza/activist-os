# Activist OS

**A multi-agent workflow for safe, evidence-backed civic advocacy.**

> Band coordinates the agents.
> FI preserves memory and provenance.
> Safety gates every public action.

Built for the [Band of Agents Hackathon](https://lablab.ai/ai-hackathons/band-of-agents-hackathon) (lablab.ai · June 12–19, 2026) · Track: **Regulated & High-Stakes Workflows** · Team: **Free Intelligence**

## What it does

Activist OS turns a community concern into an **evidence-backed, safety-reviewed campaign packet**: verified claims, campaign strategy, outreach copy, volunteer tasks, and a full provenance report.

Initial use case: vegan and ecological community campaigns — greenwashing detection and local action planning.

Civic advocacy is a genuinely high-stakes workflow. A public accusation has consequences: defamation liability, doxxing risk, harassment dynamics, reputational damage to the organizations involved. Most activist groups have no technical staff and no review process — they run on burnout and vibes. Activist OS is the missing operations layer: every public action passes through evidence verification and a safety gate before it exists.

The system is **legal-risk-aware by design**: it blocks unsupported accusations, doxxing, harassment, and unsafe escalation before anything is published.

## How the agents collaborate

```
[Community concern]
       │
       ▼
 1. EVIDENCE agent ──(evidence_brief)──► 2. CAMPAIGN agent
                                                │
                                        (campaign_plan)
                                                ▼
                                         3. SAFETY agent ──(safety_verdict)──┐
                                                │ approved                   │ blocked → revise
                                                ▼                            ▼
 4. OUTREACH agent (emails / posts / flyers)            back to CAMPAIGN agent
       │
       ▼
 5. COORDINATOR agent (volunteer task board)
       │
       ▼
 6. REPORTER agent → campaign_packet (everything + provenance + safety audit log)
```

Six specialized agents collaborate through **Band** — exchanging structured context (JSON Schema contracts), delegating work, and enforcing review gates. This is real agent-to-agent coordination across planning, execution, review and handoff — not a pipeline of sequential prompts.

## Architecture principles

1. **Contracts are the source of truth.** Every inter-agent message validates against a JSON Schema in [`contracts/`](contracts/). No free-form handoffs.
2. **Provenance is tiered.** Every claim carries its sources, tagged by how they were read: `fetched_fulltext` > `news_search` > `company_source`. A judge can see what was read versus glimpsed.
3. **Safety is a gate, not a filter.** The SAFETY agent has veto power. Nothing reaches OUTREACH without an `approved` verdict, and every veto is logged in the audit trail.
4. **Humans stay in the loop.** The output is a campaign *packet* for humans to execute — the system never publishes on its own.

## Status

🚧 **Pre-hackathon scaffold** (architecture, contracts, agent specs, demo script — prepared before kickoff, as the hackathon guidelines allow).

The **Band/Codeband integration** — live agent-to-agent coordination, context exchange, and handoffs — is built during the event (June 12–19). Progress will be visible in the commit history.

## Repository layout

```
contracts/    JSON Schema contracts for every inter-agent message (the SSOT)
agents/       One spec per agent: role, inputs, outputs, guardrails
docs/         Architecture deep-dive and demo script
```

## Lineage

Activist OS builds on the engine proven by [Insult AI](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon/insult-ai/insult-ai) (Bright Data Web Data UNLOCKED hackathon): adversarial reasoning over live web data, tiered provenance receipts, plan-before-act transparency, and clinical guardrails.

**Insult AI cross-examined claims. Activist OS coordinates evidence-backed action.**

## License

MIT
