"use client";

import { motion } from "framer-motion";
import { ArrowRight, Circle } from "lucide-react";
import dynamic from "next/dynamic";

const CognitiveCore = dynamic(() => import("./CognitiveCore"), { ssr: false });

const STATUS = [
  { label: "Cognitive layer", color: "bg-core-blue" },
  { label: "Memory platform", color: "bg-core-cyan" },
  { label: "Decision engine", color: "bg-core-emerald" },
];

export default function Hero() {
  return (
    <section id="top" className="relative mx-auto max-w-6xl px-6 pb-24 pt-40 sm:pt-48">
      <div className="grid items-center gap-16 lg:grid-cols-[1.1fr_0.9fr]">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut", delay: 0.1 }}
        >
          <p className="eyebrow mb-6">Cognitive runtime for the enterprise</p>
          <h1 className="font-display text-[42px] font-medium leading-[1.08] tracking-tight text-ink sm:text-[56px]">
            Give your business
            <br />
            <span className="bg-gradient-to-r from-core-blue via-core-cyan to-core-violet bg-clip-text text-transparent">
              a mind of its own.
            </span>
          </h1>
          <p className="mt-6 max-w-lg text-[16px] leading-relaxed text-ink-muted">
            BizOS runs the full loop of thought as live infrastructure — research,
            memory, knowledge, reasoning, decision, execution — so you can watch
            intelligence move through your business, not just read its output.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-4">
            <a
              href="/auth/signup"
              className="group flex items-center gap-2 rounded-full bg-ink px-6 py-3 text-[14px] font-medium text-void transition-transform hover:scale-[1.02]"
            >
              Get Started
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </a>
            <a
              href="#architecture"
              className="rounded-full border border-white/10 px-6 py-3 text-[14px] text-ink-muted transition-colors hover:border-white/20 hover:text-ink"
            >
              See it think
            </a>
          </div>

          <div className="mt-12 flex flex-wrap gap-x-8 gap-y-3 font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
            {STATUS.map((s) => (
              <div key={s.label} className="flex items-center gap-2">
                <Circle className={`h-2 w-2 rounded-full ${s.color} fill-current`} strokeWidth={0} />
                {s.label}
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.9, ease: "easeOut", delay: 0.25 }}
          className="relative mx-auto flex items-center justify-center"
        >
          <div className="absolute h-[380px] w-[380px] rounded-full bg-core-blue/10 blur-[90px]" />
          <CognitiveCore size={440} />
        </motion.div>
      </div>
    </section>
  );
}
