import type { HandoffView, WorkflowHistory } from "../../lib/api";
import { StatusBadge } from "./StatusBadge";
import { cap } from "../../lib/text";

function stepLabel(h: HandoffView, vetoIndex: number | null): string {
  if (h.type === "safety_veto") return "Safety VETO";
  if (h.type === "safety_approved") return "Safety APPROVED";
  if (
    h.from_agent === "campaign" &&
    h.to_agent === "safety" &&
    vetoIndex !== null &&
    h.index > vetoIndex
  ) {
    return "Campaign revision";
  }
  return cap(h.from_agent);
}

function HandoffRow({
  handoff,
  transport,
  vetoIndex,
}: {
  handoff: HandoffView;
  transport: string;
  vetoIndex: number | null;
}) {
  const veto = handoff.type === "safety_veto";
  const approved = handoff.type === "safety_approved";
  const label = stepLabel(handoff, vetoIndex) + (handoff.virtual ? " (virtual)" : "");
  return (
    <li className="flex items-start gap-3 border-b border-app-border/60 py-2 last:border-b-0">
      <span className="mt-0.5 w-5 shrink-0 text-right font-mono text-xs text-app-muted">
        {handoff.index}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span className="font-medium text-zinc-100">{label}</span>
          {veto && <StatusBadge variant="veto">VETO</StatusBadge>}
          {approved && <StatusBadge variant="approve">APPROVED</StatusBadge>}
          {handoff.virtual && <StatusBadge variant="virtual">VIRTUAL</StatusBadge>}
          <StatusBadge variant={transport === "band" ? "band" : "local"}>
            {transport === "band" ? "BAND" : "LOCAL"}
          </StatusBadge>
        </div>
        <p className="mt-0.5 truncate font-mono text-[11px] text-app-muted">
          {handoff.from_agent} → {handoff.to_agent}
        </p>
      </div>
    </li>
  );
}

export function CoordinationHistory({ history }: { history: WorkflowHistory | null }) {
  const vetoIndex = history?.veto_loop?.veto_index ?? null;
  return (
    <section className="aos-glass-primary rounded-xl p-4">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-app-muted">
        Coordination history
      </h2>
      {history ? (
        <>
          <ol className="text-sm">
            {history.handoffs.map((h) => (
              <HandoffRow
                key={h.index}
                handoff={h}
                transport={history.transport}
                vetoIndex={vetoIndex}
              />
            ))}
          </ol>
          <p className="mt-3 text-[11px] text-app-muted">
            Rendered from Transport.get_handoffs() — not narrated.
          </p>
        </>
      ) : (
        <p className="text-sm text-app-muted">No run yet.</p>
      )}
    </section>
  );
}
