"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Brain, Globe, PlayCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { MagneticButton } from "@/components/ui/MagneticButton";

const FEATURE_CARDS = [
  {
    icon: Brain,
    title: "Cognitive Runtime",
    description:
      "Watch intelligence move as tasks flow through planner, reasoning and decision engines in real-time.",
  },
  {
    icon: Globe,
    title: "Memory Galaxy",
    description:
      "Navigate semantic neighborhoods in a fully 3D celestial representation of long-term storage.",
  },
  {
    icon: PlayCircle,
    title: "Workflow Playback",
    description:
      "Replay the exact path of reasoning and decision-making for any historical execution.",
  },
];

export function Hero() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const handleInitialize = () => {
    router.push("/login");
  };

  return (
    <section
      id="top"
      className="relative mx-auto max-w-6xl w-full px-4 py-10 sm:py-16 flex flex-col items-center justify-center text-center my-auto"
    >
      {/* Multi-layered soft ambient background glow with gentle floating drift */}
      <motion.div
        animate={{ y: [0, -12, 0], scale: [1, 1.03, 1] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-[25%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-[540px] h-[540px] rounded-full bg-accent/[0.05] blur-[140px] pointer-events-none -z-10"
      />
      <motion.div
        animate={{ y: [0, 10, 0], scale: [1, 1.04, 1] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        className="absolute top-[35%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-[340px] h-[340px] rounded-full bg-[#38BDF8]/[0.05] blur-[100px] pointer-events-none -z-10"
      />

      {/* Headline */}
      <motion.h1
        initial={{ opacity: 0, y: 25 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
        className="font-display text-[44px] sm:text-[72px] lg:text-[88px] font-semibold leading-[1.06] tracking-tight text-ink max-w-4xl"
      >
        The Operating System
        <br />
        <span className="text-ink-muted font-light">for Intelligence</span>
      </motion.h1>

      {/* Subheading */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1], delay: 0.25 }}
        className="mx-auto mt-7 max-w-2xl text-[17px] sm:text-[20px] leading-relaxed text-ink-muted font-light"
      >
        Not another dashboard. A living, breathing cognitive space where memory,
        knowledge, and reasoning converge into a single unified runtime.
      </motion.p>

      {/* CTA Button with Magnetic physics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1], delay: 0.38 }}
        className="mt-9 sm:mt-11 flex justify-center"
      >
        <MagneticButton
          id="initialize-sequence-btn"
          onClick={handleInitialize}
          disabled={isLoading}
          className="group flex items-center gap-2.5 rounded-full bg-accent hover:bg-accent-hover px-9 py-4 text-[15px] font-semibold text-white transition-all duration-300 hover:scale-[1.04] active:scale-[0.98] hover:-translate-y-0.5 shadow-[0_6px_24px_rgba(232,123,42,0.2)] hover:shadow-[0_14px_36px_rgba(232,123,42,0.35)] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          Initialize Sequence
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </MagneticButton>
      </motion.div>

      {/* Feature Cards with subtle floating drift & staggered entrance */}
      <div className="mt-16 sm:mt-24 grid gap-8 sm:grid-cols-3 max-w-5xl w-full">
        {FEATURE_CARDS.map((card, i) => {
          const Icon = card.icon;
          const isFocused = hoveredIndex === i;
          const isBlurred = hoveredIndex !== null && !isFocused;

          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              transition={{
                duration: 0.7,
                ease: [0.16, 1, 0.3, 1],
                delay: 0.45 + i * 0.1,
              }}
              className="w-full"
            >
              <motion.div
                animate={isFocused ? { y: 0 } : { y: [0, -4, 0] }}
                transition={
                  isFocused
                    ? { duration: 0.2 }
                    : { duration: 5 + i * 0.8, repeat: Infinity, ease: "easeInOut", delay: i * 0.6 }
                }
                className={`glass-panel p-8 md:p-9 text-left transition-all duration-300 ease-out group/card cursor-default flex flex-col justify-between rounded-[28px] border-2 h-full ${
                  isFocused
                    ? "!border-[#38BDF8] !bg-[#F0F9FF] dark:!bg-[#0F172A] !shadow-[0_16px_36px_rgba(0,0,0,0.08)] -translate-y-1 scale-[1.01] z-10"
                    : isBlurred
                    ? "border-[color:var(--border-color)] bg-[#F5F1E8]/70 dark:bg-zinc-900/70 opacity-40 blur-[1.5px] scale-[0.98]"
                    : "border-[color:var(--border-color)] bg-[#FAF7F2] dark:bg-zinc-900 shadow-[0_4px_24px_rgba(23,23,23,0.03)] hover:shadow-[0_16px_36px_rgba(0,0,0,0.08)] hover:border-[#38BDF8] hover:bg-[#F0F9FF] hover:-translate-y-1"
                }`}
              >
                <div>
                  <div className={`mb-6 flex h-11 w-11 items-center justify-center rounded-2xl border-2 transition-all duration-300 ${
                    isFocused
                      ? "text-[#0EA5E9] border-[#38BDF8] bg-[#E0F2FE]"
                      : "border-[color:var(--border-color)] bg-[#EBE4D8] dark:bg-zinc-800 text-ink-muted group-hover/card:text-[#0EA5E9] group-hover/card:border-[#38BDF8] group-hover/card:bg-[#E0F2FE]"
                  }`}>
                    <Icon className="h-5 w-5" strokeWidth={1.5} />
                  </div>
                  <h3 className="mb-3 text-[17px] font-semibold text-ink tracking-tight">
                    {card.title}
                  </h3>
                  <p className="text-[14px] leading-relaxed text-ink-muted font-light">
                    {card.description}
                  </p>
                </div>
              </motion.div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
