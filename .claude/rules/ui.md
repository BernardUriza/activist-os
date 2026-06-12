# UI — fi-glass, the og118 way

The demo UI does **not** get built from scratch. It consumes
[`fi-glass`](https://github.com/BernardUriza/free-intelligence/tree/main/apps/packages/fi-glass)
— the glassmorphism material for Free Intelligence chat frontends — exactly
as `apps/og118/web` already does. This is dogfooding AND speed: og118 proved
the integration pattern; copy it, don't reinvent it.

## Why fi-glass fits this product

`fi-glass/agent` ships **glass-box agentic UI** — `AgentConversationSurface`
+ `useAgentConversation` render the agent's plan and activity as first-class
panels. That is literally the demo requirement (`hackathon.md`): coordination
**visible on screen**, not narrated. The veto moment renders as a glass-box
panel, plan-before-act comes free, and the "FI preserves memory and
provenance" pitch line gets a face.

## The og118 consumption pattern (copy this)

```tsx
// app/layout.tsx
import 'fi-glass/theme.css';        // glassmorphism tokens (--glass-blur, ...)
import 'fi-glass/glass-chat.css';   // the reusable glass chat preset
```

```tsx
// components — pick from the subpaths, don't fork:
import { AgentConversationSurface, useAgentConversation } from 'fi-glass/agent';
import { CopyButton } from 'fi-glass/messages';
// fi-glass/composer · fi-glass/voice · fi-glass/shell · fi-glass/conversation
```

## ⚠️ The Tailwind gotcha (documented in fi-glass README — do not relearn it)

fi-glass ships Tailwind **class strings** in its `dist`, not compiled CSS.
The consumer app must have Tailwind AND glob fi-glass's dist explicitly
(Tailwind ignores `node_modules` by default):

```css
/* Tailwind v4 */
@import 'tailwindcss';
@source '../../packages/fi-glass/dist/**/*.{js,mjs}';
```

Skip this and the message primitives render unstyled. og118's
`globals.css` has the working reference.

## Workspace reality (decide at kickoff, issue #1)

`fi-glass` is `private: true`, consumed as `workspace:*`, license
PolyForm-Noncommercial. Two sane options:

1. **og118 pattern (default)**: the demo UI lives as an app inside the
   free-intelligence monorepo (`apps/activist-os-web` or similar) and
   consumes `fi-glass: workspace:*`. This public repo holds agents,
   contracts, docs — the UI app links back here.
2. Vendored tarball into this repo — only if option 1 fights the Band
   starter's expected layout.

Custom UI work is limited to what og118 also owns: spacing, app-specific
panels (the verdict/veto panel, the packet viewer), branding. Everything
chat/agent-surface shaped comes from fi-glass. If a primitive is missing,
it gets built **upstream in fi-glass** and consumed here (thin-consumer
doctrine, same as fi-runner).

## Build read-only truth before live interaction

Demo UI renders a **real completed run first** (`web/demo.html` reading
`GET /workflow/{run_id}/history`) before any start buttons, SSE streaming,
or editing get built. Impressive interactive UI can hide broken
coordination; a read-only shell over real handoff history cannot. The mock
fallback must label itself as mock on screen — never pass hand-written copy
off as agent output.
