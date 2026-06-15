import type { SafetyReview } from "../../lib/api";
import { StatusBadge } from "./StatusBadge";

export function SafetyGateCard({ review }: { review: SafetyReview | null }) {
  return (
    <section className="aos-glass-critical rounded-xl p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-100">
          Safety gate
        </h2>
        <span className="text-[11px] font-medium text-app-muted">the money shot</span>
      </div>

      {!review ? (
        <p className="text-sm text-app-muted">Run a workflow to see the gate in action.</p>
      ) : (
        <ol className="space-y-3">
          <li className="rounded-lg border border-app-border bg-app-surface/70 p-3">
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-app-muted">
              Campaign draft
            </div>
            <p className="text-sm text-zinc-300">
              {review.draft_text || "Draft language required revision."}
            </p>
          </li>

          <div className="flex justify-center text-app-veto">↓</div>

          <li className="rounded-lg border border-app-veto/50 bg-app-veto/10 p-3">
            <div className="mb-1 flex items-center gap-2">
              <StatusBadge variant="veto">VETO</StatusBadge>
              {review.veto_observed && (
                <span className="text-[11px] text-app-muted">needs revision</span>
              )}
            </div>
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-app-veto">
              Blocked reason
            </div>
            <p className="text-sm text-zinc-200">
              {review.veto_reason || "Safety veto returned a reason."}
            </p>
            {review.blocked_items && review.blocked_items.length > 0 && (
              <ul className="mt-2 space-y-1">
                {review.blocked_items.map((b, i) => (
                  <li key={i} className="text-xs text-app-veto">
                    blocked: {b.check}
                    {b.severity ? ` (${b.severity})` : ""}
                  </li>
                ))}
              </ul>
            )}
          </li>

          <div className="flex justify-center text-app-approve">↓ revision → re-review</div>

          <li className="rounded-lg border border-app-approve/50 bg-app-approve/10 p-3">
            <div className="mb-1 flex items-center gap-2">
              <StatusBadge variant="approve">APPROVED</StatusBadge>
            </div>
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-app-approve">
              Approved rewrite
            </div>
            <p className="text-sm text-zinc-200">
              {review.rewritten_text || "Approved rewrite available after revision."}
            </p>
          </li>
        </ol>
      )}
    </section>
  );
}
