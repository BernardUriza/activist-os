import type { AgentMessage } from "../../lib/workflow-presentation";
import { cap } from "../../lib/text";

export function AgentConversationSurface({ messages }: { messages: AgentMessage[] }) {
  return (
    <section className="aos-glass-primary rounded-xl p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-app-muted">
        Agent conversation
      </h2>
      {messages.length === 0 ? (
        <p className="text-sm text-app-muted">Coordinating…</p>
      ) : (
        <div className="space-y-2.5">
          {messages.map((m) => {
            const accent =
              m.tag === "SAFETY_VETO"
                ? "border-app-veto/50 bg-app-veto/10"
                : m.tag === "SAFETY_APPROVED"
                  ? "border-app-approve/50 bg-app-approve/10"
                  : "border-app-border bg-app-surface/60";
            return (
              <div key={m.index} className={`rounded-lg border p-3 ${accent}`}>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold text-zinc-100">{cap(m.from)}</span>
                  {m.virtual ? (
                    <span className="font-mono text-[11px] text-app-virtual">
                      [virtual · backend event]
                    </span>
                  ) : (
                    <span className="font-mono text-[11px] text-app-brand">@{cap(m.to)}</span>
                  )}
                  <span className="font-mono text-[10px] uppercase tracking-wide text-app-muted">
                    {m.tag}
                  </span>
                </div>
                {m.body && <p className="mt-1 text-sm text-zinc-300">{m.body}</p>}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
