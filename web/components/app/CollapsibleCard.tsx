"use client";

import { useId, useState, type ReactNode } from "react";
import { ChevronDown, type LucideIcon } from "lucide-react";

export function CollapsibleCard({
  icon: Icon,
  title,
  summary,
  badge,
  defaultOpen = false,
  children,
}: {
  icon: LucideIcon;
  title: string;
  summary?: ReactNode;
  badge?: ReactNode;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const panelId = useId();
  return (
    <section className="aos-glass-secondary rounded-xl">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={panelId}
        className="flex w-full items-center justify-between gap-2 p-4 text-left"
      >
        <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-app-muted">
          <Icon size={15} strokeWidth={2.2} /> {title}
        </h2>
        <div className="flex items-center gap-2">
          {!open && summary}
          {badge}
          <ChevronDown
            size={16}
            className={`text-app-muted transition-transform ${open ? "rotate-180" : ""}`}
          />
        </div>
      </button>
      <div id={panelId} hidden={!open} className="px-4 pb-4">
        {children}
      </div>
    </section>
  );
}
