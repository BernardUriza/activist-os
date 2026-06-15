# UI — single source of truth

**The ONLY product-UI source of truth is the Next.js app in `web/`** (this repo's
canonical web package: Next + fi-glass + `@free-intelligence/core`).

No new UI feature, visual polish, API client, SSE behavior, branding change, or
demo logic may be implemented anywhere else.

## Reference / archive only — NEVER a build target
- The old standalone `web/*.html` (`demo.html`, `index.html`, `checklist.html`)
  — static HTML demo shells. **Reference for what the demo communicated; never
  edited, never shipped, never the source of a feature.**
- The previously-deployed `free-intelligence/apps/activist-os/web` Next app —
  reference for visual tokens / the Safety-Gate presentation model to PORT into
  this `web/`, not a parallel surface to keep building.

## Why
Static HTML "for quick" was the black hole (coagent, 2026-06-14): tests measured
one thing, local Next another, the official domain another, legacy HTML another —
four "truths." First ONE truth (this `web/`), then everything else. A parallel UI
surface outside `web/` is a violation, not a convenience. See [[new-project-stack]]
(no plain HTML outside the declared app).
