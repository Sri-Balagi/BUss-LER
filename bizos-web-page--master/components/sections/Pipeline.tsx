"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { MessageSquare, Brain, Database, Workflow, GitBranch, Zap } from "lucide-react";

const PIPELINE_STAGES = [
  {
    id: "intent",
    icon: MessageSquare,
    label: "Intent",
    desc: "Captures natural language requests, business goals, and trigger events into structured operational targets.",
  },
  {
    id: "memory",
    icon: Database,
    label: "Memory",
    desc: "Queries long-term business memory to retrieve relevant past interactions, domain context, and historical outcomes.",
  },
  {
    id: "reasoning",
    icon: Brain,
    label: "Reasoning",
    desc: "Evaluates business policies, operational constraints, and live context to synthesize optimal action strategies.",
  },
  {
    id: "planning",
    icon: Workflow,
    label: "Planning",
    desc: "Decomposes complex goals into multi-step execution workflows assigned to specialized autonomous agents.",
  },
  {
    id: "decision",
    icon: GitBranch,
    label: "Decision",
    desc: "Scores proposed execution paths against confidence thresholds, escalating to human review when required.",
  },
  {
    id: "execution",
    icon: Zap,
    label: "Execution",
    desc: "Performs automated actions across connected software systems and commits complete audit logs to system memory.",
  },
];

export function Pipeline() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((current) => (current + 1) % PIPELINE_STAGES.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full max-w-4xl px-4 py-4 sm:py-6 mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 25 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
        className="mb-12 md:mb-16 text-center"
      >
        <p className="eyebrow mb-3">Cognitive Pipeline</p>
        <h2 className="font-display text-[38px] md:text-[52px] font-semibold leading-tight text-ink">
          How it works.
        </h2>
      </motion.div>

      <div className="relative py-6">
        {/* The Track */}
        <div className="absolute left-[39px] md:left-1/2 top-0 bottom-0 w-px bg-[color:var(--border-color)] -translate-x-1/2" />
        
        {/* The Signal Line */}
        <motion.div
          className="absolute left-[39px] md:left-1/2 top-0 bottom-0 w-[3px] bg-gradient-to-b from-transparent via-[#38BDF8] to-accent -translate-x-1/2 origin-top rounded-full"
          animate={{ scaleY: PIPELINE_STAGES.length > 1 ? activeIndex / (PIPELINE_STAGES.length - 1) : 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        />

        <div className="relative z-10 flex flex-col gap-14 md:gap-16">
          {PIPELINE_STAGES.map((stage, i) => {
            const isActive = i === activeIndex;
            const isCompleted = i < activeIndex;
            const isHovered = hoveredIndex === i;
            const isBlurred = hoveredIndex !== null && !isHovered;

            return (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 28 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.7, delay: i * 0.09, ease: [0.16, 1, 0.3, 1] }}
                onClick={() => setActiveIndex(i)}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
                className={`relative flex flex-row md:flex-row items-center gap-8 md:gap-12 md:even:flex-row-reverse group cursor-pointer transition-all duration-300 ${
                  isBlurred ? "opacity-35 blur-[1.5px]" : "opacity-100"
                }`}
              >
                {/* Desktop layout spacers */}
                <div className="hidden md:block flex-1 text-right md:group-even:text-left" />

                {/* The Node */}
                <div className={`relative shrink-0 flex h-[76px] w-[76px] items-center justify-center rounded-[20px] glass-panel bg-white dark:bg-zinc-900 border-2 transition-all duration-300 ${
                  isHovered || isActive
                    ? "border-[#38BDF8] shadow-[0_8px_24px_rgba(0,0,0,0.06)] scale-105 z-10"
                    : "border-[color:var(--border-color)] shadow-[0_2px_8px_rgba(23,23,23,0.02)]"
                }`}>
                  <motion.div 
                    className="absolute inset-0 rounded-[18px] bg-[#38BDF8]/[0.06] border border-[#38BDF8]/30"
                    animate={{ opacity: isActive || isHovered ? 1 : isCompleted ? 0.4 : 0 }}
                    transition={{ duration: 0.4 }}
                  />
                  <motion.div
                    animate={{ scale: isActive || isHovered ? 1.1 : 1 }}
                    transition={{ duration: 0.4, type: "spring", stiffness: 300, damping: 20 }}
                    className="relative z-10"
                  >
                    <stage.icon className={`h-6.5 w-6.5 transition-colors duration-300 ${isActive || isHovered ? "text-[#0EA5E9]" : isCompleted ? "text-ink" : "text-ink-muted"}`} strokeWidth={1.5} />
                  </motion.div>
                </div>

                {/* The Content */}
                <div className="flex-1 text-left md:group-even:text-right">
                  <motion.div
                    animate={{ 
                      opacity: isActive || isHovered ? 1 : isCompleted ? 0.7 : 0.25, 
                      y: isActive || isHovered ? 0 : 4 
                    }}
                    transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                  >
                    <span className={`font-mono text-[11px] font-semibold tracking-widest uppercase mb-1.5 block transition-colors duration-300 ${isActive || isHovered ? "text-[#0EA5E9]" : "text-ink-faint"}`}>
                      Stage 0{i + 1}
                    </span>
                    <h3 className={`font-display text-[22px] md:text-[24px] font-semibold mb-1.5 transition-colors duration-300 ${isActive || isHovered ? "text-[#0EA5E9]" : "text-ink"}`}>
                      {stage.label}
                    </h3>
                    <p className="text-[14.5px] leading-relaxed text-ink-muted font-light">
                      {stage.desc}
                    </p>
                  </motion.div>
                </div>

              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
