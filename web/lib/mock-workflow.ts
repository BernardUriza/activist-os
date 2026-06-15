import type { WorkflowHistory } from "./api";

// Ported from the committed free-intelligence/apps/activist-os /demo cold-open
// (0cdbcf6c / 33175023). Copy is the old mock's, not invented — adapted only to
// this app's HandoffType (the generic "handoff" + the four terminal types).
export const MOCK_DEFAULT_CONCERN =
  "Cafe Verde claims its packaging is compostable, but the local waste facility does not accept compostable packaging.";

export const MOCK_WORKFLOW_HISTORY: WorkflowHistory = {
  run_id: "cold-open",
  status: "completed",
  transport: "local",
  veto_loop: { observed: true, veto_index: 2, approved_index: 4 },
  handoffs: [
    { index: 0, from_agent: "evidence", to_agent: "campaign", type: "handoff", summary: "handoff: evidence → campaign", timestamp: "", virtual: false },
    { index: 1, from_agent: "campaign", to_agent: "safety", type: "handoff", summary: "handoff: campaign → safety", timestamp: "", virtual: false },
    { index: 2, from_agent: "safety", to_agent: "campaign", type: "safety_veto", summary: "safety veto: safety → campaign", timestamp: "", virtual: false },
    { index: 3, from_agent: "campaign", to_agent: "safety", type: "handoff", summary: "handoff: campaign → safety", timestamp: "", virtual: false },
    { index: 4, from_agent: "safety", to_agent: "outreach", type: "safety_approved", summary: "safety approved: safety → outreach", timestamp: "", virtual: false },
    { index: 5, from_agent: "outreach", to_agent: "coordinator", type: "handoff", summary: "handoff: outreach → coordinator", timestamp: "", virtual: false },
    { index: 6, from_agent: "coordinator", to_agent: "reporter", type: "tasks_ready", summary: "tasks ready: coordinator → reporter", timestamp: "", virtual: true },
    { index: 7, from_agent: "reporter", to_agent: "system", type: "packet_ready", summary: "packet ready: reporter → system", timestamp: "", virtual: true },
  ],
  artifacts: {
    evidence_brief: {
      title: "Restaurant X claims 100% compostable packaging, but local waste systems do not process it.",
      summary: "3 claims verified — 2 usable in campaign, 4 sources with provenance tiers attached.",
      claims_count: 3,
      sources_count: 4,
    },
    safety_review: {
      veto_observed: true,
      approved: true,
      draft_text: "Restaurant X is lying to its customers about eco-friendly packaging.",
      veto_reason: "defamation: unsupported accusation against a named target — blocked.",
      rewritten_text:
        "Available evidence does not support the restaurant's 'compostable' claim under local disposal conditions.",
    },
    campaign_packet: {
      reporter_virtual: true,
      outreach_assets_count: 3,
      volunteer_tasks_count: 4,
      provenance_items_count: 4,
      title: "Campaign packet — compostable packaging claim",
      summary: "Assembled from 8 coordinated handoffs; safety audit log included (approved).",
    },
  },
};
