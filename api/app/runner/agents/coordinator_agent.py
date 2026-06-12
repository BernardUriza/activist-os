"""
CoordinatorAgent — converts the approved strategy into a concrete volunteer task board.

Input:  WorkflowRun.outreach_pack + campaign_plan
Output: WorkflowRun.task_board (TaskBoard)
"""
from __future__ import annotations

from app.models import (
    AgentName, EventType, TaskBoard, VolunteerTask,
    WorkflowRun, WorkflowStatus,
)
from .base_agent import BaseAgent


class CoordinatorAgent(BaseAgent):
    name = AgentName.COORDINATOR

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        run.set_status(WorkflowStatus.COORDINATOR_RUNNING)
        run.add_event(self._event(run, EventType.AGENT_STARTED, "Coordinator agent building task board"))

        assert run.outreach_pack is not None

        run.task_board = TaskBoard(
            run_id=run.run_id,
            tasks=[
                VolunteerTask(
                    title="Print and distribute flyers",
                    description="Print 100 copies of the flyer and distribute near the restaurant entrance during lunch hours (12–2 PM).",
                    channel="print",
                    estimated_hours=3.0,
                    materials_needed=["Printer", "100 sheets A5 paper"],
                ),
                VolunteerTask(
                    title="Post on neighbourhood social media groups",
                    description="Share the approved social post on local Facebook groups, Nextdoor, and Instagram. Link to evidence summary page.",
                    channel="social_media",
                    estimated_hours=0.5,
                    materials_needed=["Approved social post copy", "Evidence summary link"],
                ),
                VolunteerTask(
                    title="Send formal letter to restaurant management",
                    description="Email the approved letter to the restaurant's public contact address. BCC the group coordinator.",
                    channel="email",
                    estimated_hours=0.5,
                    materials_needed=["Approved email copy", "Restaurant contact email"],
                ),
                VolunteerTask(
                    title="Document response and update evidence log",
                    description="If the restaurant responds, log the response date and content. Update the campaign packet with any new information.",
                    channel="documentation",
                    estimated_hours=1.0,
                    materials_needed=["Campaign packet access"],
                ),
            ],
        )

        run.add_event(self._event(
            run, EventType.AGENT_COMPLETED,
            f"Task board ready — {len(run.task_board.tasks)} volunteer tasks",
            {"task_count": len(run.task_board.tasks)},
        ))
        return run
