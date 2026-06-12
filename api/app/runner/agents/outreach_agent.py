"""
OutreachAgent — drafts posts, emails, flyers, and public copy.
Only runs after SafetyAgent approves. Output language mirrors the concern language.

Input:  WorkflowRun.campaign_plan (approved)
Output: WorkflowRun.outreach_pack (OutreachPack)
"""
from __future__ import annotations

from app.models import (
    AgentName, EventType, OutreachAsset, OutreachPack,
    WorkflowRun, WorkflowStatus,
)
from .base_agent import BaseAgent


class OutreachAgent(BaseAgent):
    name = AgentName.OUTREACH

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        run.set_status(WorkflowStatus.OUTREACH_RUNNING)
        run.add_event(self._event(run, EventType.AGENT_STARTED, "Outreach agent drafting copy"))

        assert run.campaign_plan is not None
        lang = "en"  # TODO: detect from UserConcern.text language

        run.outreach_pack = OutreachPack(
            run_id=run.run_id,
            assets=[
                OutreachAsset(
                    asset_type="social_post",
                    channel="instagram",
                    language=lang,
                    content=(
                        "Did you know? Packaging labeled '100% compostable' often requires "
                        "industrial composting facilities — which our city doesn't have. "
                        "Ask your local restaurant what happens to their packaging. "
                        "#EcoLabeling #GreenWashing #KnowYourWaste"
                    ),
                ),
                OutreachAsset(
                    asset_type="email",
                    channel="direct",
                    language=lang,
                    content=(
                        "Subject: Request for transparent environmental labeling\n\n"
                        "Dear Management,\n\n"
                        "We appreciate your efforts toward sustainable packaging. "
                        "However, municipal waste data indicates that 'industrially compostable' "
                        "packaging cannot be processed by local facilities. "
                        "We respectfully request that your labeling accurately reflect "
                        "the disposal conditions available to customers.\n\n"
                        "Sincerely,\nLocal Environmental Group"
                    ),
                ),
                OutreachAsset(
                    asset_type="flyer",
                    channel="print",
                    language=lang,
                    content=(
                        "THE FACTS ABOUT 'COMPOSTABLE' PACKAGING\n\n"
                        "✓ Industrial composting requires 60°C for 12 weeks\n"
                        "✓ No local facility meets these conditions\n"
                        "✓ This packaging ends up in landfill\n\n"
                        "Source: Municipal Solid Waste Report 2025\n"
                        "Ask us for the evidence."
                    ),
                ),
            ],
        )

        run.add_event(self._event(
            run, EventType.AGENT_COMPLETED,
            f"Outreach pack ready — {len(run.outreach_pack.assets)} assets",
            {"asset_types": [a.asset_type for a in run.outreach_pack.assets]},
        ))
        return run
