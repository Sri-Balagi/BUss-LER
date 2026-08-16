"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Cpu,
  BrainCircuit,
  HardDrive,
  Network,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

const FEATURES = [
  {
    icon: Cpu,
    name: "Autonomous Operations",
    copy: "Eliminate repetitive manual tasks by orchestrating intelligent agent workflows across your core enterprise operations.",
    color: {
      bg: "bg-[#FFF7ED] dark:bg-[#2A1810]",
      border: "border-[#F97316]/40",
      text: "text-[#EA580C] dark:text-[#F97316]",
      shadow: "shadow-[0_4px_16px_rgba(249,115,22,0.18)]",
      hoverBg: "group-hover:bg-[#FFEDD5]",
    },
  },
  {
    icon: BrainCircuit,
    name: "Intelligent Decision-Making",
    copy: "Accelerate high-stakes business calls with real-time confidence scoring, clear reasoning traces, and policy safeguards.",
    color: {
      bg: "bg-[#F0F9FF] dark:bg-[#0F2338]",
      border: "border-[#38BDF8]/40",
      text: "text-[#0EA5E9] dark:text-[#38BDF8]",
      shadow: "shadow-[0_4px_16px_rgba(56,189,248,0.18)]",
      hoverBg: "group-hover:bg-[#E0F2FE]",
    },
  },
  {
    icon: HardDrive,
    name: "Institutional Memory",
    copy: "Preserve critical business context and historical knowledge across teams so insights and learnings are never lost.",
    color: {
      bg: "bg-[#F5F3FF] dark:bg-[#1E1735]",
      border: "border-[#A855F7]/40",
      text: "text-[#8B5CF6] dark:text-[#A855F7]",
      shadow: "shadow-[0_4px_16px_rgba(168,85,247,0.18)]",
      hoverBg: "group-hover:bg-[#EDE9FE]",
    },
  },
  {
    icon: Network,
    name: "Agent Orchestration",
    copy: "Coordinate multi-agent teams seamlessly, assigning specialized roles, strict operational boundaries, and shared context.",
    color: {
      bg: "bg-[#ECFDF5] dark:bg-[#0A261D]",
      border: "border-[#10B981]/40",
      text: "text-[#10B981] dark:text-[#34D399]",
      shadow: "shadow-[0_4px_16px_rgba(16,185,129,0.18)]",
      hoverBg: "group-hover:bg-[#D1FAE5]",
    },
  },
  {
    icon: Sparkles,
    name: "Continuous Learning",
    copy: "Improve organizational efficiency automatically as every completed task refines future execution accuracy.",
    color: {
      bg: "bg-[#EEF2FF] dark:bg-[#161B3A]",
      border: "border-[#6366F1]/40",
      text: "text-[#6366F1] dark:text-[#818CF8]",
      shadow: "shadow-[0_4px_16px_rgba(99,102,241,0.18)]",
      hoverBg: "group-hover:bg-[#E0E7FF]",
    },
  },
  {
    icon: ShieldCheck,
    name: "Enterprise Governance",
    copy: "Maintain full compliance and control with transparent audit streams, role permissions, and human-in-the-loop overrides.",
    color: {
      bg: "bg-[#FEF3C7] dark:bg-[#2E200C]",
      border: "border-[#F59E0B]/40",
      text: "text-[#D97706] dark:text-[#FBBF24]",
      shadow: "shadow-[0_4px_16px_rgba(245,158,11,0.18)]",
      hoverBg: "group-hover:bg-[#FDE68A]",
    },
  },
] as const;

export default function Features() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section id="features" className="relative w-full border-t border-[color:var(--border-color)] bg-[#F5F1E8] dark:bg-[#161513]">
      <div className="mx-auto max-w-6xl px-6 py-24 md:py-36">
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
          className="mb-16 max-w-3xl"
        >
          <p className="eyebrow mb-4">Enterprise Value</p>
          <h2 className="font-display text-[42px] md:text-[56px] font-semibold leading-[1.1] tracking-tight text-ink">
            Quantifiable business impact at scale.
          </h2>
          <p className="mt-6 text-[16px] md:text-[18px] leading-relaxed text-ink-muted font-light">
            BizOS transforms fragmented manual workflows into coordinated, autonomous business operations with continuous enterprise learning and transparent governance.
          </p>
        </motion.div>

        <div className="grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            const isFocused = hoveredIndex === i;
            const isBlurred = hoveredIndex !== null && !isFocused;

            return (
              <motion.div
                key={f.name}
                initial={{ opacity: 0, y: 28 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
                transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1], delay: 0.2 + (i % 3) * 0.1 }}
                className="w-full"
              >
                <motion.div
                  animate={isFocused ? { y: 0 } : { y: [0, -4, 0] }}
                  transition={
                    isFocused
                      ? { duration: 0.2 }
                      : { duration: 5.5 + (i % 3) * 0.8, repeat: Infinity, ease: "easeInOut", delay: i * 0.4 }
                  }
                  className={`glass-panel group relative overflow-hidden p-8 md:p-9 transition-all duration-300 ease-out rounded-[28px] border-2 h-full ${
                    isFocused
                      ? "!border-[#38BDF8] !bg-[#F0F9FF] dark:!bg-[#0F172A] !shadow-[0_16px_36px_rgba(0,0,0,0.08)] -translate-y-1 scale-[1.01] z-10"
                      : isBlurred
                      ? "border-[color:var(--border-color)] bg-[#F5F1E8]/70 dark:bg-zinc-900/70 opacity-40 blur-[1.5px] scale-[0.98]"
                      : "border-[color:var(--border-color)] bg-[#FAF7F2] dark:bg-zinc-900 shadow-[0_4px_24px_rgba(23,23,23,0.03)] hover:shadow-[0_16px_36px_rgba(0,0,0,0.08)] hover:border-[#38BDF8] hover:bg-[#F0F9FF] hover:-translate-y-1"
                  }`}
                >
                  {/* Rich Meaningful Color-Coded Icon Badge */}
                  <div
                    className={`mb-6 flex h-13 w-13 items-center justify-center rounded-2xl border-2 transition-all duration-300 ${f.color.bg} ${f.color.border} ${f.color.text} ${f.color.shadow} ${f.color.hoverBg} group-hover:scale-105`}
                  >
                    <Icon className="h-6 w-6 transition-transform duration-300 group-hover:scale-105" strokeWidth={1.75} />
                  </div>

                  <h3 className="font-display text-[19px] font-semibold text-ink tracking-tight">{f.name}</h3>
                  <p className="mt-3 text-[14.5px] leading-relaxed text-ink-muted font-light">{f.copy}</p>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
