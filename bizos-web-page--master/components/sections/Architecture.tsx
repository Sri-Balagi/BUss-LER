"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Target,
  Network,
  Cpu,
  Scale,
  Workflow,
  CheckCircle2,
} from "lucide-react";

const STEPS = [
  { n: "01", label: "Ingestion", icon: Target, desc: "Telemetry Capture" },
  { n: "02", label: "Topology", icon: Network, desc: "Enterprise Context" },
  { n: "03", label: "Synthesis", icon: Cpu, desc: "Multi-Model Logic" },
  { n: "04", label: "Governance", icon: Scale, desc: "Policy Safeguards" },
  { n: "05", label: "Coordination", icon: Workflow, desc: "Agent Delegation" },
  { n: "06", label: "Verification", icon: CheckCircle2, desc: "State & Audit" },
];

export function Architecture() {
  const [hoveredStep, setHoveredStep] = useState<number | null>(null);

  return (
    <section id="architecture" className="relative mx-auto max-w-6xl px-6 py-24 md:py-36 border-t border-[color:var(--border-color)]">
      <motion.div
        initial={{ opacity: 0, y: 25 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
        className="mb-16 max-w-2xl text-center md:text-left mx-auto md:mx-0"
      >
        <p className="eyebrow mb-4">Enterprise Reliability & Governance</p>
        <h2 className="font-display text-[42px] md:text-[56px] font-semibold leading-[1.1] tracking-tight text-ink">
          Deterministic safeguards for enterprise-wide execution.
        </h2>
        <p className="mt-4 text-[16px] md:text-[18px] leading-relaxed text-ink-muted font-light">
          Every business function operates under strict architectural guardrails that guarantee repeatable logic, total auditability, transparent policy compliance, and zero black-box drift across all enterprise operations.
        </p>
      </motion.div>

      {/* High-Precision 6-Stage Timeline with Light Sky Blue Accents & Clean Neutral Shadow */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.8, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
        className="glass-panel overflow-x-auto p-10 sm:p-14 md:p-16 relative rounded-[32px] bg-[#FAF7F2]/90 dark:bg-zinc-900 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_16px_36px_rgba(0,0,0,0.08)] hover:border-[#38BDF8] hover:-translate-y-1 transition-all duration-300 ease-out"
      >
        <div className="relative flex min-w-[980px] md:min-w-full items-start justify-between pt-3 pb-4 px-12 sm:px-16">
          
          {/* Base Connecting Line (Positioned exactly through center of node circles at top-9 sm:top-10) */}
          <div className="absolute left-20 right-20 top-9 sm:top-10 h-[3px] bg-[#E2DAD0] dark:bg-zinc-800 pointer-events-none" />

          {/* Animated Progress Fill Line */}
          <motion.div
            className="absolute left-20 top-9 sm:top-10 h-[3px] bg-gradient-to-r from-accent via-[#F97316] to-[#38BDF8] pointer-events-none"
            animate={{ width: ["0%", "calc(100% - 160px)"] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          />

          {/* Animated Progress Dot (Centered perfectly on the line) */}
          <motion.div
            className="absolute top-9 sm:top-10 z-20 pointer-events-none -translate-x-1/2 -translate-y-1/2"
            animate={{ left: ["80px", "calc(100% - 80px)"] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          >
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-accent/25 dark:bg-[#38BDF8]/25 backdrop-blur-sm shadow-[0_0_18px_rgba(232,123,42,0.9)]">
              <div className="h-2.5 w-2.5 rounded-full bg-accent dark:bg-[#38BDF8] ring-2 ring-white dark:ring-zinc-900" />
            </div>
          </motion.div>

          {/* 6 Stage Nodes with Balanced ~80px Clearance */}
          {STEPS.map((step, idx) => {
            const Icon = step.icon;
            const isHovered = hoveredStep === idx;
            const isBlurred = hoveredStep !== null && !isHovered;

            return (
              <motion.div
                key={step.n}
                initial={{ opacity: 0, scale: 0.85, y: 15 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.55, delay: 0.25 + idx * 0.09, ease: [0.16, 1, 0.3, 1] }}
                onMouseEnter={() => setHoveredStep(idx)}
                onMouseLeave={() => setHoveredStep(null)}
                className={`relative z-10 flex flex-col items-center gap-3.5 cursor-pointer transition-all duration-300 w-[140px] shrink-0 text-center ${
                  isBlurred ? "opacity-35 blur-[1.5px]" : "opacity-100"
                }`}
              >
                {/* Stage Circle Node with Hover Zoom */}
                <motion.div
                  animate={
                    isHovered
                      ? { scale: 1.15, y: -4 }
                      : { scale: 1, y: 0 }
                  }
                  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                  className={`flex h-16 w-16 sm:h-18 sm:w-18 flex-col items-center justify-center rounded-full border-2 transition-all duration-300 ${
                    isHovered
                      ? "border-[#38BDF8] bg-[#F0F9FF] text-[#0EA5E9] dark:border-[#38BDF8] dark:bg-[#0F172A] dark:text-[#38BDF8] shadow-[0_6px_20px_rgba(0,0,0,0.06)]"
                      : "border-[#E2DAD0] bg-white dark:bg-zinc-900 text-ink-muted hover:border-[#38BDF8] hover:text-[#0EA5E9] hover:bg-[#F0F9FF]"
                  }`}
                >
                  <Icon
                    className={`h-5.5 sm:h-6 w-5.5 sm:w-6 transition-transform duration-300 ${
                      isHovered ? "scale-110 text-[#0EA5E9] dark:text-[#38BDF8]" : "text-ink-muted"
                    }`}
                    strokeWidth={1.75}
                  />
                  <span className="font-mono text-[10px] sm:text-[11px] font-bold tracking-wider mt-0.5 opacity-80">
                    {step.n}
                  </span>
                </motion.div>

                {/* Stage Title & Subtitle Labels */}
                <div className="w-full text-center flex flex-col items-center justify-center">
                  <p
                    className={`font-display text-[15.5px] sm:text-[16.5px] font-bold tracking-tight transition-colors duration-300 ${
                      isHovered ? "text-[#0EA5E9] dark:text-[#38BDF8]" : "text-ink"
                    }`}
                  >
                    {step.label}
                  </p>
                  <p className="text-[11.5px] font-sans text-ink-muted/80 mt-1 font-medium leading-tight whitespace-nowrap">
                    {step.desc}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </section>
  );
}
