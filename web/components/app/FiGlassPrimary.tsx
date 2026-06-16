"use client";

/**
 * FiGlassPrimary — the 5C primary surface for /app: the fi-glass conversation
 * is the main column (chat + composer drive the workflow), the audited artifacts
 * (safety gate, evidence brief, campaign packet) ride a side rail off the SAME
 * agent run. The legacy dashboard is preserved at /app?dashboard=1 until parity
 * is proven; nothing here deletes it.
 */

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
    <main className="mx-auto max-w-6xl px-4 py-8">
      <header className="mb-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/branding/emblem.png"
              alt="Activist OS"
              width={40}
              height={40}
              className="h-10 w-10 rounded-xl"
            />
            <div>
              <h1 className="text-2xl font-bold leading-none text-zinc-100">Activist OS</h1>
              <p className="mt-0.5 text-xs text-app-muted">Safe civic advocacy workflows</p>
            </div>
          </div>
          <span className="font-mono text-xs text-app-muted">
            API {getApiBaseUrl()}
            {agent.runId ? ` · run ${agent.runId.slice(0, 8)}` : ""}
          </span>
        </div>
        <p className="mt-2 text-sm text-app-muted">
          Coordinate evidence, campaign strategy, safety review, outreach, and action planning in one
          governed workflow — every public action passes a safety gate, and every gate decision is on
          the record.
        </p>
        <div className="mt-3">
          <SemanticStatusBar mode={agent.mode} history={agent.history} />
        </div>
        {agent.error && <p className="mt-2 text-sm text-app-veto">{agent.error}</p>}
      </header>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <FiGlassConversation agent={agent} />
        </div>
        <aside className="space-y-4">
          <SafetyGateCard review={review} />
          <EvidenceBriefCard brief={evidence} />
          <CampaignPacketCard packet={packet} />
        </aside>
      </div>

      <footer className="mt-10 flex flex-wrap items-center justify-between gap-3 border-t border-app-border/60 pt-5">
        <div className="flex items-center gap-2.5">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/branding/emblem.png" alt="Activist OS" className="h-6 w-6 rounded opacity-90" />
          <span className="text-xs text-app-muted">Evidence. Coordination. Safety.</span>
        </div>
        <span className="font-mono text-[11px] text-app-muted">Activist OS · Free Intelligence</span>
      </footer>
    </main>
  );
}
