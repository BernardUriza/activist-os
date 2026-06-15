import type { AgentName, HandoffType, HandoffView, WorkflowHistory } from "./api";
import type { StreamEvent } from "../components/app/LiveEventLog";

export interface AgentMessage {
  index: number;
  from: AgentName;
  to: AgentName;
  tag: string;
  body: string;
  virtual: boolean;
}

const STATE_BLURBS: Record<string, string> = {
  EVIDENCE_COMPLETE: "Evidence brief ready — claims verified with provenance tiers.",
  SAFETY_REQUEST: "Campaign plan submitted for the five safety checks.",
  SAFETY_VETO: "VETO — blocked items returned to Campaign with precise reasons.",
  REVISION_READY: "Revised language prepared — resubmitted for re-review.",
  SAFETY_APPROVED: "APPROVED — the only status that unlocks public action.",
  OUTREACH_READY: "Outreach pack drafted in the community's language.",
  TASKS_READY: "Volunteer task board assembled.",
  PACKET_READY: "Campaign packet compiled — audit log included.",
};

function deriveTag(
  from: AgentName,
  to: AgentName,
  type: HandoffType,
  index: number,
  vetoIndex: number | null,
): string {
  if (type === "safety_veto") return "SAFETY_VETO";
  if (type === "safety_approved") return "SAFETY_APPROVED";
  if (type === "tasks_ready") return "TASKS_READY";
  if (type === "packet_ready") return "PACKET_READY";
  if (from === "evidence" && to === "campaign") return "EVIDENCE_COMPLETE";
  if (from === "campaign" && to === "safety") {
    return vetoIndex !== null && index > vetoIndex ? "REVISION_READY" : "SAFETY_REQUEST";
  }
  if (from === "outreach" && to === "coordinator") return "OUTREACH_READY";
  return "HANDOFF";
}

export function messagesFromHistory(history: WorkflowHistory): AgentMessage[] {
  const vetoIndex = history.veto_loop?.veto_index ?? null;
  return history.handoffs.map((h: HandoffView) => {
    const tag = deriveTag(h.from_agent, h.to_agent, h.type, h.index, vetoIndex);
    return {
      index: h.index,
      from: h.from_agent,
      to: h.to_agent,
      tag,
      body: STATE_BLURBS[tag] || h.summary || "",
      virtual: h.virtual,
    };
  });
}

export function messagesFromEvents(events: StreamEvent[]): AgentMessage[] {
  const vetoEvent = events.find(
    (e) => e.event_type === "handoff_sent" && e.type === "safety_veto",
  );
  const vetoIndex = vetoEvent?.index ?? null;
  return events
    .filter((e) => e.event_type === "handoff_sent" && e.from_agent && e.to_agent)
    .map((e) => {
      const from = e.from_agent as AgentName;
      const to = e.to_agent as AgentName;
      const type = (e.type as HandoffType) ?? "handoff";
      const index = e.index ?? 0;
      const tag = deriveTag(from, to, type, index, vetoIndex);
      return { index, from, to, tag, body: STATE_BLURBS[tag] || "", virtual: false };
    });
}
