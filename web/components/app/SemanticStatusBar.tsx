import { Radio, Cpu, Activity, ShieldAlert, Link2, Bot } from "lucide-react";
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
  const isBand = transport === "BAND";
  const reporterVirtual = history?.artifacts.campaign_packet.reporter_virtual ?? null;
  const vetoLoop = history?.veto_loop.observed ?? false;
  const band = history?.band ?? null;
  const bandRoom = band ? `${band.room_id.slice(0, 4)}…${band.room_id.slice(-4)}` : null;

  return (
    <div className="flex flex-wrap items-center gap-2 text-[11px]">
      <StatusBadge variant={isBand ? "band" : "local"}>
        {isBand ? <Radio size={11} strokeWidth={2.4} /> : <Cpu size={11} strokeWidth={2.4} />}
        {transport}
      </StatusBadge>
      {band && (
        <StatusBadge variant="band">
          <Radio size={11} strokeWidth={2.4} /> {bandRoom} · {band.messages_sent} msg ·{" "}
          {band.virtual_events} virt
        </StatusBadge>
      )}
      <StatusBadge
        variant={
          mode === "ERROR" ? "veto" : mode === "LIVE" ? "approve" : mode === "MOCK" ? "virtual" : "muted"
        }
      >
        <Activity size={11} strokeWidth={2.4} /> {mode === "MOCK" ? "MOCK FALLBACK" : mode}
      </StatusBadge>
      <StatusBadge variant={vetoLoop ? "veto" : "muted"}>
        <ShieldAlert size={11} strokeWidth={2.4} /> {vetoLoop ? "VETO LOOP" : "—"}
      </StatusBadge>
      <StatusBadge variant="muted">
        <Link2 size={11} strokeWidth={2.4} /> Provenance ON
      </StatusBadge>
      <StatusBadge variant={reporterVirtual ? "virtual" : "muted"}>
        <Bot size={11} strokeWidth={2.4} />{" "}
        {reporterVirtual === null ? "—" : reporterVirtual ? "VIRTUAL" : "IN-ROOM"}
      </StatusBadge>
    </div>
  );
}
