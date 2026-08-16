"use client";

import { motion } from "framer-motion";

const STEPS = [
  { n: "01", label: "Research" },
  { n: "02", label: "Memory" },
  { n: "03", label: "Knowledge" },
  { n: "04", label: "Reasoning" },
  { n: "05", label: "Decision" },
  { n: "06", label: "Approval" },
  { n: "07", label: "Execution" },
];

export default function Architecture() {
  return (
    <section id="architecture" className="relative mx-auto max-w-6xl px-6 py-28">
      <div className="mb-16 max-w-xl">
        <p className="eyebrow mb-4">How a run actually moves</p>
        <h2 className="font-display text-[32px] font-medium leading-tight text-ink sm:text-[38px]">
          Every task takes the same path.
        </h2>
        <p className="mt-4 text-[15px] leading-relaxed text-ink-muted">
          BizOS doesn't hide the reasoning behind a spinner. Each run is this
          exact sequence, and the Runtime Monitor lets you watch it happen
          step by step.
        </p>
      </div>

      <div className="glass-panel overflow-x-auto p-8 sm:p-10">
        <div className="relative flex min-w-[640px] items-center justify-between">
          <div className="absolute left-0 right-0 top-5 h-px bg-white/[0.08]" />
          <motion.div
            className="absolute top-[18px] h-1.5 w-1.5 rounded-full bg-core-cyan shadow-glow-cyan"
            animate={{ left: ["0%", "100%"] }}
            transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
          />
          {STEPS.map((step) => (
            <div key={step.n} className="relative z-10 flex flex-col items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full border border-white/[0.1] bg-panel font-mono text-[11px] text-ink-muted">
                {step.n}
              </div>
              <span className="font-display text-[13px] text-ink-muted">{step.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
