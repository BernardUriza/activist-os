"use client";

/**
 * FiGlassConversationCanary — the opt-in preview wrapper (/app?fi_glass_canary=1)
 * that lifts its own ActivistAgent and renders the canonical FiGlassConversation.
 * The 5C primary surface (FiGlassPrimary) reuses the same FiGlassConversation
 * with a lifted agent so chat + artifacts rail share one workflow run.
 */

import { useActivistAgent } from "../../lib/useActivistAgent";
import { FiGlassConversation } from "./FiGlassConversation";

export function FiGlassConversationCanary({ runId }: { runId?: string | null }) {
  const agent = useActivistAgent({ initialRunId: runId });
  return <FiGlassConversation agent={agent} />;
}
