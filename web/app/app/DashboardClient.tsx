"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Route } from "next";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import {
  getApiBaseUrl,
  getWorkflowEventsUrl,
  getWorkflowHistory,
  startWorkflow,
  WorkflowNotFoundError,
  type WorkflowHistory,
} from "../../lib/api";
import { CampaignPacketCard } from "../../components/app/CampaignPacketCard";
import { CoordinationHistory } from "../../components/app/CoordinationHistory";
import { EvidenceBriefCard } from "../../components/app/EvidenceBriefCard";
import { type StreamEvent } from "../../components/app/LiveEventLog";
import { SafetyGateCard } from "../../components/app/SafetyGateCard";
import { SemanticStatusBar } from "../../components/app/SemanticStatusBar";
import { AgentConversationSurface } from "../../components/app/AgentConversationSurface";
import { FiGlassConversationCanary } from "../../components/app/FiGlassConversationCanary";
import { MOCK_DEFAULT_CONCERN, MOCK_WORKFLOW_HISTORY } from "../../lib/mock-workflow";
import { messagesFromEvents, messagesFromHistory } from "../../lib/workflow-presentation";

type Mode = "IDLE" | "STARTING" | "STREAMING" | "LIVE" | "ERROR" | "MOCK";

export function DashboardClient() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const deepLinkRunId = searchParams.get("run_id");
  const fiGlassCanary = searchParams.get("fi_glass_canary") === "1";

  const [concern, setConcern] = useState(deepLinkRunId ? "" : MOCK_DEFAULT_CONCERN);
  const [mode, setMode] = useState<Mode>(deepLinkRunId ? "IDLE" : "MOCK");
  const [runId, setRunId] = useState<string | null>(null);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [history, setHistory] = useState<WorkflowHistory | null>(
    deepLinkRunId ? null : MOCK_WORKFLOW_HISTORY,
  );
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const esRef = useRef<EventSource | null>(null);
  const openedFor = useRef<string | null>(null);

  const loadHistory = useCallback(async (id: string) => {
    try {
      const data = await getWorkflowHistory(id);
      setHistory(data);
      setMode("LIVE");
    } catch (err) {
      setErrorMsg(
        err instanceof WorkflowNotFoundError
          ? `Run ${id} not found.`
          : `Could not load history: ${(err as Error).message}`,
      );
      setMode("ERROR");
    }
  }, []);

  const openStream = useCallback(
    (id: string) => {
      if (openedFor.current === id) return;
      openedFor.current = id;
      esRef.current?.close();
      setEvents([]);
      setMode("STREAMING");

      const es = new EventSource(getWorkflowEventsUrl(id));
      esRef.current = es;

      es.onmessage = (ev) => {
        let payload: StreamEvent;
        try {
          payload = JSON.parse(ev.data);
        } catch {
          return;
        }
        setEvents((prev) => [...prev, payload]);
        if (payload.event_type === "stream_end") {
          es.close();
          void loadHistory(id);
        }
      };

      es.onerror = () => {
        es.close();
        // SSE dropped before stream_end — fall back to a direct history fetch
        // (never to a mock). If that fails too, loadHistory flips to ERROR.
        if (!history) void loadHistory(id);
      };
    },
    [history, loadHistory],
  );

  const handleRun = useCallback(async () => {
    if (!concern.trim()) return;
    setErrorMsg(null);
    setHistory(null);
    setMode("STARTING");
    try {
      const { run_id } = await startWorkflow({ concern: concern.trim() });
      setRunId(run_id);
      router.replace(`${pathname}?run_id=${encodeURIComponent(run_id)}` as Route, { scroll: false });
      openStream(run_id);
    } catch (err) {
      setErrorMsg(`Could not start workflow: ${(err as Error).message}`);
      setMode("ERROR");
    }
  }, [concern, openStream, pathname, router]);

  useEffect(() => {
    if (deepLinkRunId && openedFor.current !== deepLinkRunId) {
      setRunId(deepLinkRunId);
      openStream(deepLinkRunId);
    }
  }, [deepLinkRunId, openStream]);

  useEffect(() => () => esRef.current?.close(), []);

  const review = history?.artifacts.safety_review ?? null;
  const evidence = history?.artifacts.evidence_brief ?? null;
  const packet = history?.artifacts.campaign_packet ?? null;
  const messages = history ? messagesFromHistory(history) : messagesFromEvents(events);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      {fiGlassCanary && (
        <section className="mb-6 rounded-xl border border-app-brand/40 bg-app-brand/5 p-4">
          <p className="mb-3 font-mono text-[11px] uppercase tracking-wide text-app-brand">
            fi-glass canary · preview surface (the dashboard below is unchanged)
          </p>
          <FiGlassConversationCanary runId={deepLinkRunId} />
        </section>
      )}
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
            {runId ? ` · run ${runId.slice(0, 8)}` : ""}
          </span>
        </div>
        <p className="mt-2 text-sm text-app-muted">
          Coordinate evidence, campaign strategy, safety review, outreach, and action planning in one
          governed workflow — every public action passes a safety gate, and every gate decision is on
          the record.
        </p>
        <div className="mt-3">
          <SemanticStatusBar mode={mode} history={history} />
        </div>
      </header>

      <section className="aos-glass-primary mb-6 rounded-xl p-4">
        <label htmlFor="concern" className="mb-1 block text-sm font-medium text-zinc-200">
          Describe a civic concern
        </label>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            id="concern"
            value={concern}
            onChange={(e) => setConcern(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleRun()}
            placeholder="Restaurant X claims 100% compostable packaging the city cannot process."
            className="flex-1 rounded-lg border border-app-border bg-app-bg px-3 py-2 text-sm text-zinc-100 outline-none focus:border-app-brand"
          />
          <button
            onClick={handleRun}
            disabled={mode === "STARTING" || mode === "STREAMING" || !concern.trim()}
            className="rounded-lg bg-app-brand px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          >
            {mode === "STARTING" || mode === "STREAMING" ? "Running…" : "Run workflow"}
          </button>
        </div>
        {errorMsg && <p className="mt-2 text-sm text-app-veto">{errorMsg}</p>}
        {mode === "MOCK" && (
          <p className="mt-2 text-xs text-app-muted">
            Reproducible cold-open shown until a workflow runs — run one for a live coordination.
          </p>
        )}
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="order-2 lg:order-1">
          <CoordinationHistory history={history} />
        </div>
        <div className="order-3 space-y-4 lg:order-2">
          <AgentConversationSurface messages={messages} />
          <EvidenceBriefCard brief={evidence} />
        </div>
        <div className="order-1 space-y-4 lg:order-3">
          <SafetyGateCard review={review} />
          <CampaignPacketCard packet={packet} />
        </div>
      </div>

      <footer className="mt-10 flex flex-wrap items-center justify-between gap-3 border-t border-app-border/60 pt-5">
        <div className="flex items-center gap-2.5">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/branding/emblem.png"
            alt="Activist OS"
            className="h-6 w-6 rounded opacity-90"
          />
          <span className="text-xs text-app-muted">Evidence. Coordination. Safety.</span>
        </div>
        <span className="font-mono text-[11px] text-app-muted">Activist OS · Free Intelligence</span>
      </footer>
    </main>
  );
}
