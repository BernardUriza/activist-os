import { FileSearch, Quote, Link2, type LucideIcon } from "lucide-react";
import type { EvidenceBrief } from "../../lib/api";

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
    <section className="aos-glass-secondary rounded-xl p-4">
      <h2 className="mb-2 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-app-muted">
        <FileSearch size={15} strokeWidth={2.2} /> Evidence brief
      </h2>
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
    </section>
  );
}
