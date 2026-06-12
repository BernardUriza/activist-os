"""
Smoke test — greenwashing case end-to-end.

Expected path:
  EvidenceBrief created
  CampaignDraft created (unsafe first draft)
  SafetyAgent VETOES unsafe wording → veto_count == 1
  CampaignAgent rewrites
  SafetyAgent APPROVES rewritten draft
  OutreachPack generated
  TaskBoard generated
  Reporter emits CampaignPacket
  audit_events contains the veto and the approval
"""
import pytest

from app.models import SafetyStatus, WorkflowRun, WorkflowStatus
from app.models.contracts import UserConcern
from app.runner.transports.local_transport import LocalTransport
from app.runner.workflow_runner import WorkflowRunner


@pytest.fixture
def concern():
    return UserConcern(
        text=(
            "Restaurant X claims 100% compostable packaging, "
            "but local waste systems do not process it."
        ),
        location="Local city",
        category="greenwashing",
    )


@pytest.mark.asyncio
async def test_workflow_completes(concern):
    transport = LocalTransport()
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=concern)

    result = await runner.run(run)

    assert result.status == WorkflowStatus.COMPLETED, f"Run status: {result.status}, error: {result.error}"


@pytest.mark.asyncio
async def test_evidence_brief_created(concern):
    transport = LocalTransport()
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=concern)

    result = await runner.run(run)

    assert result.evidence_brief is not None
    assert len(result.evidence_brief.claims) >= 1


@pytest.mark.asyncio
async def test_safety_veto_occurs(concern):
    """The veto loop must fire at least once — this is the money shot."""
    transport = LocalTransport()
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=concern)

    result = await runner.run(run)

    assert result.veto_count >= 1, "Safety veto must occur at least once in the demo case"


@pytest.mark.asyncio
async def test_safety_final_approved(concern):
    transport = LocalTransport()
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=concern)

    result = await runner.run(run)

    assert result.safety_verdict is not None
    assert result.safety_verdict.status == SafetyStatus.APPROVED


@pytest.mark.asyncio
async def test_campaign_packet_exists(concern):
    transport = LocalTransport()
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=concern)

    result = await runner.run(run)

    assert result.campaign_packet is not None
    assert len(result.campaign_packet.outreach_pack.assets) >= 1
    assert len(result.campaign_packet.task_board.tasks) >= 1


@pytest.mark.asyncio
async def test_audit_trail_contains_veto_and_approval(concern):
    transport = LocalTransport()
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=concern)

    result = await runner.run(run)

    event_types = [e.event_type for e in result.audit_events]
    assert "safety_veto" in [e.value for e in event_types], "Audit trail must contain a veto"
    assert "safety_approved" in [e.value for e in event_types], "Audit trail must contain an approval"


@pytest.mark.asyncio
async def test_audit_trail_in_packet(concern):
    """Governance that only shows approvals is marketing."""
    transport = LocalTransport()
    runner = WorkflowRunner(transport)
    run = WorkflowRun(concern=concern)

    result = await runner.run(run)

    assert result.campaign_packet is not None
    packet_types = [e.event_type.value for e in result.campaign_packet.audit_events]
    assert "safety_veto" in packet_types, "Rejection must ship inside the campaign packet"
