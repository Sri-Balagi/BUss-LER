"use client";

import { motion } from "framer-motion";

const AUDIENCES = [
  {
    team: "Operations",
    copy: "Hand off approvals and routine calls to agents that show their work before they act.",
  },
  {
    team: "Research",
    copy: "Point agents at your knowledge base and watch them cite, connect, and remember what they find.",
  },
  {
    team: "Engineering",
    copy: "Build the workflow once in the Studio, then trust the runtime to run it the same way every time.",
  },
];

export default function Solutions() {
  return (
    <section id="solutions" className="relative mx-auto max-w-6xl px-6 py-28">
      <div className="mb-14 flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
        <div className="max-w-md">
          <p className="eyebrow mb-4">Built to be handed real work</p>
          <h2 className="font-display text-[32px] font-medium leading-tight text-ink sm:text-[38px]">
            Wherever decisions pile up.
          </h2>
        </div>
        <a
          href="#contact"
          className="text-[13px] text-ink-muted underline decoration-white/20 underline-offset-4 transition-colors hover:text-ink"
        >
          Talk to us about your team →
        </a>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {AUDIENCES.map((a, i) => (
          <motion.div
            key={a.team}
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.55, ease: "easeOut", delay: i * 0.08 }}
            className="glass-panel p-6"
          >
            <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-core-cyan">
              {a.team}
            </span>
            <p className="mt-3 text-[14px] leading-relaxed text-ink-muted">{a.copy}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
