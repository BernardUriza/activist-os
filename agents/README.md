# Agents

One directory per agent. Each `SPEC.md` defines: role, input/output contract, guardrails,
and the draft role prompt. The contracts in [`../contracts/`](../contracts/) are the
source of truth for every handoff — agents exchange these payloads through Band.

Flow: EVIDENCE → CAMPAIGN ⇄ SAFETY (veto loop) → OUTREACH + COORDINATOR → REPORTER.
