"""
ReporterAgent — assembles the final CampaignPacket with full provenance and audit trail.

The full audit trail ships inside the packet — including rejections.
Governance that only shows its approvals is marketing.

Input:  all prior WorkflowRun fields
Output: WorkflowRun.campaign_packet (CampaignPacket)
"""
from __future__ import annotations

from app.models import (
    AgentName, CampaignPacket, EventType,
    WorkflowRun, WorkflowStatus,
)
from .base_agent import BaseAgent


class ReporterAgent(BaseAgent):
    name = AgentName.REPORTER

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        run.set_status(WorkflowStatus.REPORTER_RUNNING)
        run.add_event(self._event(run, EventType.AGENT_STARTED, "Reporter agent assembling campaign packet"))

        assert run.evidence_brief is not None
        assert run.campaign_plan is not None
        assert run.safety_verdict is not None
        assert run.outreach_pack is not None
        assert run.task_board is not None

        run.campaign_packet = CampaignPacket(
            run_id=run.run_id,
            concern=run.concern.text,
            evidence_brief=run.evidence_brief,
            campaign_plan=run.campaign_plan,
            safety_verdict=run.safety_verdict,
            outreach_pack=run.outreach_pack,
            task_board=run.task_board,
            audit_events=list(run.audit_events),
        )

        run.set_status(WorkflowStatus.COMPLETED)
        run.add_event(self._event(
            run, EventType.WORKFLOW_COMPLETED,
            "Campaign packet assembled and ready for human review",
            {
                "claims": len(run.evidence_brief.claims),
                "outreach_assets": len(run.outreach_pack.assets),
                "tasks": len(run.task_board.tasks),
                "veto_count": run.veto_count,
                "audit_events": len(run.audit_events),
            },
        ))
        return run
