export interface StreamEvent {
  event_type: string;
  index?: number;
  from_agent?: string;
  to_agent?: string;
  type?: string;
}

const DOT: Record<string, string> = {
  workflow_started: "text-app-brand",
  handoff_sent: "text-app-accent",
  workflow_completed: "text-app-approve",
  stream_end: "text-app-muted",
};

export function LiveEventLog({ events }: { events: StreamEvent[] }) {
  return (
    <section className="aos-glass-primary rounded-xl p-4">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-app-muted">
        Live events
      </h2>
      {events.length === 0 ? (
        <p className="text-sm text-app-muted">Waiting for the stream…</p>
      ) : (
        <ul className="space-y-1 font-mono text-xs">
          {events.map((e, i) => (
            <li key={i} className="flex items-center gap-2">
              <span className={DOT[e.event_type] ?? "text-app-muted"}>●</span>
              <span className="text-zinc-300">{e.event_type}</span>
              {e.event_type === "handoff_sent" && (
                <span className="text-app-muted">
                  #{e.index} {e.from_agent}→{e.to_agent} ({e.type})
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
