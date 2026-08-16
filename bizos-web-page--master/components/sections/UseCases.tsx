"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Coffee, ShoppingBag, Stethoscope, Factory, GraduationCap, Building2 } from "lucide-react";

const USE_CASES = [
  {
    id: "restaurant",
    icon: Coffee,
    title: "Restaurant",
    scenario: "Instead of just tracking inventory, BizOS notices a weather pattern shift, checks local event schedules, predicts a 40% spike in foot traffic this weekend, automatically orders extra ingredients from preferred suppliers, and drafts a staff scheduling recommendation for approval.",
  },
  {
    id: "retail",
    icon: ShoppingBag,
    title: "Retail",
    scenario: "BizOS remembers a specific customer cohort's return reasons from last quarter. When a new product line with similar material specs arrives, it automatically flags the risk to quality control and pre-drafts targeted customer support guidelines before issues arise.",
  },
  {
    id: "healthcare",
    icon: Stethoscope,
    title: "Healthcare",
    scenario: "Not a passive medical record database. BizOS cross-references a patient's new prescription against their entire historical symptom timeline and recent lab anomalies, alerting the physician to a subtle contraindication that standard rule-based systems missed.",
  },
  {
    id: "manufacturing",
    icon: Factory,
    title: "Manufacturing",
    scenario: "BizOS continuously monitors sensor telemetry across the supply chain. When it detects a micro-vibration anomaly in a core machine, it doesn't just alert maintenance; it checks part availability, reschedules the production queue to minimize downtime, and orders the replacement part.",
  },
  {
    id: "education",
    icon: GraduationCap,
    title: "Education",
    scenario: "BizOS tracks learning progression. When it notices a student struggling with calculus concepts, it references their past success with visual learning methods and automatically dynamically generates a visually-driven supplementary curriculum tailored specifically to them.",
  },
  {
    id: "enterprise",
    icon: Building2,
    title: "Enterprise",
    scenario: "When legal updates a compliance policy, BizOS doesn't just send a memo. It autonomously audits the entire codebase, flags non-compliant functions, drafts the necessary code patches, and submits them to engineering review with the specific legal context attached.",
  },
];

export function UseCases() {
  const [activeId, setActiveId] = useState(USE_CASES[0].id);

  const activeCase = USE_CASES.find((uc) => uc.id === activeId)!;

  return (
    <section className="relative mx-auto max-w-6xl px-6 py-28 border-t border-white/[0.04]">
      <div className="mb-16 text-center">
        <p className="eyebrow mb-4">Domains of Intelligence</p>
        <h2 className="font-display text-[32px] md:text-[40px] font-medium leading-tight text-ink">
          How BizOS thinks in reality.
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.5fr] gap-8">
        <div className="flex flex-col gap-3">
          {USE_CASES.map((uc) => {
            const isActive = activeId === uc.id;
            return (
              <button
                key={uc.id}
                onClick={() => setActiveId(uc.id)}
                className={`group relative flex items-center gap-4 rounded-2xl p-5 text-left transition-all duration-300 ${
                  isActive
                    ? "bg-white/[0.08] border border-white/[0.12] shadow-lg"
                    : "hover:bg-white/[0.04] border border-transparent"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-use-case"
                    className="absolute inset-0 rounded-2xl border border-accent/30 bg-accent/[0.03]"
                    initial={false}
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <div className={`relative z-10 flex h-10 w-10 items-center justify-center rounded-full transition-colors duration-300 ${isActive ? "bg-accent/20 text-accent" : "bg-white/[0.05] text-ink-muted group-hover:text-ink"}`}>
                  <uc.icon className="h-4 w-4" />
                </div>
                <span className={`relative z-10 font-display text-[16px] font-medium transition-colors duration-300 ${isActive ? "text-ink" : "text-ink-muted group-hover:text-ink"}`}>
                  {uc.title}
                </span>
              </button>
            );
          })}
        </div>

        <div className="glass-panel p-8 md:p-12 relative overflow-hidden flex flex-col justify-center min-h-[300px]">
          <div className="absolute inset-0 bg-gradient-to-br from-transparent to-accent/5 pointer-events-none" />
          
          <AnimatePresence mode="wait">
            <motion.div
              key={activeId}
              initial={{ opacity: 0, y: 10, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -10, filter: "blur(4px)" }}
              transition={{ duration: 0.4 }}
              className="relative z-10"
            >
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-accent/20 bg-accent/5 mb-6">
                <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse-slow" />
                <span className="text-[10px] font-mono tracking-widest text-accent uppercase">
                  {activeCase.title} Scenario
                </span>
              </div>
              <p className="text-[18px] md:text-[22px] leading-relaxed text-ink font-light">
                {activeCase.scenario}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
