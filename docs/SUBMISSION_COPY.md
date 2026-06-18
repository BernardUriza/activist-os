# Submission copy — Activist OS

Paste-ready copy for the lablab.ai / Band of Agents submission form. Every claim
here is backed by the live demo and the canonical contract.

- **Project name:** Activist OS
- **Live demo:** <https://proud-stone-023fae70f.7.azurestaticapps.net/app>
- **Track:** Regulated & High-Stakes Workflows

---

## Short description (one line)

A high-stakes multi-agent workflow for safe, evidence-backed civic advocacy —
six Band-coordinated agents with a Safety agent that can veto any campaign before
it goes public.

## Long description

Activist OS turns a single community concern into a verified campaign packet:
provenance-checked evidence, an evidence-bounded narrative, a volunteer task
board, and a full safety audit — **before anything is published**.

Six specialized agents each own one role and exchange structured context through
Band: Evidence verifies claims and tags provenance; Campaign turns evidence into
a narrative; **Safety holds veto power** over doxxing, harassment, and
unsupported accusations; Outreach drafts public copy; Coordinator builds the task
board; Reporter assembles the audit packet. The coordination is *visible, not
narrated* — every one of the eight handoffs renders from the real transport.

The product is the governance: Safety can reject a campaign draft, the rejection
stays on the record inside the packet, and the system never publishes on its own.
Humans hold the send button.

## How to use the demo

1. Open <https://proud-stone-023fae70f.7.azurestaticapps.net/app>.
2. Submit a civic concern (e.g. *"Restaurant compostable claim lacks local
   disposal evidence"*).
3. Watch the eight Band-coordinated handoffs stream in (TRANSPORT badge +
   provenance room chip).
4. Watch Safety **veto** the first draft, Campaign revise, and Safety **approve**
   the revision.
5. Open the artifacts rail: Evidence Brief, Safety Gate (with the rejected
   revision), Campaign Packet.

## Tech stack

- **Frontend:** Next.js 16 + fi-glass `AgentConversationSurface` + Tailwind v4.
- **Backend:** FastAPI (`app.main:app`), SSE workflow stream.
- **Coordination:** Band — real agent room, one room per run (or reuse_single),
  four recruited seats with reporter/system as virtual legs.
- **Substrate:** Free-Intelligence (FI) — workflow provenance and memory.
- **Deploy:** Azure Static Web Apps (web) + Azure Container Apps (api), OIDC +
  GHCR, path-scoped GitHub Actions.

## What makes it high-stakes / regulated

Advocacy carries real legal and safety exposure: an unsupported claim is a
defamation risk, a public campaign can escalate into harassment, and there is no
ops layer to catch it. Activist OS puts a governed safety gate between intent and
public action — the exact failure mode regulated workflows must prevent.

## What Band does

Band coordinates the agents in a real room. Each handoff is stamped with the
run's room id (shown as the provenance chip in the UI). A canonical demo run is
**8 handoffs, 6 Band messages, 2 virtual events**; the room holds four recruited
seats at a five-seat cap, with reporter and system riding as virtual legs (no
seat consumed). A `reuse_single` strategy reuses one existing room to stay under
room caps across runs.

## What FI does

Free-Intelligence is the substrate: it preserves workflow provenance and memory
across the handoff chain, and provides the contract the web adapter maps to
`ChatMessage[]` for fi-glass to render verbatim. The transport protocol is the
source of truth — neither backend nor frontend bends to the other's convenience.

## Safety claims

- A dedicated Safety agent with **veto power** over public-facing output.
- The canonical run is one veto → one revision → one approval (the money shot),
  with both the rejection and the approval on the record.
- Evidence-bounded language: the narrative never exceeds what the evidence
  supports.
- **No autonomous public posting** — the system assembles, humans send.

## Limitations / honest notes

- The public demo is intentionally open (no auth) for judging convenience. A
  production deployment should add authentication and rate limiting on
  `/workflow/*`; `/health` stays keyless for the liveness probe. This is a
  deployment hardening step, not a gap in the coordination contract.
- The default demo transport is a deterministic local mock so the run is
  reproducible; the real Band transport is opt-in (`TRANSPORT=band`).
- The legacy 3-column dashboard remains at `/app?dashboard=1` as a parity/debug
  fallback, not the primary surface.
