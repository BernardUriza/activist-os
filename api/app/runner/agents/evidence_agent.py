"""
EvidenceAgent — finds and verifies claims.

Input:  WorkflowRun.concern (UserConcern)
Output: WorkflowRun.evidence_brief (EvidenceBrief)

Stub: returns deterministic evidence for the greenwashing smoke-test case.
Real implementation: uses fi-runner + Bright Data web scraping + Claude to
fetch and verify sources against provenance tiers.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.models import (
    AgentName, ClaimVerdict, EvidenceBrief, EvidenceClaim,
    EvidenceSource, EventType, ProvenanceTier, WorkflowRun, WorkflowStatus,
)
from .base_agent import BaseAgent


class EvidenceAgent(BaseAgent):
    name = AgentName.EVIDENCE

    async def run(self, run: WorkflowRun) -> WorkflowRun:
        run.set_status(WorkflowStatus.EVIDENCE_RUNNING)
        run.add_event(self._event(run, EventType.AGENT_STARTED, "Evidence agent started — verifying claims"))

        brief = EvidenceBrief(
            concern=run.concern.text,
            claims=[
                EvidenceClaim(
                    statement="The restaurant uses packaging labeled '100% compostable' that local waste infrastructure cannot process.",
                    verdict=ClaimVerdict.SUPPORTED,
                    confidence=0.87,
                    usable_in_campaign=True,
                    sources=[
                        EvidenceSource(
                            url="https://example.com/municipal-waste-report-2025",
                            title="Municipal Solid Waste Report 2025",
                            provenance_tier=ProvenanceTier.FETCHED_FULLTEXT,
                            quote="Industrial compostable packaging requires processing at 60°C for 12 weeks — conditions not met by any local facility.",
                            retrieved_at=datetime.now(timezone.utc),
                        ),
                        EvidenceSource(
                            url="https://example.com/supplier-certification",
                            title="Supplier certification page",
                            provenance_tier=ProvenanceTier.COMPANY_SOURCE,
                            quote="Certified compostable under EN 13432 — requires industrial composting facility.",
                            retrieved_at=datetime.now(timezone.utc),
                        ),
                    ],
                ),
                EvidenceClaim(
                    statement="The restaurant's menu claims the packaging is eco-friendly without qualification.",
                    verdict=ClaimVerdict.SUPPORTED,
                    confidence=0.95,
                    usable_in_campaign=True,
                    sources=[
                        EvidenceSource(
                            url="https://example.com/restaurant-menu",
                            title="Restaurant menu — archived",
                            provenance_tier=ProvenanceTier.FETCHED_FULLTEXT,
                            quote="All packaging is 100% eco-friendly and compostable.",
                            retrieved_at=datetime.now(timezone.utc),
                        ),
                    ],
                ),
            ],
        )

        run.evidence_brief = brief
        run.add_event(self._event(
            run, EventType.AGENT_COMPLETED,
            f"Evidence brief produced — {len(brief.claims)} claims verified",
            {"claims_count": len(brief.claims), "supported": sum(1 for c in brief.claims if c.verdict == ClaimVerdict.SUPPORTED)},
        ))
        return run
