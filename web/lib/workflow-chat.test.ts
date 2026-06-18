import { describe, it, expect } from "vitest";

import { MOCK_WORKFLOW_HISTORY } from "./mock-workflow";
import type { StreamEvent } from "./api";
import {
  chatMessagesFromEvents,
  chatMessagesFromHistory,
  severityForTag,
  type AgentChatMetadata,
} from "./workflow-chat";

const meta = (m: { metadata?: Record<string, unknown> }) =>
  m.metadata as unknown as AgentChatMetadata;

describe("severityForTag", () => {
  it("maps VETO → critical, APPROVED → approved, everything else → info", () => {
    expect(severityForTag("SAFETY_VETO")).toBe("critical");
    expect(severityForTag("SAFETY_APPROVED")).toBe("approved");
    expect(severityForTag("EVIDENCE_COMPLETE")).toBe("info");
    expect(severityForTag("HANDOFF")).toBe("info");
  });
});

describe("chatMessagesFromHistory — workflow history → ChatMessage[]", () => {
  const messages = chatMessagesFromHistory(MOCK_WORKFLOW_HISTORY);

  it("produces one assistant ChatMessage per handoff (8 for the cold-open)", () => {
    expect(messages).toHaveLength(8);
    expect(messages.every((m) => m.role === "assistant")).toBe(true);
    expect(messages.map((m) => m.id)).toEqual([
      "handoff-0",
      "handoff-1",
      "handoff-2",
      "handoff-3",
      "handoff-4",
      "handoff-5",
      "handoff-6",
      "handoff-7",
    ]);
  });

  it("flags the VETO message as critical", () => {
    const veto = messages.find((m) => meta(m).tag === "SAFETY_VETO");
    expect(veto).toBeDefined();
    expect(meta(veto!).severity).toBe("critical");
    expect(meta(veto!).from).toBe("safety");
    expect(meta(veto!).to).toBe("campaign");
  });

  it("flags the APPROVED message as approved", () => {
    const approved = messages.find((m) => meta(m).tag === "SAFETY_APPROVED");
    expect(approved).toBeDefined();
    expect(meta(approved!).severity).toBe("approved");
  });

  it("carries the virtual flag through to metadata", () => {
    const reporter = messages.find((m) => meta(m).tag === "PACKET_READY");
    expect(meta(reporter!).virtual).toBe(true);
  });
});

describe("chatMessagesFromEvents — live SSE handoffs → ChatMessage[]", () => {
  const events: StreamEvent[] = [
    { event_type: "workflow_started" },
    { event_type: "handoff_sent", index: 0, from_agent: "evidence", to_agent: "campaign", type: "handoff" },
    { event_type: "handoff_sent", index: 1, from_agent: "campaign", to_agent: "safety", type: "handoff" },
    { event_type: "handoff_sent", index: 2, from_agent: "safety", to_agent: "campaign", type: "safety_veto" },
  ];

  it("maps only handoff_sent events, preserving order and severity", () => {
    const messages = chatMessagesFromEvents(events);
    expect(messages).toHaveLength(3);
    expect(meta(messages[2]).severity).toBe("critical");
    expect(meta(messages[0]).tag).toBe("EVIDENCE_COMPLETE");
  });
});
