"use client";

import { motion } from "framer-motion";

const TRADITIONAL = [
  "Stores information",
  "Requires searching",
  "Manual workflows",
  "Context switching",
  "Static databases",
];

const BIZOS = [
  "Understands",
  "Remembers",
  "Reasons",
  "Acts",
  "Continuous context",
  "Unified intelligence",
];

export function Comparison() {
  return (
    <section className="relative mx-auto max-w-6xl px-6 py-28 border-t border-white/[0.04]">
      <div className="mb-16 text-center">
        <p className="eyebrow mb-4">Philosophy</p>
        <h2 className="font-display text-[32px] md:text-[40px] font-medium leading-tight text-ink">
          A fundamental shift in computing.
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="glass-panel p-10 md:p-14 border-white/[0.04]"
        >
          <h3 className="font-mono text-[13px] uppercase tracking-widest text-ink-muted mb-8 pb-4 border-b border-white/[0.06]">
            Traditional Software
          </h3>
          <ul className="space-y-6">
            {TRADITIONAL.map((item) => (
              <li key={item} className="flex items-center gap-4">
                <span className="w-1.5 h-1.5 rounded-full bg-white/20" />
                <span className="text-[16px] text-ink-muted">{item}</span>
              </li>
            ))}
          </ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
          className="glass-panel p-10 md:p-14 relative overflow-hidden border-accent/20"
        >
          <div className="absolute inset-0 bg-accent/5 pointer-events-none" />
          <h3 className="relative z-10 font-mono text-[13px] uppercase tracking-widest text-accent mb-8 pb-4 border-b border-accent/20">
            BizOS
          </h3>
          <ul className="relative z-10 space-y-6">
            {BIZOS.map((item) => (
              <li key={item} className="flex items-center gap-4">
                <span className="w-2 h-2 rounded-full bg-accent shadow-[0_0_8px_var(--accent-primary)]" />
                <span className="text-[16px] text-ink font-medium">{item}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      </div>
    </section>
  );
}
