"use client";

/**
 * useActivistAgent — core's AgentHook implemented over the Activist OS WORKFLOW
 * transport (NOT /chat/stream). It POSTs /workflow/start, streams
 * /workflow/{id}/events via EventSource, and on stream_end loads
 * /workflow/{id}/history so the final, audited handoffs replace the live
 * transcript. The visible thread is exposed as core ChatMessage[] (mapped by
 * lib/workflow-chat), so a fi-glass AgentConversationSurface can render it.
 *
 * This is the workflow twin of useTemplateAgent: same AgentHook contract, a
 * different transport. The default /app dashboard keeps its own inline transport
 * untouched — this hook exists for the fi-glass canary surface only.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  initialAgentTurnState,
  type AgentHook,
  type AgentTurnState,
  type ChatMessage,
} from "@free-intelligence/core";

import {
  getWorkflowEventsUrl,
  getWorkflowHistory,
  startWorkflow,
  WorkflowNotFoundError,
  type WorkflowHistory,
} from "./api";
import { type StreamEvent } from "../components/app/LiveEventLog";
import { MOCK_WORKFLOW_HISTORY } from "./mock-workflow";
import { chatMessagesFromEvents, chatMessagesFromHistory } from "./workflow-chat";

export type ActivistMode = "IDLE" | "MOCK" | "STARTING" | "STREAMING" | "LIVE" | "ERROR";

export interface ActivistAgent extends AgentHook {
  messages: ChatMessage[];
  history: WorkflowHistory | null;
  runId: string | null;
  mode: ActivistMode;
  error: string | null;
}

export function useActivistAgent(opts?: { initialRunId?: string | null }): ActivistAgent {
  const initialRunId = opts?.initialRunId ?? null;

  const [mode, setMode] = useState<ActivistMode>(initialRunId ? "IDLE" : "MOCK");
  const [runId, setRunId] = useState<string | null>(initialRunId);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [history, setHistory] = useState<WorkflowHistory | null>(
    initialRunId ? null : MOCK_WORKFLOW_HISTORY,
  );
  const [error, setError] = useState<string | null>(null);

  const esRef = useRef<EventSource | null>(null);
  const openedFor = useRef<string | null>(null);
  const streamEndedRef = useRef(false);
  const modeRef = useRef(mode);
  modeRef.current = mode;

  const loadHistory = useCallback(async (id: string, retries = 0) => {
    try {
      const data = await getWorkflowHistory(id);
      setHistory(data);
      setMode("LIVE");
    } catch (err) {
      if (err instanceof WorkflowNotFoundError && retries > 0) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        return loadHistory(id, retries - 1);
      }
      setError(
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
      streamEndedRef.current = false;
      setEvents([]);
      setHistory(null);
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
          streamEndedRef.current = true;
          es.close();
          void loadHistory(id);
        }
      };

      es.onerror = () => {
        es.close();
        if (streamEndedRef.current) return;
        void loadHistory(id, 3);
      };
    },
    [loadHistory],
  );

  const send = useCallback(
    async (message: string) => {
      const concern = message.trim();
      if (!concern || modeRef.current === "STARTING" || modeRef.current === "STREAMING") return;
      setError(null);
      setHistory(null);
      setEvents([]);
      openedFor.current = null;
      setMode("STARTING");
      try {
        const { run_id } = await startWorkflow({ concern });
        setRunId(run_id);
        openStream(run_id);
      } catch (err) {
        setError(`Could not start workflow: ${(err as Error).message}`);
        setMode("ERROR");
      }
    },
    [openStream],
  );

  const abort = useCallback(() => {
    esRef.current?.close();
    openedFor.current = null;
    setMode((prev) => (prev === "STREAMING" || prev === "STARTING" ? "IDLE" : prev));
  }, []);

  const reset = useCallback(() => {
    esRef.current?.close();
    openedFor.current = null;
    setEvents([]);
    setRunId(null);
    setError(null);
    setHistory(MOCK_WORKFLOW_HISTORY);
    setMode("MOCK");
  }, []);

  useEffect(() => {
    if (initialRunId && openedFor.current !== initialRunId) {
      setRunId(initialRunId);
      openStream(initialRunId);
    }
  }, [initialRunId, openStream]);

  useEffect(() => () => esRef.current?.close(), []);

  const isStreaming = mode === "STARTING" || mode === "STREAMING";

  const turn: AgentTurnState = useMemo(
    () => ({ ...initialAgentTurnState(), status: isStreaming ? "streaming" : "done" }),
    [isStreaming],
  );

  const messages = useMemo(
    () => (history ? chatMessagesFromHistory(history) : chatMessagesFromEvents(events)),
    [history, events],
  );

  return { turn, isStreaming, send, abort, reset, messages, history, runId, mode, error };
}
