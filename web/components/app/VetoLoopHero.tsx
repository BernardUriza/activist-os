"use client";

import dynamic from "next/dynamic";
import type { SafetyReview } from "../../lib/api";

const VetoLoopCanvas = dynamic(() => import("./VetoLoopCanvas"), { ssr: false });

export function VetoLoopHero({ review }: { review: SafetyReview | null }) {
  const phase = review ? "running" : "idle";
  return (
    <section className="aos-glass-critical relative overflow-hidden rounded-xl">
      <div className="h-[180px] w-full">
        <VetoLoopCanvas phase={phase} />
      </div>
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between px-4 pb-2.5 text-[10px] uppercase tracking-[0.18em] text-app-muted">
        <span>Safety loop</span>
        <span>{phase === "running" ? "veto → revision → approved" : "idle"}</span>
      </div>
    </section>
  );
}
