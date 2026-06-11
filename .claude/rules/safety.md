# Safety — the gate is the product

Analog of insult-ai's `clinical.md`, adapted: there the persona pivots on
crisis signals; here an entire agent holds veto power over public action.

## The doctrine

**Attack the pattern, never the person.** Campaigns target practices,
policies, and corporate claims — never private individuals. A store
manager's name in a flyer is a doxxing fail even if the greenwashing is
real.

## The five checks (every plan, every revision)

| Check | Fails when |
|---|---|
| `defamation` | a public claim rests on `partial`/`unsupported` evidence, or overstates a `supported` one |
| `doxxing` | personal data of any private individual appears in any artifact |
| `harassment` | an action targets a person rather than a pattern, or enables pile-ons |
| `unsupported_claims` | narrative/copy uses a claim with `usable_in_campaign: false` |
| `escalation` | any action beyond lawful, nonviolent organizing |

## Veto semantics (non-negotiable)

- `approved` is the ONLY state that unlocks OUTREACH and COORDINATOR.
- `needs_revision` returns to CAMPAIGN with precise `blocked_items` — never
  vague "tone it down" notes. Each blocked item names the target and reason.
- `blocked` kills the plan revision entirely (e.g., the core claim is
  unsupported — no amount of rewording fixes that).
- **When in doubt, do not approve.** A false negative costs a revision
  cycle; a false positive costs a community group a lawsuit.

## The audit log is complete or it is worthless

EVERY verdict — including rejections and the reasoning behind them — lands
in `safety_audit_log` and ships inside the campaign packet. Governance that
only shows its approvals is marketing. The rejected revision in the demo is
the proof the gate is real.

## Language discipline

- "legal-risk-aware by design" — always.
- "legal immunity", "lawsuit-proof", "legally safe" — never. No system
  grants that, and claiming it in a regulated-workflows track is
  self-disqualifying.

## Sensitive escalations

If a submitted concern signals crisis (self-harm, violence, immediate
danger), the system abandons campaign mode and responds with grounded
support and resources — engine behavior inherited from Insult AI's clinical
guardrails. Activism tooling must not launder emergencies into campaigns.
