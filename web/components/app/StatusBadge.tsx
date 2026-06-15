import type { ReactNode } from "react";

type Variant = "veto" | "approve" | "virtual" | "band" | "local" | "brand" | "muted";

const VARIANT: Record<Variant, string> = {
  veto: "border-app-veto/50 bg-app-veto/15 text-app-veto",
  approve: "border-app-approve/50 bg-app-approve/15 text-app-approve",
  virtual: "border-app-virtual/50 bg-app-virtual/15 text-app-virtual",
  band: "border-app-brand/50 bg-app-brand/15 text-app-brand",
  local: "border-app-border bg-app-surface text-app-muted",
  brand: "border-app-brand/50 bg-app-brand/15 text-app-brand",
  muted: "border-app-border bg-app-surface text-app-muted",
};

export function StatusBadge({
  variant = "muted",
  children,
}: {
  variant?: Variant;
  children: ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${VARIANT[variant]}`}
    >
      {children}
    </span>
  );
}
