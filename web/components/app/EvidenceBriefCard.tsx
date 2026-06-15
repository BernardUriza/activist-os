import type { EvidenceBrief } from "../../lib/api";

export function EvidenceBriefCard({ brief }: { brief: EvidenceBrief | null }) {
  return (
    <section className="aos-glass-secondary rounded-xl p-4">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-app-muted">
        Evidence brief
      </h2>
      {!brief ? (
        <p className="text-sm text-app-muted">—</p>
      ) : (
        <>
          <p className="text-sm font-medium text-zinc-200">{brief.title}</p>
          <p className="mt-1 text-xs text-app-muted">{brief.summary}</p>
          <div className="mt-3 flex gap-4 text-xs">
            <span className="text-zinc-300">
              <span className="font-semibold text-app-brand">{brief.claims_count}</span> claims
            </span>
            <span className="text-zinc-300">
              <span className="font-semibold text-app-brand">{brief.sources_count}</span> sources
            </span>
          </div>
        </>
      )}
    </section>
  );
}
