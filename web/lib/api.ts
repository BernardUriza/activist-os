/** API base URL — single source of truth for the FastAPI backend address.
 *
 * Note on Next.js: `NEXT_PUBLIC_*` is **build-time** inlined into the bundle,
 * not read at runtime. The Azure SWA pipeline must inject this before
 * `next build`; otherwise the production chat hits localhost. */
const DEFAULT_DEV_API_URL = "http://localhost:8080";

export const API_URL = normalizeApiUrl(
  process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_DEV_API_URL,
);

// Client abort for a /chat/stream turn. MUST stay LONGER than the backend's
// APP_CHAT_TURN_TIMEOUT_S (600s) so the SERVER wins the race and returns its
// own timeout message instead of the client aborting first. Heavy agentic
// turns run several minutes — a short client timeout kills them prematurely.
export const CHAT_STREAM_TIMEOUT_MS = 630_000;
export const API_REQUEST_TIMEOUT_MS = 30_000;
export const MAX_CHAT_MESSAGE_CHARS = 12_000;

function normalizeApiUrl(raw: string): string {
  const value = raw.trim();
  try {
    const url = new URL(value);
    return url.toString().replace(/\/$/, "");
  } catch {
    if (process.env.NODE_ENV !== "production") return DEFAULT_DEV_API_URL;
    throw new Error(`Invalid NEXT_PUBLIC_API_URL: ${value}`);
  }
}

/** Join a path onto the API base, normalizing the slash. */
export function apiUrl(path: string): string {
  const tail = path.startsWith("/") ? path : `/${path}`;
  return `${API_URL}${tail}`;
}

/** Optional shared API key — same caveat as `API_URL`: `NEXT_PUBLIC_*` is
 * **build-time** inlined, so it ends up in the bundle a user can read in
 * DevTools. That's intentional: this is NOT a secret, it's a public gate.
 * The real cost-control floor is the API-side per-IP rate limit (see
 * api/app/auth.py:limiter). Leave unset in dev — the API fail-opens. */
export const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

export function newClientRequestId(prefix = "web"): string {
  const random =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
  return `${prefix}-${random}`;
}

/** Build the headers needed to talk to the API. Centralized so a future
 * scheme change (e.g. Bearer JWT) is one edit, and so we never accidentally
 * ship a request that forgets the key. */
export function apiHeaders(extra?: HeadersInit): HeadersInit {
  const base: Record<string, string> = {
    "X-Client-Request-ID": newClientRequestId(),
  };
  if (API_KEY) base["X-API-Key"] = API_KEY;
  if (extra instanceof Headers) {
    extra.forEach((v, k) => (base[k] = v));
  } else if (Array.isArray(extra)) {
    for (const [k, v] of extra) base[k] = v;
  } else if (extra) {
    Object.assign(base, extra);
  }
  return base;
}

// ── Activist OS coordination API ───────────────────────────────────────────

export type AgentName =
  | "evidence"
  | "campaign"
  | "safety"
  | "outreach"
  | "coordinator"
  | "reporter"
  | "system";

export type HandoffType =
  | "handoff"
  | "safety_veto"
  | "safety_approved"
  | "tasks_ready"
  | "packet_ready";

export interface HandoffView {
  index: number;
  from_agent: AgentName;
  to_agent: AgentName;
  type: HandoffType;
  summary: string;
  timestamp: string;
  virtual: boolean;
}

export interface VetoLoop {
  observed: boolean;
  veto_index: number | null;
  approved_index: number | null;
}

export interface EvidenceBrief {
  title: string;
  summary: string;
  claims_count: number;
  sources_count: number;
}

export interface SafetyReview {
  veto_observed: boolean;
  approved: boolean;
  draft_text: string;
  veto_reason: string;
  rewritten_text: string;
  // The API does not surface blocked_items in /history today (kept optional so
  // the card lights up if a future API tweak exposes it).
  blocked_items?: { check: string; severity?: string }[];
}

export interface CampaignPacket {
  reporter_virtual: boolean;
  outreach_assets_count: number;
  volunteer_tasks_count: number;
  provenance_items_count: number;
  title: string;
  summary: string;
}

export interface WorkflowArtifacts {
  evidence_brief: EvidenceBrief;
  safety_review: SafetyReview;
  campaign_packet: CampaignPacket;
}

export interface BandProvenance {
  room_id: string;
  messages_sent: number;
  virtual_events: number;
}

export interface WorkflowHistory {
  run_id: string;
  status: string;
  transport: string;
  handoffs: HandoffView[];
  veto_loop: VetoLoop;
  artifacts: WorkflowArtifacts;
  band?: BandProvenance;
}

export class WorkflowNotFoundError extends Error {
  constructor(runId: string) {
    super(`workflow run not found: ${runId}`);
    this.name = "WorkflowNotFoundError";
  }
}

export function getApiBaseUrl(): string {
  return API_URL;
}

export async function startWorkflow(input: {
  concern: string;
}): Promise<{ run_id: string; status?: string }> {
  const res = await fetch(apiUrl("/workflow/start"), {
    method: "POST",
    headers: apiHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ concern: input.concern }),
    signal: AbortSignal.timeout(API_REQUEST_TIMEOUT_MS),
  });
  if (!res.ok) throw new Error(`startWorkflow failed: HTTP ${res.status}`);
  return res.json();
}

export async function getWorkflowHistory(runId: string): Promise<WorkflowHistory> {
  const res = await fetch(
    apiUrl(`/workflow/${encodeURIComponent(runId)}/history`),
    { headers: apiHeaders(), signal: AbortSignal.timeout(API_REQUEST_TIMEOUT_MS) },
  );
  if (res.status === 404) throw new WorkflowNotFoundError(runId);
  if (!res.ok) throw new Error(`getWorkflowHistory failed: HTTP ${res.status}`);
  return res.json();
}

/** EventSource cannot send custom headers — the API's /events route is ungated
 * (no X-API-Key), so a bare GET works. Returns the absolute SSE URL. */
export function getWorkflowEventsUrl(runId: string): string {
  return apiUrl(`/workflow/${encodeURIComponent(runId)}/events`);
}
