"use client";

import { motion } from "framer-motion";
import { HardDrive, BookOpen, Brain, Target, Bot, Activity } from "lucide-react";

const MODULES = [
  {
    icon: HardDrive,
    title: "Persistent Memory",
    desc: "Long-term episodic and semantic storage. Allows the system to recall past states, user preferences, and historical execution paths instantly.",
    status: "Active",
  },
  {
    icon: BookOpen,
    title: "Knowledge Engine",
    desc: "Graph-based representation of business rules, entity relationships, and constraints. Provides factual grounding for all operations.",
    status: "Active",
  },
  {
    icon: Brain,
    title: "Reasoning Engine",
    desc: "Dynamic logic synthesis. Evaluates context against knowledge and memory to determine the optimal sequence of actions.",
    status: "Processing",
  },
  {
    icon: Target,
    title: "Goal Planning",
    desc: "Translates high-level intent into multi-step tactical plans, constantly re-evaluating feasibility as environmental variables shift.",
    status: "Active",
  },
  {
    icon: Bot,
    title: "AI Agents",
    desc: "Autonomous micro-workers specializing in domain-specific tasks. Dispatched dynamically based on reasoning engine output.",
    status: "Standby",
  },
  {
    icon: Activity,
    title: "Workflow Automation",
    desc: "The execution layer. Interfaces with external APIs and internal systems to commit actions and record state changes.",
    status: "Active",
  },
];

export function Capabilities() {
  return (
    <section className="relative mx-auto max-w-6xl px-6 py-28 border-t border-white/[0.04]">
      <div className="mb-16">
        <p className="eyebrow mb-4">Core Architecture</p>
        <h2 className="font-display text-[32px] md:text-[40px] font-medium leading-tight text-ink">
          Operating System Modules.
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {MODULES.map((mod, i) => (
          <motion.div
            key={mod.title}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            className="flex flex-col justify-between p-6 rounded-[20px] bg-white/[0.02] border border-white/[0.05] hover:border-white/[0.1] transition-colors"
          >
            <div>
              <div className="flex items-center justify-between mb-8">
                <mod.icon className="w-5 h-5 text-ink-muted" strokeWidth={1.5} />
                <div className="flex items-center gap-2">
                  <span className={`w-1.5 h-1.5 rounded-full ${mod.status === "Processing" ? "bg-accent animate-pulse" : mod.status === "Active" ? "bg-[#00F0FF]" : "bg-white/20"}`} />
                  <span className="font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                    {mod.status}
                  </span>
                </div>
              </div>
              <h3 className="font-display text-[16px] font-medium text-ink mb-3">{mod.title}</h3>
              <p className="text-[14px] leading-relaxed text-ink-muted font-light">
                {mod.desc}
              </p>
            </div>
            
            <div className="mt-8 pt-4 border-t border-white/[0.04] flex items-center justify-between">
              <span className="font-mono text-[10px] text-ink-faint">sys.module.{mod.title.toLowerCase().replace(" ", "_")}</span>
              <span className="font-mono text-[10px] text-ink-faint">v2.4.0</span>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
