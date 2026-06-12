"""
CampaignAgent — turns verified evidence into a campaign narrative.

Input:  WorkflowRun.evidence_brief (EvidenceBrief)
Output: WorkflowRun.campaign_plan (CampaignPlan)

Never goes beyond what the evidence supports. On Safety veto, increments
revision counter and rewrites with the blocked_items feedback applied.
"""
from __future__ import annotations

from app.models import (
    AgentName, CampaignAction, CampaignPlan,
    EventType, SafetyStatus, WorkflowRun, WorkflowStatus,
)
from .base_agent import BaseAgent

_UNSAFE_DRAFT = "Restaurant X is lying to its customers about eco-friendly packaging."
_SAFE_DRAFT = (
    "Available evidence does not support the restaurant's 'compostable' claim "
    "under local disposal conditions. Municipal waste infrastructure cannot "
    "process industrial-grade compostable packaging. Residents deserve accurate "
    "information before making purchasing decisions based on environmental claims."
)


class CampaignAgent(BaseAgent):
    name = AgentName.CAMPAIGN

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        run.set_status(WorkflowStatus.CAMPAIGN_RUNNING)
        run.add_event(self._event(run, EventType.AGENT_STARTED, "Campaign agent started"))

        assert run.evidence_brief is not None, "CampaignAgent requires evidence_brief"

        prior_verdict = run.safety_verdict
        is_revision = prior_verdict is not None and prior_verdict.status == SafetyStatus.NEEDS_REVISION
        revision_num = (run.campaign_plan.revision + 1) if run.campaign_plan else 0

        if is_revision:
            # Apply Safety feedback — use the evidence-backed, factual narrative
            narrative = _SAFE_DRAFT
            run.add_event(self._event(
                run, EventType.CAMPAIGN_REWRITTEN,
                f"Campaign rewritten (revision {revision_num}) applying Safety feedback",
                {"blocked_items": [b.model_dump() for b in prior_verdict.blocked_items]},
            ))
        else:
            # First draft — intentionally contains unsupported accusation for demo veto
            narrative = _UNSAFE_DRAFT

        run.campaign_plan = CampaignPlan(
            run_id=run.run_id,
            narrative=narrative,
            key_message=(
                "Demand transparent environmental labeling from local businesses."
                if is_revision else _UNSAFE_DRAFT
            ),
            actions=[
                CampaignAction(
                    description="Distribute flyers at the restaurant entrance explaining the composting infrastructure gap.",
                    channel="flyer",
                    target_audience="Restaurant customers",
                ),
                CampaignAction(
                    description="Post on local neighbourhood social media groups with the evidence summary.",
                    channel="social_media",
                    target_audience="Local community",
                ),
                CampaignAction(
                    description="Send a formal letter to the restaurant management requesting label correction.",
                    channel="email",
                    target_audience="Restaurant management",
                ),
            ],
            revision=revision_num,
        )

        run.add_event(self._event(
            run, EventType.AGENT_COMPLETED,
            f"Campaign plan ready (revision {revision_num})",
            {"revision": revision_num, "is_revision": is_revision},
        ))
        return run
