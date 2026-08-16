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
    <div className="glass-panel col-span-full p-7 lg:col-span-2">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <p className="eyebrow mb-2">Runtime Monitor · live</p>
          <h2 className="font-display text-[19px] font-medium text-ink">
            Where every run is right now
          </h2>
        </div>
        <div className="font-mono text-[11px] text-ink-faint">
          tick {state.tick.toString().padStart(4, "0")}
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-0 right-0 top-[74px] h-px bg-white/[0.08]" />
        {PULSES.map((p, i) => (
          <motion.div
            key={i}
            className="absolute top-[71px] h-1.5 w-1.5 rounded-full"
            style={{
              background: `rgba(${p.color},0.95)`,
              boxShadow: `0 0 10px 2px rgba(${p.color},0.7)`,
            }}
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
                className="group flex flex-col items-center gap-3 rounded-lg py-2 transition-colors"
              >
                <div className="flex h-[56px] items-end">
                  <motion.div
                    animate={{ height: barHeight }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className={`w-1.5 rounded-full ${
                      isSelected
                        ? "bg-core-cyan shadow-glow-cyan"
                        : "bg-white/15 group-hover:bg-white/25"
                    }`}
                  />
                </div>
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full border font-mono text-[12px] transition-colors ${
                    isSelected
                      ? "border-core-cyan/50 bg-core-cyan/10 text-core-cyan"
                      : "border-white/10 bg-panel text-ink-muted group-hover:border-white/20"
                  }`}
                >
                  <AnimatePresence mode="popLayout">
                    <motion.span
                      key={count}
                      initial={{ y: -6, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      exit={{ y: 6, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                    >
                      {count}
                    </motion.span>
                  </AnimatePresence>
                </div>
                <span
                  className={`text-[11.5px] transition-colors ${
                    isSelected ? "text-ink" : "text-ink-muted"
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
          className="mt-6 font-mono text-[11.5px] text-ink-faint"
        >
          Filtering agent fleet to{" "}
          <span className="text-core-cyan">{state.selectedStage}</span> — click the stage again to clear.
        </motion.p>
      )}
    </div>
  );
}
