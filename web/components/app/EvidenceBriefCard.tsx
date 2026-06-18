import { FileSearch, Quote, Link2, type LucideIcon } from "lucide-react";
import type { EvidenceBrief } from "../../lib/api";
import { CollapsibleCard } from "./CollapsibleCard";

function Metric({
  icon: Icon,
  value,
  label,
}: {
  icon: LucideIcon;
  value: number;
  label: string;
}) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-app-border bg-app-surface/70 px-3 py-2">
      <Icon size={16} className="text-app-brand" strokeWidth={2.2} />
      <span className="text-lg font-semibold text-zinc-100">{value}</span>
      <span className="text-[11px] uppercase tracking-wide text-app-muted">{label}</span>
    </div>
  );
}

export function EvidenceBriefCard({ brief }: { brief: EvidenceBrief | null }) {
  return (
    <CollapsibleCard
      icon={FileSearch}
      title="Evidence brief"
      summary={
        <span className="text-[11px] text-app-muted">
          {brief ? `${brief.claims_count} claims · ${brief.sources_count} sources` : "—"}
        </span>
      }
    >
      {!brief ? (
        <p className="text-sm text-app-muted">—</p>
      ) : (
        <>
          <p className="text-sm font-medium text-zinc-200">{brief.title}</p>
          <div className="mt-3 flex gap-2">
            <Metric icon={Quote} value={brief.claims_count} label="claims" />
            <Metric icon={Link2} value={brief.sources_count} label="sources" />
          </div>
        </>
      )}
    </CollapsibleCard>
  );
}
