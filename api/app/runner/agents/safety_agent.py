"""
SafetyAgent — the veto gate. Runs the five checks on every campaign plan.
'approved' is the ONLY state that unlocks OUTREACH and COORDINATOR.

The five checks (safety.md):
  defamation       — public claim rests on partial/unsupported evidence, or overstates
  doxxing          — personal data of any private individual
  harassment       — action targets a person not a pattern
  unsupported_claims — narrative uses a claim with usable_in_campaign: False
  escalation       — any action beyond lawful, nonviolent organizing

When in doubt, do not approve. A false negative costs a revision cycle;
a false positive costs a lawsuit.
"""
from __future__ import annotations

from app.models import (
    AgentName, BlockedItem, EventType, SafetyStatus, SafetyVerdict,
    WorkflowRun, WorkflowStatus,
)
from .base_agent import BaseAgent

_UNSUPPORTED_PHRASES = [
    "is lying",
    "is deceiving",
    "is a fraud",
    "is criminal",
    "is scamming",
]


class SafetyAgent(BaseAgent):
    name = AgentName.SAFETY

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        run.set_status(WorkflowStatus.SAFETY_REVIEW)
        run.add_event(self._event(run, EventType.AGENT_STARTED, "Safety agent reviewing campaign plan"))

        assert run.campaign_plan is not None, "SafetyAgent requires campaign_plan"
        assert run.evidence_brief is not None, "SafetyAgent requires evidence_brief"

        blocked: list[BlockedItem] = []
        narrative_lower = run.campaign_plan.narrative.lower()

        # Check: unsupported accusation / defamation
        for phrase in _UNSUPPORTED_PHRASES:
            if phrase in narrative_lower:
                blocked.append(BlockedItem(
                    check="defamation",
                    description=(
                        f"Narrative contains accusatory language ('{phrase}') not supported by evidence. "
                        "Rewrite using factual, evidence-backed framing."
                    ),
                    target="campaign narrative",
                ))
                break

        # Check: unsupported claims used in narrative
        unusable = [c for c in run.evidence_brief.claims if not c.usable_in_campaign]
        if unusable:
            blocked.append(BlockedItem(
                check="unsupported_claims",
                description=f"{len(unusable)} claim(s) marked usable_in_campaign=False appear in scope.",
                target="evidence_brief.claims",
            ))

        # Check: doxxing (private individual names — simple heuristic for stub)
        # Real implementation: NER + entity classification
        doxxing_signals = ["home address", "personal phone", "private email"]
        for signal in doxxing_signals:
            if signal in narrative_lower:
                blocked.append(BlockedItem(
                    check="doxxing",
                    description=f"Potential private data found: '{signal}'.",
                    target="campaign narrative",
                ))

        if blocked:
            status = SafetyStatus.NEEDS_REVISION
            run.veto_count += 1
            event_type = EventType.SAFETY_VETO
            summary = f"VETO (#{run.veto_count}) — {len(blocked)} issue(s) found"
        else:
            status = SafetyStatus.APPROVED
            event_type = EventType.SAFETY_APPROVED
            summary = "Campaign approved — all five checks passed"

        run.safety_verdict = SafetyVerdict(
            run_id=run.run_id,
            status=status,
            blocked_items=blocked,
            reviewer_notes=summary,
        )

        run.add_event(self._event(
            run, event_type, summary,
            {"status": status, "blocked_count": len(blocked), "veto_count": run.veto_count},
        ))
        return run
