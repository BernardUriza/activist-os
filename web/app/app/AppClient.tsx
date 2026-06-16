"use client";

import { useSearchParams } from "next/navigation";

import { FiGlassPrimary } from "../../components/app/FiGlassPrimary";
import { DashboardClient } from "./DashboardClient";

/**
 * AppClient — the /app surface selector (5C pivot). The fi-glass conversation is
 * now the PRIMARY surface; the legacy 3-column dashboard is preserved at
 * /app?dashboard=1 as the parity escape hatch and is NOT deleted until parity is
 * proven. Branching here (not inside either client) keeps only one surface
 * mounted, so only one workflow SSE stream is ever opened.
 */
export function AppClient() {
  const searchParams = useSearchParams();
  const showDashboard = searchParams.get("dashboard") === "1";
  const runId = searchParams.get("run_id");

  if (showDashboard) return <DashboardClient />;
  return <FiGlassPrimary runId={runId} />;
}
