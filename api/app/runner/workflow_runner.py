"""
WorkflowRunner — orchestrates the 6-agent chain through the transport layer.

Flow: Evidence → Campaign ⇄ Safety (veto loop) → Outreach → Coordinator → Reporter

The veto loop is the architectural centerpiece and must never be cut.
Safety can veto up to MAX_VETO_CYCLES times before the run is blocked.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.models import (
    AgentHandoff, AgentName, AuditEvent, EventType,
    HandoffType, SafetyStatus, WorkflowRun, WorkflowStatus,
)
from .agents import (
    CampaignAgent, CoordinatorAgent, EvidenceAgent,
    OutreachAgent, ReporterAgent, SafetyAgent,
)
from .transports.base import Transport

MAX_VETO_CYCLES = 3


class WorkflowRunner:

    def __init__(self, transport: Transport) -> None:
        self._transport = transport
        self._evidence = EvidenceAgent()
        self._campaign = CampaignAgent()
        self._safety = SafetyAgent()
        self._outreach = OutreachAgent()
        self._coordinator = CoordinatorAgent()
        self._reporter = ReporterAgent()

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        await self._emit(run, AgentName.SYSTEM, EventType.WORKFLOW_STARTED,
                         f"Workflow started for concern: {run.concern.text[:80]}…")
        await self._save(run)

        # 1. Evidence
        run = await self._evidence.run(run)
        await self._handoff(run, AgentName.EVIDENCE, AgentName.CAMPAIGN,
                            HandoffType.EVIDENCE_COMPLETE, run.evidence_brief.model_dump())
        await self._save(run)

        # 2. Campaign ⇄ Safety veto loop
        while True:
            run = await self._campaign.run(run)
            await self._handoff(run, AgentName.CAMPAIGN, AgentName.SAFETY,
                                HandoffType.SAFETY_REQUEST, run.campaign_plan.model_dump())
            await self._save(run)

            run = await self._safety.run(run)

            if run.safety_verdict.status == SafetyStatus.APPROVED:
                await self._handoff(run, AgentName.SAFETY, AgentName.OUTREACH,
                                    HandoffType.SAFETY_APPROVED, run.safety_verdict.model_dump())
                break

            if run.safety_verdict.status == SafetyStatus.BLOCKED:
                run.set_status(WorkflowStatus.BLOCKED)
                await self._emit(run, AgentName.SAFETY, EventType.WORKFLOW_BLOCKED,
                                 "Run blocked — core claim unsupported; no revision can fix it.")
                await self._save(run)
                return run

            # NEEDS_REVISION
            if run.veto_count >= MAX_VETO_CYCLES:
                run.set_status(WorkflowStatus.BLOCKED)
                await self._emit(run, AgentName.SAFETY, EventType.WORKFLOW_BLOCKED,
                                 f"Run blocked — exceeded {MAX_VETO_CYCLES} veto cycles without approval.")
                await self._save(run)
                return run

            await self._handoff(run, AgentName.SAFETY, AgentName.CAMPAIGN,
                                HandoffType.SAFETY_VETO, run.safety_verdict.model_dump())
            run.set_status(WorkflowStatus.SAFETY_REVISION)
            await self._save(run)

        # 3. Outreach
        run = await self._outreach.run(run)
        await self._handoff(run, AgentName.OUTREACH, AgentName.COORDINATOR,
                            HandoffType.OUTREACH_READY, run.outreach_pack.model_dump())
        await self._save(run)

        # 4. Coordinator
        run = await self._coordinator.run(run)
        await self._handoff(run, AgentName.COORDINATOR, AgentName.REPORTER,
                            HandoffType.TASKS_READY, run.task_board.model_dump())
        await self._save(run)

        # 5. Reporter — assemble final packet
        run = await self._reporter.run(run)
        await self._handoff(run, AgentName.REPORTER, AgentName.SYSTEM,
                            HandoffType.PACKET_READY, {"run_id": run.run_id})
        await self._save(run)

        return run

    async def _handoff(
        self, run: WorkflowRun,
        from_agent: AgentName, to_agent: AgentName,
        htype: HandoffType, payload: dict,
    ) -> None:
        handoff = AgentHandoff(
            run_id=run.run_id,
            from_agent=from_agent,
            to_agent=to_agent,
            type=htype,
            payload=payload,
        )
        await self._transport.send_handoff(handoff)
        run.add_event(AuditEvent(
            run_id=run.run_id,
            event_type=EventType.HANDOFF_SENT,
            agent=from_agent,
            summary=f"{from_agent} → {to_agent}: {htype}",
            handoff_ref=handoff.handoff_id,
            occurred_at=datetime.now(timezone.utc),
        ))

    async def _emit(self, run: WorkflowRun, agent: AgentName, etype: EventType, summary: str) -> None:
        event = AuditEvent(
            run_id=run.run_id, event_type=etype, agent=agent, summary=summary,
            occurred_at=datetime.now(timezone.utc),
        )
        run.add_event(event)
        await self._transport.record_event(event)

    async def _save(self, run: WorkflowRun) -> None:
        await self._transport.set_context(run.run_id, run.model_dump(mode="json"))
