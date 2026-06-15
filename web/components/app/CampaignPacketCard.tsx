import type { CampaignPacket } from "../../lib/api";
import { StatusBadge } from "./StatusBadge";

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <div className="rounded-lg border border-app-border bg-app-surface/70 px-3 py-2 text-center">
      <div className="text-lg font-semibold text-app-brand">{value}</div>
      <div className="text-[11px] uppercase tracking-wide text-app-muted">{label}</div>
    </div>
  );
}

function Bullet({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2 text-sm text-zinc-300">
      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: color }} />
      <span>{children}</span>
    </li>
  );
}

export function CampaignPacketCard({ packet }: { packet: CampaignPacket | null }) {
  return (
    <section className="aos-glass-secondary rounded-xl p-4">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-app-muted">
          Campaign packet
        </h2>
        {packet?.reporter_virtual && <StatusBadge variant="virtual">REPORTER VIRTUAL</StatusBadge>}
      </div>
      {!packet ? (
        <p className="text-sm text-app-muted">—</p>
      ) : (
        <>
          <p className="text-sm font-medium text-zinc-200">{packet.title}</p>
          <p className="mt-1 text-xs text-app-muted">{packet.summary}</p>

          <ul className="mt-3 space-y-1.5">
            <Bullet color="var(--color-app-accent)">
              Outreach pack — {packet.outreach_assets_count} community-language assets
            </Bullet>
            <Bullet color="var(--color-app-warn)">
              Task board — {packet.volunteer_tasks_count} volunteer actions, lawful + nonviolent
            </Bullet>
            <Bullet color="var(--color-app-approve)">
              Safety audit log — {packet.provenance_items_count} provenance items; vetoes included,
              not just approvals
            </Bullet>
          </ul>

          <p className="mt-3 text-xs text-app-muted">
            <span className="text-zinc-200">Humans hold the send button</span> — the system
            assembles, it never publishes.
          </p>

          <div className="mt-3 grid grid-cols-3 gap-2">
            <Stat value={packet.outreach_assets_count} label="Outreach" />
            <Stat value={packet.volunteer_tasks_count} label="Tasks" />
            <Stat value={packet.provenance_items_count} label="Provenance" />
          </div>
        </>
      )}
    </section>
  );
}
