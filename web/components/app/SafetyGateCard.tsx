import { FileText, OctagonX, CircleCheck, type LucideIcon } from "lucide-react";
import type { SafetyReview } from "../../lib/api";
import { StatusBadge } from "./StatusBadge";
import { VetoLoopHero } from "./VetoLoopHero";
import { VetoLoopDiagram } from "./VetoLoopDiagram";

function Detail({
  icon: Icon,
  badge,
  color,
  text,
  open,
}: {
  icon: LucideIcon;
  badge: React.ReactNode;
  color: string;
  text: string;
  open?: boolean;
}) {
  return (
    <details open={open} className="rounded-lg border border-app-border bg-app-surface/60 px-3 py-2">
      <summary className="flex cursor-pointer items-center gap-2 text-[11px] uppercase tracking-wide">
        <Icon size={14} strokeWidth={2.2} style={{ color }} />
        {badge}
      </summary>
      <p className="mt-1.5 text-sm text-zinc-200">{text}</p>
    </details>
  );
}

export function SafetyGateCard({ review }: { review: SafetyReview | null }) {
  return (
    <section className="aos-glass-critical rounded-xl p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-100">Safety gate</h2>
        <span className="text-[11px] font-medium text-app-muted">the money shot</span>
      </div>

      <VetoLoopHero review={review} />

      <div className="mt-3">
        <VetoLoopDiagram review={review} />
      </div>

      {!review ? (
        <p className="mt-3 text-sm text-app-muted">Run a workflow to see the gate in action.</p>
      ) : (
        <div className="mt-3 space-y-2">
          <Detail
            icon={FileText}
            color="var(--color-app-brand)"
            badge={<span className="text-app-muted">Campaign draft</span>}
            text={review.draft_text || "Draft language required revision."}
          />
          <Detail
            icon={OctagonX}
            color="var(--color-app-veto)"
            open
            badge={
              <span className="flex items-center gap-2">
                <StatusBadge variant="veto">VETO</StatusBadge>
                {review.veto_observed && <span className="text-app-muted">needs revision</span>}
              </span>
            }
            text={review.veto_reason || "Safety veto returned a reason."}
          />
          <Detail
            icon={CircleCheck}
            color="var(--color-app-approve)"
            open
            badge={<StatusBadge variant="approve">APPROVED</StatusBadge>}
            text={review.rewritten_text || "Approved rewrite available after revision."}
          />
        </div>
      )}
    </section>
  );
}
