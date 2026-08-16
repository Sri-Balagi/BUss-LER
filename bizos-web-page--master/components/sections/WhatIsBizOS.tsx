"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Database, Library, BrainCircuit, Workflow, GitBranch, Zap } from "lucide-react";

const STAGES = [
  { label: "Memory", icon: Database, desc: "Persistent long-term business memory." },
  { label: "Knowledge", icon: Library, desc: "Structured semantic understanding." },
  { label: "Reasoning", icon: BrainCircuit, desc: "Analyzes information and generates decisions." },
  { label: "Planning", icon: Workflow, desc: "Creates intelligent execution plans." },
  { label: "Decision", icon: GitBranch, desc: "Evaluates options using business context." },
  { label: "Execution", icon: Zap, desc: "Transforms decisions into actions." },
];

export function WhatIsBizOS() {
  const [activeStage, setActiveStage] = useState(0);
  const [hoveredStage, setHoveredStage] = useState<number | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % STAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative w-full border-t border-[color:var(--border-color)]">
      <div className="mx-auto max-w-6xl px-6 py-24 md:py-36 grid grid-cols-1 lg:grid-cols-12 gap-16 lg:gap-20 items-center">
        
        {/* Visual: Vertical Flow (Visual Left) */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="lg:col-span-5 flex justify-center w-full order-2 lg:order-1"
        >
          <div className="relative w-full max-w-[380px] p-8 md:p-9 glass-panel rounded-[28px] bg-white dark:bg-zinc-900 border-2 border-[color:var(--border-color)] shadow-[0_6px_28px_rgba(23,23,23,0.03)] hover:shadow-[0_16px_36px_rgba(0,0,0,0.08)] hover:border-[#38BDF8] hover:-translate-y-1 transition-all duration-300 ease-out flex flex-col items-center">
            
            {/* Background Grid Accent */}
            <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.015] mix-blend-overlay pointer-events-none" />

            {/* Connecting Vertical Track */}
            <div className="absolute top-[56px] bottom-[56px] w-px bg-[color:var(--border-color)] left-1/2 -translate-x-1/2" />

            {/* Glowing signal flow */}
            <motion.div
              className="absolute w-[2px] bg-gradient-to-b from-transparent via-accent to-transparent left-1/2 -translate-x-1/2"
              style={{ height: "70px", top: "56px" }}
              animate={{
                top: [`${56 + (activeStage === 0 ? 0 : activeStage - 1) * 72}px`, `${56 + activeStage * 72}px`],
                opacity: [0, 1, 0]
              }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            />

            <div className="relative z-10 flex flex-col gap-7 w-full">
              {STAGES.map((stage, i) => {
                const isActive = i === activeStage;
                const isHovered = hoveredStage === i;
                const isBlurred = hoveredStage !== null && !isHovered;
                const Icon = stage.icon;

                return (
                  <motion.div
                    key={stage.label}
                    initial={{ opacity: 0, y: 15 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.35 + i * 0.08, ease: [0.16, 1, 0.3, 1] }}
                    className={`flex items-center gap-5 group cursor-pointer transition-all duration-300 ${
                      isBlurred ? "opacity-35 blur-[1.5px]" : "opacity-100"
                    }`}
                    onClick={() => setActiveStage(i)}
                    onMouseEnter={() => setHoveredStage(i)}
                    onMouseLeave={() => setHoveredStage(null)}
                  >
                    {/* The Node */}
                    <motion.div
                      animate={{ scale: isActive || isHovered ? 1.1 : 1 }}
                      className={`relative z-10 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border-2 transition-all duration-300 ${
                        isActive
                          ? "border-accent bg-accent/[0.04] text-accent shadow-[0_0_18px_rgba(232,123,42,0.18)]"
                          : isHovered
                          ? "border-[#38BDF8] text-[#0EA5E9] bg-[#E0F2FE] shadow-[0_4px_16px_rgba(0,0,0,0.05)]"
                          : "border-[color:var(--border-color)] bg-white dark:bg-zinc-900 text-ink-muted"
                      }`}
                    >
                      <Icon className="h-5 w-5" strokeWidth={1.5} />
                    </motion.div>
                    
                    {/* The Text Label */}
                    <div className="text-left">
                      <span className={`font-display text-[14px] font-semibold transition-colors duration-300 ${
                        isActive ? "text-accent" : isHovered ? "text-[#0EA5E9]" : "text-ink"
                      }`}>
                        {stage.label}
                      </span>
                      <p className="text-[11px] text-ink-muted font-light mt-0.5">
                        {stage.desc}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Content (Text Right) */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
          className="lg:col-span-7 text-left order-1 lg:order-2"
        >
          <p className="eyebrow mb-6">The Solution</p>
          <h2 className="font-display text-[42px] md:text-[56px] font-semibold leading-[1.1] tracking-tight text-ink mb-6">
            BizOS is an Artificial Intelligence Operating System.
          </h2>
          <p className="text-[16px] md:text-[18px] leading-relaxed text-ink-muted font-light">
            It continuously understands your business through memory, knowledge, reasoning, and execution. One unified cognitive environment. Not isolated applications.
          </p>
        </motion.div>

      </div>
    </section>
  );
}
