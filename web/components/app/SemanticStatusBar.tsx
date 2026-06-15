import type { WorkflowHistory } from "../../lib/api";
import { StatusBadge } from "./StatusBadge";

type Mode = "IDLE" | "STARTING" | "STREAMING" | "LIVE" | "ERROR" | "MOCK";

export function SemanticStatusBar({
  mode,
  history,
}: {
  mode: Mode;
  history: WorkflowHistory | null;
}) {
  const transport = history?.transport?.toUpperCase() ?? "—";
  const reporterVirtual = history?.artifacts.campaign_packet.reporter_virtual ?? null;
  const vetoLoop = history?.veto_loop.observed ?? false;

  return (
    <div className="flex flex-wrap items-center gap-2 text-[11px]">
      <StatusBadge variant={transport === "BAND" ? "band" : "local"}>
        Transport: {transport}
      </StatusBadge>
      <StatusBadge
        variant={
          mode === "ERROR" ? "veto" : mode === "LIVE" ? "approve" : mode === "MOCK" ? "virtual" : "muted"
        }
      >
        Mode: {mode === "MOCK" ? "MOCK FALLBACK" : mode}
      </StatusBadge>
      <StatusBadge variant={vetoLoop ? "veto" : "muted"}>
        Safety: {vetoLoop ? "VETO LOOP" : "—"}
      </StatusBadge>
      <StatusBadge variant="muted">Provenance: ON</StatusBadge>
      <StatusBadge variant={reporterVirtual ? "virtual" : "muted"}>
        Reporter: {reporterVirtual === null ? "—" : reporterVirtual ? "VIRTUAL" : "IN-ROOM"}
      </StatusBadge>
    </div>
  );
}
