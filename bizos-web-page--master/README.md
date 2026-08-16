# BizOS — Landing Page

The public landing page for BizOS, an "AI operating system." Built with
Next.js 15 (App Router), React 19, TypeScript, Tailwind, and Framer Motion.

## Run it

```bash
npm install
npm run dev
```

Then open http://localhost:3000. First load plays a short boot sequence
("BizOS — initializing… memory platform online… decision engine ready…")
before revealing the page; it only plays once per browser session.

```bash
npm run build && npm run start   # production build
```

> This project was built in a sandboxed environment without access to
> `fonts.googleapis.com`, so `npm run build` couldn't be verified here with
> the real fonts wired in (Space Grotesk / Inter / JetBrains Mono via
> `next/font/google`). Everything else — components, types, Tailwind config —
> was fully compiled and checked. On a machine with normal internet access,
> `next/font` will fetch and self-host the fonts automatically at build time;
> no other changes are needed.

## Design system

- **Palette** — near-black `#05070A` base, glass panels in translucent white,
  four accent colors each tied to a cognitive subsystem rather than used
  decoratively: electric blue (core/runtime), cyan (memory), violet
  (knowledge), emerald (decision).
- **Type** — Space Grotesk for display headings, Inter for body copy,
  JetBrains Mono for system/status text (the boot sequence, eyebrows, the
  architecture step numbers) — the monospace is doing real work signaling
  "this is the machine talking."
- **Signature element** — the Cognitive Core in the hero (`components/CognitiveCore.tsx`):
  a canvas-rendered rotating sphere of connected nodes with colored pulses
  traveling along real connections, each pulse colored by which subsystem
  it represents. It's meant to be the one thing this page is remembered by.
- **Motion** — kept to a few deliberate moments (boot sequence, hero
  reveal, the pulse sweeping through the Architecture pipeline, card
  hover-lift) rather than animating everything, per the "quiet unless it's
  saying something" direction. `prefers-reduced-motion` is respected
  throughout.

## Structure

```
app/
  layout.tsx      fonts + metadata
  page.tsx        composes the sections below
  globals.css     tokens, glass utility, reduced-motion overrides
components/
  BootSequence.tsx    one-time OS boot overlay
  NeuralBackground.tsx  faint ambient particle field (canvas)
  CognitiveCore.tsx     signature hero visual (canvas)
  Nav.tsx               floating glass nav + live status dot
  Hero.tsx
  Features.tsx          six product surfaces
  Architecture.tsx      the real Research→…→Execution run sequence
  Solutions.tsx         by-team teaser
  Pricing.tsx           honest placeholder (tiers aren't finalized yet)
  Footer.tsx            closing CTA + about/contact/docs links
```

## Authenticated dashboard (`/dashboard`)

The flagship surface. Everything on it is driven by one shared, client-side
"live" engine (`lib/dashboard/state.tsx`) that ticks every ~1.8s and nudges
agents, pipeline counts, memory events, infrastructure metrics, and the
audit log together — so the widgets read as one cognitive system rather
than eight disconnected cards. No backend is wired up; this is a fully
interactive simulation.

- **Sidebar** — floating glass icon rail that expands on hover; only
  Dashboard is live, other items surface a small "not wired up yet" toast
  instead of dead links.
- **Runtime Overview** — the flagship widget: the Research→…→Execution
  pipeline as live bars with traveling signal pulses. Click a stage to
  filter the Agent Fleet below by it.
- **Agent Fleet** — live roster with status pulses and animated confidence
  bars; click a card for a detail panel.
- **Memory Galaxy (mini)** — canvas of recent memory writes/retrievals as
  glowing stars; hover for detail.
- **Knowledge Graph (mini)** — SVG graph with a live traversal pulse;
  hover a node to highlight its neighbors.
- **Decision Center** — a real (client-side) approve/reject queue.
- **Goal Manager** — expandable/collapsible animated goal tree.
- **Infrastructure Health** — animated radial gauges instead of a table.
- **Audit Log** — terminal-style feed of what the system just did.

## Next steps

The brief also calls out dedicated public pages (Features, Architecture,
Solutions, Pricing, Docs, About, Contact) and deeper authenticated surfaces
(Workflow Studio, Runtime Monitor, Memory Galaxy, Knowledge Graph, Goal
Manager, Decision Center, Infrastructure, Metrics, Audit Logs, Settings) as
their own full pages — happy to build any of those next using the same
token system and live-state engine.
