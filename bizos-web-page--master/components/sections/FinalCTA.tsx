"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { MagneticButton } from "@/components/ui/MagneticButton";

export function FinalCTA() {
  return (
    <section className="relative mx-auto max-w-5xl px-6 py-28 md:py-40 text-center">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col items-center"
      >
        <motion.p
          initial={{ opacity: 0, y: 15 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="eyebrow mb-6"
        >
          Initialize the core
        </motion.p>

        <motion.h2
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.75, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="font-display text-[44px] md:text-[68px] lg:text-[84px] font-semibold leading-[1.08] tracking-tight text-ink mb-6"
        >
          Ready to watch it think?
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="max-w-2xl text-[16px] md:text-[19px] leading-relaxed text-ink-muted font-light mb-12"
        >
          Step into a living cognitive environment. Watch memory, knowledge, reasoning, and execution converge in real-time.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.42, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col sm:flex-row items-center gap-5 w-full sm:w-auto"
        >
          <MagneticButton
            onClick={() => window.location.href = "/auth/signup"}
            className="group flex items-center justify-center gap-2.5 rounded-full bg-accent hover:bg-accent-hover px-9 py-4 text-[15px] font-semibold text-white transition-all duration-300 hover:scale-[1.04] active:scale-[0.98] hover:-translate-y-0.5 shadow-[0_6px_24px_rgba(232,123,42,0.2)] hover:shadow-[0_14px_36px_rgba(232,123,42,0.35)] w-full sm:w-auto text-center cursor-pointer"
          >
            Get Started
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </MagneticButton>
          <a
            href="mailto:hello@bizos.ai"
            className="rounded-full border-2 border-[color:var(--border-color)] bg-[#F5F1E8] dark:bg-zinc-900 px-9 py-4 text-[15px] font-medium text-ink transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] hover:bg-[#E0F2FE] dark:hover:bg-[#0F2338] hover:border-[#38BDF8] hover:text-[#0EA5E9] hover:shadow-[0_8px_20px_rgba(0,0,0,0.06)] w-full sm:w-auto text-center shadow-[0_2px_8px_rgba(23,23,23,0.02)]"
          >
            Request Early Access
          </a>
        </motion.div>
      </motion.div>
    </section>
  );
}
