"use client";

import { motion, AnimatePresence } from "framer-motion";
import { STAGES, useCognitiveState, useCognitiveActions } from "@/lib/dashboard/state";

const PULSES = [
  { color: "76,224,224", duration: 4.4, delay: 0 },
  { color: "47,111,255", duration: 5.2, delay: 1.1 },
  { color: "139,92,246", duration: 4.8, delay: 2.3 },
];

export default function RuntimeOverview() {
  const state = useCognitiveState();
  const { selectStage } = useCognitiveActions();
  const max = Math.max(...Object.values(state.stageCounts), 1);

  return (
    <div className="glass-card col-span-1 md:col-span-2 lg:col-span-2 p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <p className="eyebrow mb-2 text-accent">Runtime Monitor · live</p>
          <h2 className="font-display text-[20px] font-semibold text-ink tracking-tight">
            Where every run is right now
          </h2>
        </div>
        <div className="font-mono text-[11px] font-semibold text-ink-muted px-3 py-1 rounded-full border border-[#E2DAD0] dark:border-zinc-700 bg-white/80 dark:bg-zinc-800 shadow-sm">
          tick {state.tick.toString().padStart(4, "0")}
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-0 right-0 top-[74px] h-px bg-[#E2DAD0] dark:bg-zinc-800" />
        {PULSES.map((p, i) => (
          <motion.div
            key={i}
            className="absolute top-[71px] h-1.5 w-1.5 rounded-full bg-accent"
            animate={{ left: ["0%", "100%"] }}
            transition={{ duration: p.duration, delay: p.delay, repeat: Infinity, ease: "linear" }}
          />
        ))}

        <div className="grid grid-cols-4 gap-3 sm:grid-cols-7">
          {STAGES.map((stage) => {
            const count = state.stageCounts[stage.key];
            const isSelected = state.selectedStage === stage.key;
            const barHeight = 8 + (count / max) * 44;
            return (
              <button
                key={stage.key}
                onClick={() => selectStage(isSelected ? null : stage.key)}
                className="group flex flex-col items-center gap-3 rounded-2xl py-2 transition-all duration-200 ease-[0.16,1,0.3,1] hover:scale-105 cursor-pointer"
              >
                <div className="flex h-[56px] items-end">
                  <motion.div
                    animate={{ height: barHeight }}
                    transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                    className={`w-2.5 rounded-full transition-colors ${
                      isSelected
                        ? "bg-[#0EA5E9] dark:bg-[#38BDF8]"
                        : "bg-[#E2DAD0] dark:bg-zinc-700 group-hover:bg-[#38BDF8]"
                    }`}
                  />
                </div>
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full border font-mono text-[12px] transition-all duration-200 ${
                    isSelected
                      ? "border-[#38BDF8] bg-[#F0F9FF] dark:bg-[#0F172A] text-[#0EA5E9] dark:text-[#38BDF8] font-bold shadow-sm"
                      : "border-[#E2DAD0] dark:border-zinc-800 bg-white/90 dark:bg-zinc-800 text-ink-muted group-hover:border-[#38BDF8] group-hover:text-[#0EA5E9]"
                  }`}
                >
                  <AnimatePresence mode="popLayout">
                    <motion.span
                      key={count}
                      initial={{ y: -6, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      exit={{ y: 6, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      {count}
                    </motion.span>
                  </AnimatePresence>
                </div>
                <span
                  className={`text-[11.5px] font-medium transition-colors ${
                    isSelected ? "text-ink font-semibold" : "text-ink-muted group-hover:text-ink"
                  }`}
                >
                  {stage.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {state.selectedStage && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 font-mono text-[11.5px] text-ink-muted font-medium"
        >
          Filtering agent fleet to{" "}
          <span className="text-[#0EA5E9] dark:text-[#38BDF8] font-semibold">{state.selectedStage}</span> — click the stage again to clear.
        </motion.p>
      )}
    </div>
  );
}
