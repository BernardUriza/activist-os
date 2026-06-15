import Link from "next/link";

export const metadata = {
  title: "Safe, evidence-backed civic advocacy workflows",
};

export default function Home() {
  return (
    <div className="aos-landing">
      <header
        className="sticky top-0 z-50 backdrop-blur-md"
        style={{
          background: "color-mix(in srgb, var(--fi-bg), transparent 25%)",
          borderBottom: "1px solid var(--fi-border-soft)",
        }}
      >
        <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/branding/emblem.png"
              alt="Activist OS"
              width={36}
              height={36}
              className="h-9 w-9 rounded-lg"
            />
            <span className="font-semibold tracking-tight">Activist OS</span>
          </div>
          <div className="hidden items-center gap-8 text-sm text-muted md:flex">
            <a href="#workflow" className="transition hover:text-white">Workflow</a>
            <a href="#veto" className="transition hover:text-white">Safety veto</a>
            <a href="#packet" className="transition hover:text-white">Output</a>
            <a href="#architecture" className="transition hover:text-white">Architecture</a>
          </div>
          <Link href="/app" className="fi-btn fi-btn--ghost px-4 py-2 text-sm">
            Open console
          </Link>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6">
        {/* 1. Hero + agent flow */}
        <section className="grid items-center gap-12 py-20 lg:grid-cols-2 lg:py-28">
          <div className="fi-rise">
            <p className="fi-eyebrow mb-5">Regulated &amp; High-Stakes Workflows</p>
            <h1 className="mb-6 text-4xl font-extrabold leading-[1.05] tracking-tight md:text-5xl lg:text-6xl">
              Safe, evidence-backed
              <br />
              civic advocacy workflows.
            </h1>
            <p className="mb-8 max-w-xl text-lg leading-relaxed text-muted">
              Coordinate specialized agents to turn a community concern into a verified campaign
              packet — with provenance, safety review, and human-action tasks{" "}
              <span className="font-medium text-white">before anything goes public.</span>
            </p>
            <div className="mb-10 flex flex-wrap gap-3">
              <Link href="/app" className="fi-btn fi-btn--primary">Launch Activist OS →</Link>
              <a href="#workflow" className="fi-btn fi-btn--ghost">View agent flow</a>
            </div>
            <div className="fi-mono space-y-1 text-sm text-faint">
              <p><span style={{ color: "var(--fi-accent)" }}>Band</span> coordinates the agents.</p>
              <p><span style={{ color: "var(--fi-evidence)" }}>FI</span> preserves memory and provenance.</p>
              <p><span style={{ color: "var(--fi-safety)" }}>Safety</span> gates every public action.</p>
            </div>
          </div>

          <div className="fi-glass-panel fi-rise p-6 lg:p-8" style={{ animationDelay: ".1s" }}>
            <p className="fi-eyebrow mb-5">Agent flow</p>
            <div className="fi-mono space-y-3 text-sm">
              <div className="fi-agent-node fi-evidence-b flex items-center justify-between px-4 py-3">
                <span>Evidence</span>
                <span className="fi-badge fi-badge--verified">verified</span>
              </div>
              <div className="fi-arrow text-center">↓</div>
              <div
                className="rounded-xl p-3"
                style={{
                  border: "1px dashed color-mix(in srgb, var(--fi-safety), transparent 55%)",
                  background: "color-mix(in srgb, var(--fi-safety), transparent 95%)",
                }}
              >
                <p className="mb-2 px-1 text-[.6rem] uppercase tracking-widest text-faint">veto loop</p>
                <div className="fi-agent-node mb-2 flex items-center justify-between px-4 py-3">
                  <span>Campaign</span>
                  <span className="fi-arrow">⇄</span>
                </div>
                <div className="fi-agent-node fi-safety flex items-center justify-between px-4 py-3">
                  <span>Safety</span>
                  <span className="fi-badge fi-badge--review">review</span>
                </div>
              </div>
              <div className="fi-arrow text-center">↓</div>
              <div className="grid grid-cols-2 gap-3">
                <div className="fi-agent-node px-4 py-3">Outreach</div>
                <div className="fi-agent-node px-4 py-3">Coordinator</div>
              </div>
              <div className="fi-arrow text-center">↓</div>
              <div className="fi-agent-node fi-approved flex items-center justify-between px-4 py-3">
                <span>Reporter</span>
                <span className="fi-badge fi-badge--approved">packet</span>
              </div>
            </div>
          </div>
        </section>

        {/* 2. The high-stakes problem */}
        <section className="border-t py-16" style={{ borderColor: "var(--fi-border-soft)" }}>
          <p className="fi-eyebrow mb-3">The high-stakes problem</p>
          <h2 className="mb-3 max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
            Advocacy is easy to start and easy to get wrong.
          </h2>
          <p className="mb-10 max-w-2xl text-muted">
            Grassroots groups carry real legal and safety exposure with no ops layer to catch it.
          </p>
          <div className="grid gap-5 md:grid-cols-3">
            <div className="fi-glass-panel p-6">
              <div className="fi-mono mb-4 text-2xl" style={{ color: "var(--fi-veto)" }}>01</div>
              <h3 className="mb-2 text-lg font-semibold">Unsupported claims create legal risk.</h3>
              <p className="text-sm leading-relaxed text-muted">A defamation suit is the fastest way for a corporation to silence a local group. One overstated accusation is all it takes.</p>
            </div>
            <div className="fi-glass-panel p-6">
              <div className="fi-mono mb-4 text-2xl" style={{ color: "var(--fi-safety)" }}>02</div>
              <h3 className="mb-2 text-lg font-semibold">Public campaigns can accidentally escalate.</h3>
              <p className="text-sm leading-relaxed text-muted">Targeting a person instead of a practice, or leaking private data, turns advocacy into harassment — even when the cause is right.</p>
            </div>
            <div className="fi-glass-panel p-6">
              <div className="fi-mono mb-4 text-2xl" style={{ color: "var(--fi-accent)" }}>03</div>
              <h3 className="mb-2 text-lg font-semibold">Volunteer teams burn out on coordination.</h3>
              <p className="text-sm leading-relaxed text-muted">Groups dissolve because organizers drown in email, spreadsheets, and drafting — not because the cause died.</p>
            </div>
          </div>
        </section>

        {/* 3. How the workflow works */}
        <section id="workflow" className="border-t py-16" style={{ borderColor: "var(--fi-border-soft)", scrollMarginTop: "5rem" }}>
          <p className="fi-eyebrow mb-3">How the workflow works</p>
          <h2 className="mb-3 max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
            Six specialized agents, one governed handoff chain.
          </h2>
          <p className="mb-10 max-w-2xl text-muted">
            Each agent owns one role and exchanges structured context through Band. The coordination
            is visible — not narrated.
          </p>
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            <div className="fi-glass-panel fi-evidence-b p-6">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-lg font-semibold">Evidence</h3>
                <span className="fi-badge fi-badge--verified">verified</span>
              </div>
              <p className="text-sm leading-relaxed text-muted">Finds and verifies claims, attaching a provenance tier to every source.</p>
            </div>
            <div className="fi-glass-panel p-6">
              <h3 className="mb-3 text-lg font-semibold">Campaign</h3>
              <p className="text-sm leading-relaxed text-muted">Turns verified evidence into a campaign narrative — never beyond what the evidence supports.</p>
            </div>
            <div className="fi-glass-panel fi-safety p-6">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-lg font-semibold">Safety</h3>
                <span className="fi-badge fi-badge--review">veto power</span>
              </div>
              <p className="text-sm leading-relaxed text-muted">Blocks doxxing, harassment, unsupported accusations, and unsafe escalation before anything ships.</p>
            </div>
            <div className="fi-glass-panel p-6">
              <h3 className="mb-3 text-lg font-semibold">Outreach</h3>
              <p className="text-sm leading-relaxed text-muted">Drafts posts, emails, flyers, and public copy — in the language of the community.</p>
            </div>
            <div className="fi-glass-panel p-6">
              <h3 className="mb-3 text-lg font-semibold">Coordinator</h3>
              <p className="text-sm leading-relaxed text-muted">Converts the approved strategy into a concrete volunteer task board.</p>
            </div>
            <div className="fi-glass-panel fi-approved p-6">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-lg font-semibold">Reporter</h3>
                <span className="fi-badge fi-badge--approved">packet</span>
              </div>
              <p className="text-sm leading-relaxed text-muted">Assembles the final provenance and audit packet, including every safety verdict.</p>
            </div>
          </div>
        </section>

        {/* 4. Safety veto loop */}
        <section id="veto" className="border-t py-16" style={{ borderColor: "var(--fi-border-soft)", scrollMarginTop: "5rem" }}>
          <p className="fi-eyebrow mb-3" style={{ color: "var(--fi-safety)" }}>The safety veto loop</p>
          <h2 className="mb-3 max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
            Safety can veto the campaign before public release.
          </h2>
          <p className="mb-10 max-w-2xl text-muted">
            This is not a prompt chain. It is a governed workflow — and the rejection is on the record.
          </p>
          <div className="fi-glass-panel max-w-3xl p-6 lg:p-8">
            <div className="fi-mono space-y-4 text-sm">
              <div className="fi-agent-node px-5 py-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs uppercase tracking-widest text-faint">Campaign draft</span>
                </div>
                <p className="leading-relaxed text-white">&ldquo;Restaurant X is lying to its customers.&rdquo;</p>
              </div>
              <div className="flex items-center gap-2 pl-1 text-faint">
                <span className="fi-arrow">↓</span>
                <span className="text-xs">sent to Safety via Band</span>
              </div>
              <div className="fi-agent-node fi-veto px-5 py-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs uppercase tracking-widest text-faint">Safety verdict</span>
                  <span className="fi-badge fi-badge--vetoed">vetoed</span>
                </div>
                <p className="leading-relaxed" style={{ color: "var(--fi-veto)" }}>
                  VETO — unsupported accusation. Requires stronger evidence or softer language.
                </p>
              </div>
              <div className="flex items-center gap-2 pl-1 text-faint">
                <span className="fi-arrow">↻</span>
                <span className="text-xs">returned to Campaign for revision</span>
              </div>
              <div className="fi-agent-node fi-approved px-5 py-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs uppercase tracking-widest text-faint">Rewritten &amp; approved</span>
                  <span className="fi-badge fi-badge--approved">approved</span>
                </div>
                <p className="leading-relaxed text-white">
                  &ldquo;Available evidence does not support the restaurant&rsquo;s &lsquo;compostable&rsquo; claim in
                  local disposal conditions.&rdquo;
                </p>
              </div>
            </div>
          </div>
          <p className="mt-6 max-w-2xl text-sm text-muted">
            The rejected revision ships <span className="text-white">inside the packet</span> —
            governance that only shows its approvals is marketing.
          </p>
        </section>

        {/* 5. Campaign packet */}
        <section id="packet" className="border-t py-16" style={{ borderColor: "var(--fi-border-soft)", scrollMarginTop: "5rem" }}>
          <p className="fi-eyebrow mb-3">The output</p>
          <h2 className="mb-3 max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
            A campaign packet, ready for humans to execute.
          </h2>
          <p className="mb-10 max-w-2xl text-muted">
            Hours of specialist work, governed and auditable. The system assembles it; humans hold the send button.
          </p>
          <div className="fi-glass-panel max-w-3xl p-6 lg:p-8">
            <ul className="fi-mono grid gap-x-8 gap-y-4 text-sm sm:grid-cols-2">
              <li className="flex items-center gap-3"><span style={{ color: "var(--fi-evidence)" }}>▪</span> Evidence brief</li>
              <li className="flex items-center gap-3"><span style={{ color: "var(--fi-safety)" }}>▪</span> Risk-reviewed campaign message</li>
              <li className="flex items-center gap-3"><span style={{ color: "var(--fi-accent)" }}>▪</span> Outreach copy</li>
              <li className="flex items-center gap-3"><span style={{ color: "var(--fi-accent)" }}>▪</span> Volunteer task plan</li>
              <li className="flex items-center gap-3"><span style={{ color: "var(--fi-evidence)" }}>▪</span> Source / provenance report</li>
              <li className="flex items-center gap-3"><span style={{ color: "var(--fi-approved)" }}>▪</span> Safety audit log</li>
            </ul>
          </div>
        </section>

        {/* 6. Architecture */}
        <section id="architecture" className="border-t py-16" style={{ borderColor: "var(--fi-border-soft)", scrollMarginTop: "5rem" }}>
          <p className="fi-eyebrow mb-3">The architecture</p>
          <h2 className="mb-10 max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
            Why Band + FI + Safety.
          </h2>
          <div className="grid gap-5 md:grid-cols-3">
            <div className="fi-glass-panel p-6">
              <h3 className="mb-2 text-lg font-semibold" style={{ color: "var(--fi-accent)" }}>Band</h3>
              <p className="text-sm leading-relaxed text-muted">Coordinates agent handoffs, shared context, and workflow state — the visible coordination layer.</p>
            </div>
            <div className="fi-glass-panel p-6">
              <h3 className="mb-2 text-lg font-semibold" style={{ color: "var(--fi-evidence)" }}>FI</h3>
              <p className="text-sm leading-relaxed text-muted">Stores provenance, memory, evidence trails, and audit artifacts across the whole run.</p>
            </div>
            <div className="fi-glass-panel p-6">
              <h3 className="mb-2 text-lg font-semibold" style={{ color: "var(--fi-safety)" }}>Safety</h3>
              <p className="text-sm leading-relaxed text-muted">Reviews every public-facing action before release. <span className="text-white">Legal-risk-aware by design.</span></p>
            </div>
          </div>
          <p className="fi-mono mt-8 text-sm text-faint">
            Insult AI cross-examined claims. <span className="text-white">Activist OS coordinates evidence-backed action.</span>
          </p>
        </section>

        {/* 7. Final CTA */}
        <section className="border-t py-20 lg:py-28" style={{ borderColor: "var(--fi-border-soft)" }}>
          <div
            className="fi-glass-panel p-10 text-center lg:p-14"
            style={{ background: "color-mix(in srgb, var(--fi-surface), var(--fi-accent) 4%)" }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/branding/logo-white.png"
              alt="Activist OS — Evidence. Coordination. Safety."
              width={320}
              height={175}
              className="mx-auto mb-6 w-full max-w-[16rem] opacity-90"
            />
            <h2 className="mx-auto mb-4 max-w-2xl text-3xl font-bold tracking-tight md:text-4xl">
              Turn a community concern into safe, coordinated action.
            </h2>
            <p className="mx-auto mb-8 max-w-xl text-muted">
              First use case: vegan and ecological community campaigns, including greenwashing
              detection and local action planning.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              <Link href="/app" className="fi-btn fi-btn--primary">Launch Activist OS →</Link>
              <Link href="/app" className="fi-btn fi-btn--ghost">Open coordination console</Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t py-10" style={{ borderColor: "var(--fi-border-soft)" }}>
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-sm text-faint sm:flex-row">
          <div className="flex items-center gap-2.5">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/branding/emblem.png" alt="Activist OS" className="h-6 w-6 rounded" />
            <span className="fi-mono">Activist OS · Free Intelligence</span>
          </div>
          <p>Built for the Band of Agents Hackathon · Regulated &amp; High-Stakes Workflows</p>
        </div>
      </footer>
    </div>
  );
}
