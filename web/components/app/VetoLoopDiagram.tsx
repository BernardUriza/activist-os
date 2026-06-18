"use client";

import { motion } from "framer-motion";
import {
  FileText,
  ShieldAlert,
  OctagonX,
  CircleCheck,
  RotateCcw,
  ArrowRight,
  type LucideIcon,
} from "lucide-react";
import type { SafetyReview } from "../../lib/api";

type Step = {
  icon: LucideIcon;
  label: string;
  color: string;
  active: boolean;
  loopsBackWhenVetoed?: boolean;
};

export function VetoLoopDiagram({ review }: { review: SafetyReview | null }) {
  const vetoed = review?.veto_observed ?? false;
  const approved = Boolean(review?.rewritten_text);

  const steps: Step[] = [
    { icon: FileText, label: "Draft", color: "var(--color-app-brand)", active: Boolean(review) },
    {
      icon: ShieldAlert,
      label: "Safety",
      color: "var(--color-app-virtual)",
      active: Boolean(review),
      loopsBackWhenVetoed: true,
    },
    { icon: OctagonX, label: "Veto", color: "var(--color-app-veto)", active: vetoed },
    { icon: CircleCheck, label: "Approved", color: "var(--color-app-approve)", active: approved },
  ];

  return (
    <div className="flex items-center justify-between gap-1 px-1 py-1">
      {steps.map((s, i) => (
        <div key={s.label} className="flex items-center gap-1">
          <motion.div
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: s.active ? 1 : 0.35, scale: 1 }}
            transition={{ delay: i * 0.12, type: "spring", stiffness: 220, damping: 18 }}
            className="flex flex-col items-center gap-1"
          >
            <span
              className="flex h-9 w-9 items-center justify-center rounded-full border"
              style={{
                borderColor: s.color,
                background: s.active ? `color-mix(in srgb, ${s.color} 18%, transparent)` : "transparent",
                color: s.color,
              }}
            >
              <s.icon size={16} strokeWidth={2.2} />
            </span>
            <span className="text-[10px] font-medium uppercase tracking-wide text-app-muted">
              {s.label}
            </span>
          </motion.div>
          {i < steps.length - 1 && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.12 + 0.06 }}
              className="text-app-muted"
            >
              {s.loopsBackWhenVetoed && vetoed ? (
                <RotateCcw size={13} style={{ color: "var(--color-app-warn)" }} />
              ) : (
                <ArrowRight size={13} strokeWidth={2.2} />
              )}
            </motion.span>
          )}
        </div>
      ))}
    </div>
  );
}
