"use client";

/**
 * FiGlassConversation — the Activist OS workflow rendered through the canonical
 * fi-glass AgentConversationSurface. Presentational: it takes a lifted
 * ActivistAgent so the chat surface and an artifacts rail can share ONE agent
 * (one workflow run, one SSE stream). Controlled / external-transcript mode
 * (fi-glass >=1.2.0): the workflow owns the thread (1 send -> 8+ handoff
 * messages), the canonical hook supplies send/turn/error/retry machinery.
 */

import { AgentConversationSurface, useAgentConversation } from "fi-glass/agent";
import "fi-glass/theme.css";
import "fi-glass/glass-chat.css";
import type { ChatMessage } from "@free-intelligence/core";

import type { ActivistAgent } from "../../lib/useActivistAgent";
import type { AgentChatMetadata } from "../../lib/workflow-chat";

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

function metaOf(m: ChatMessage): AgentChatMetadata | null {
  return (m.metadata as AgentChatMetadata | undefined) ?? null;
}

export function FiGlassConversation({ agent }: { agent: ActivistAgent }) {
  const conversation = useAgentConversation(agent, { externalMessages: agent.messages });

  return (
    <AgentConversationSurface
        conversation={conversation}
        layout="contained"
        composerPlaceholder="Describe a civic concern — the band coordinates it live…"
        newChatLabel="New concern"
        composerBoxClassName="glass-chat-composer"
        composerTextareaClassName="glass-chat-composer-input"
        messageBubbleClassName={(m) => {
          if (m.role === "user") return "glass-chat-bubble-user";
          const md = metaOf(m);
          if (md?.severity === "critical") return "glass-chat-bubble-veto";
          if (md?.severity === "approved") return "glass-chat-bubble-approved";
          return "glass-chat-bubble-assistant";
        }}
        renderHeader={(m) => {
          const md = metaOf(m);
          if (!md) return null;
          return (
            <span className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-zinc-100">{cap(md.from)}</span>
              {md.virtual ? (
                <span className="font-mono text-[11px] text-app-virtual">
                  [virtual · backend event]
                </span>
              ) : (
                <span className="font-mono text-[11px] text-app-brand">@{cap(md.to)}</span>
              )}
            </span>
          );
        }}
        renderBadge={(m) => {
          const md = metaOf(m);
          if (!md) return null;
          if (md.severity === "critical")
            return (
              <span className="rounded border border-app-veto/50 bg-app-veto/10 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-app-veto">
                VETO
              </span>
            );
          if (md.severity === "approved")
            return (
              <span className="rounded border border-app-approve/50 bg-app-approve/10 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-app-approve">
                APPROVED
              </span>
            );
          return (
            <span className="font-mono text-[10px] uppercase tracking-wide text-app-muted">
              {md.tag}
            </span>
          );
        }}
      />
  );
}
