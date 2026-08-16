"use client";

import { motion } from "framer-motion";
import {
  Workflow,
  Activity,
  Orbit,
  Share2,
  GitBranch,
  Server,
} from "lucide-react";

const ACCENTS = {
  blue: { icon: "bg-core-blue/10 text-core-blue", glow: "group-hover:shadow-glow-blue" },
  cyan: { icon: "bg-core-cyan/10 text-core-cyan", glow: "group-hover:shadow-glow-cyan" },
  violet: { icon: "bg-core-violet/10 text-core-violet", glow: "group-hover:shadow-glow-violet" },
  emerald: { icon: "bg-core-emerald/10 text-core-emerald", glow: "group-hover:shadow-glow-emerald" },
} as const;

const FEATURES = [
  {
    icon: Workflow,
    name: "Workflow Studio",
    copy: "Wire up agents on an infinite canvas. Connections carry real data, not just arrows.",
    accent: "blue",
  },
  {
    icon: Activity,
    name: "Runtime Monitor",
    copy: "Watch each run move from research to execution, node by node, in real time.",
    accent: "cyan",
  },
  {
    icon: Orbit,
    name: "Memory Galaxy",
    copy: "Every memory is a star. Related ideas sit close together — fly through to find one.",
    accent: "cyan",
  },
  {
    icon: Share2,
    name: "Knowledge Graph",
    copy: "Explore what your agents know as a living map, not a list of documents.",
    accent: "violet",
  },
  {
    icon: GitBranch,
    name: "Decision Center",
    copy: "See why an agent chose what it chose — reasoning, references, and confidence, laid out plainly.",
    accent: "emerald",
  },
  {
    icon: Server,
    name: "Infrastructure",
    copy: "Workers, queues, and containers rendered as a health map instead of a log file.",
    accent: "blue",
  },
] as const;

export default function Features() {
  return (
    <section id="features" className="relative mx-auto max-w-6xl px-6 py-28">
      <div className="mb-14 max-w-xl">
        <p className="eyebrow mb-4">What's running underneath</p>
        <h2 className="font-display text-[32px] font-medium leading-tight text-ink sm:text-[38px]">
          Six surfaces. One runtime.
        </h2>
        <p className="mt-4 text-[15px] leading-relaxed text-ink-muted">
          Each surface below is a window into the same cognitive process — the
          same run, viewed from a different angle.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f, i) => {
          const Icon = f.icon;
          return (
            <motion.div
              key={f.name}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.55, ease: "easeOut", delay: (i % 3) * 0.08 }}
              className="glass-panel group relative overflow-hidden p-6 transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.12]"
            >
              <div
                className={`mb-5 flex h-10 w-10 items-center justify-center rounded-lg border border-white/[0.08] ${ACCENTS[f.accent].icon} transition-shadow duration-300 ${ACCENTS[f.accent].glow}`}
              >
                <Icon className="h-5 w-5" strokeWidth={1.6} />
              </div>
              <h3 className="font-display text-[17px] font-medium text-ink">{f.name}</h3>
              <p className="mt-2 text-[13.5px] leading-relaxed text-ink-muted">{f.copy}</p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
