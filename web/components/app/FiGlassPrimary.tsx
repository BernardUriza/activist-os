"use client";

/**
 * FiGlassPrimary — the 5C primary surface for /app, rebuilt as a THIN consumer
 * over fi-glass's AgentWorkspaceShell (viewport-locked layout owned upstream).
 * The consumer only wires data/brand/slots: a brand header, the contained
 * conversation, an artifacts rail (safety gate / evidence brief / campaign
 * packet) off the SAME run, and a footer. No layout/scroll/glass treatment
 * lives here — that is fi-glass. The legacy dashboard stays at /app?dashboard=1.
 */

import { AgentWorkspaceShell } from "fi-glass/agent";

import { getApiBaseUrl } from "../../lib/api";
import { useActivistAgent } from "../../lib/useActivistAgent";
import { FiGlassConversation } from "./FiGlassConversation";
import { SafetyGateCard } from "./SafetyGateCard";
import { EvidenceBriefCard } from "./EvidenceBriefCard";
import { CampaignPacketCard } from "./CampaignPacketCard";
import { SemanticStatusBar } from "./SemanticStatusBar";

export function FiGlassPrimary({ runId }: { runId?: string | null }) {
  const agent = useActivistAgent({ initialRunId: runId });
  const review = agent.history?.artifacts.safety_review ?? null;
  const evidence = agent.history?.artifacts.evidence_brief ?? null;
  const packet = agent.history?.artifacts.campaign_packet ?? null;

  return (
    <AgentWorkspaceShell
      visual="aurora"
      density="comfortable"
      header={
        <header className="flex flex-col gap-2 border-b border-app-border/60 px-5 py-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/branding/emblem.png"
                alt="Activist OS"
                width={36}
                height={36}
                className="h-9 w-9 rounded-xl"
              />
              <div>
                <h1 className="text-lg font-bold leading-none text-zinc-100">Activist OS</h1>
                <p className="mt-0.5 text-[11px] text-app-muted">
                  Governed civic advocacy — every public action passes a safety gate.
                </p>
              </div>
            </div>
            <span className="font-mono text-[11px] text-app-muted">
              API {getApiBaseUrl()}
              {agent.runId ? ` · run ${agent.runId.slice(0, 8)}` : ""}
            </span>
          </div>
          <SemanticStatusBar mode={agent.mode} history={agent.history} />
          {agent.error && <p className="text-sm text-app-veto">{agent.error}</p>}
        </header>
      }
      conversation={<FiGlassConversation agent={agent} />}
      rail={
        <div className="space-y-4 p-4">
          <SafetyGateCard review={review} />
          <EvidenceBriefCard brief={evidence} />
          <CampaignPacketCard packet={packet} />
        </div>
      }
      footer={
        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-app-border/60 px-5 py-2.5">
          <div className="flex items-center gap-2.5">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/branding/emblem.png" alt="Activist OS" className="h-5 w-5 rounded opacity-90" />
            <span className="text-[11px] text-app-muted">Evidence. Coordination. Safety.</span>
          </div>
          <span className="font-mono text-[11px] text-app-muted">Activist OS · Free Intelligence</span>
        </footer>
      }
    />
  );
}
