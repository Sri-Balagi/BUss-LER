"use client";

import { motion } from "framer-motion";

export default function Pricing() {
  return (
    <section id="pricing" className="relative mx-auto max-w-6xl px-6 py-28">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.55, ease: "easeOut" }}
        className="glass-panel flex flex-col items-start gap-6 p-10 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <p className="eyebrow mb-4">Pricing</p>
          <h2 className="font-display text-[26px] font-medium text-ink">
            Plans are still being shaped around real usage.
          </h2>
          <p className="mt-3 max-w-md text-[14px] leading-relaxed text-ink-muted">
            We're finalizing tiers with the teams already running BizOS.
            Tell us what you'd run through it and we'll figure out the right
            plan together.
          </p>
        </div>
        <a
          href="#contact"
          className="shrink-0 rounded-full bg-ink px-6 py-3 text-[14px] font-medium text-void transition-transform hover:scale-[1.02]"
        >
          Get early pricing
        </a>
      </motion.div>
    </section>
  );
}
