import { Megaphone, ListChecks, ShieldCheck, Hand, Bot, Info, type LucideIcon } from "lucide-react";
import type { CampaignPacket } from "../../lib/api";
import { StatusBadge } from "./StatusBadge";
import { CollapsibleCard } from "./CollapsibleCard";

function Stat({
  icon: Icon,
  value,
  label,
  color,
}: {
  icon: LucideIcon;
  value: number;
  label: string;
  color: string;
}) {
  return (
    <div className="flex flex-col items-center gap-0.5 rounded-lg border border-app-border bg-app-surface/70 px-2 py-2 text-center">
      <Icon size={16} strokeWidth={2.2} style={{ color }} />
      <div className="text-lg font-semibold text-zinc-100">{value}</div>
      <div className="text-[10px] uppercase tracking-wide text-app-muted">{label}</div>
    </div>
  );
}

export function CampaignPacketCard({ packet }: { packet: CampaignPacket | null }) {
  return (
    <CollapsibleCard
      icon={Megaphone}
      title="Campaign packet"
      badge={
        packet?.reporter_virtual ? (
          <StatusBadge variant="virtual">
            <Bot size={11} strokeWidth={2.4} /> Virtual
          </StatusBadge>
        ) : undefined
      }
      summary={
        <span className="text-[11px] text-app-muted">
          {packet
            ? `${packet.outreach_assets_count} assets · ${packet.volunteer_tasks_count} tasks · ${packet.provenance_items_count} prov`
            : "—"}
        </span>
      }
    >
      {!packet ? (
        <p className="text-sm text-app-muted">—</p>
      ) : (
        <>
          <p className="text-sm font-medium text-zinc-200">{packet.title}</p>

          <div className="mt-3 grid grid-cols-3 gap-2">
            <Stat
              icon={Megaphone}
              value={packet.outreach_assets_count}
              label="Outreach"
              color="var(--color-app-accent)"
            />
            <Stat
              icon={ListChecks}
              value={packet.volunteer_tasks_count}
              label="Tasks"
              color="var(--color-app-warn)"
            />
            <Stat
              icon={ShieldCheck}
              value={packet.provenance_items_count}
              label="Provenance"
              color="var(--color-app-approve)"
            />
          </div>

          <p className="mt-3 flex items-center gap-2 text-xs text-app-muted">
            <Hand size={14} strokeWidth={2.2} className="text-zinc-300" />
            <span>
              <span className="text-zinc-200">Humans hold the send button.</span> The system
              assembles, never publishes.
            </span>
          </p>

          {packet.reporter_virtual && (
            <details className="group mt-3">
              <summary className="flex cursor-pointer items-center gap-1.5 text-[11px] text-app-virtual">
                <Info size={12} strokeWidth={2.4} /> Why a virtual reporter?
              </summary>
              <p className="mt-1.5 rounded-lg bg-app-surface/60 p-2.5 text-[11px] leading-relaxed text-app-muted">
                Reporter is virtualized to respect Band room participant limits while preserving the
                canonical workflow history.
              </p>
            </details>
          )}
        </>
      )}
    </CollapsibleCard>
  );
}
