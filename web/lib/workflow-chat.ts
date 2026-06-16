import type { ChatMessage } from "@free-intelligence/core";

import type { AgentName, WorkflowHistory } from "./api";
import type { StreamEvent } from "../components/app/LiveEventLog";
import {
  messagesFromEvents,
  messagesFromHistory,
  type AgentMessage,
} from "./workflow-presentation";

export type AgentSeverity = "critical" | "approved" | "info";

export interface AgentChatMetadata {
  agent: AgentName;
  from: AgentName;
  to: AgentName;
  tag: string;
  virtual: boolean;
  index: number;
  severity: AgentSeverity;
}

export function severityForTag(tag: string): AgentSeverity {
  if (tag === "SAFETY_VETO") return "critical";
  if (tag === "SAFETY_APPROVED") return "approved";
  return "info";
}

function toChatMessage(m: AgentMessage): ChatMessage {
  const metadata: AgentChatMetadata = {
    agent: m.from,
    from: m.from,
    to: m.to,
    tag: m.tag,
    virtual: m.virtual,
    index: m.index,
    severity: severityForTag(m.tag),
  };
  return {
    id: `handoff-${m.index}`,
    role: "assistant",
    content: m.body,
    timestamp: "",
    metadata: metadata as unknown as Record<string, unknown>,
  };
}

export function chatMessagesFromHistory(history: WorkflowHistory): ChatMessage[] {
  return messagesFromHistory(history).map(toChatMessage);
}

export function chatMessagesFromEvents(events: StreamEvent[]): ChatMessage[] {
  return messagesFromEvents(events).map(toChatMessage);
}
