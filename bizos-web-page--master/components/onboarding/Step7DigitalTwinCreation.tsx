"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useOnboarding } from "@/lib/onboarding-context";
import { CheckCircle2, Sparkles, Cpu, Layers, Brain, Database, Zap } from "lucide-react";

const ONBOARDING_STORAGE_KEY = "bizos_onboarding_data";

interface StepProps {
  onComplete: () => void;
}

const STAGES = [
  { id: 1, text: "Creating your Digital Twin...", icon: Brain, duration: 1200 },
  { id: 2, text: "Building Knowledge Graph...", icon: Database, duration: 1400 },
  { id: 3, text: "Initializing Memory Platform...", icon: Layers, duration: 1300 },
  { id: 4, text: "Configuring Autonomous AI Agents...", icon: Cpu, duration: 1500 },
  { id: 5, text: "Preparing Operational Dashboard...", icon: Zap, duration: 1200 },
  { id: 6, text: "Almost Ready...", icon: Sparkles, duration: 1000 },
];

export function Step7DigitalTwinCreation({ onComplete }: StepProps) {
  const { data, completeOnboarding } = useOnboarding();
  const [currentStageIdx, setCurrentStageIdx] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    let timeout: NodeJS.Timeout;

    if (currentStageIdx < STAGES.length) {
      const stage = STAGES[currentStageIdx];
      const targetProgress = Math.round(((currentStageIdx + 1) / STAGES.length) * 100);

      timeout = setTimeout(() => {
        setProgress(targetProgress);
        if (currentStageIdx + 1 < STAGES.length) {
          setCurrentStageIdx((prev) => prev + 1);
        } else {
          // All stages complete — show 100% state
          setIsFinished(true);

          // Synchronously write completion to localStorage BEFORE any navigation
          try {
            const existing = localStorage.getItem(ONBOARDING_STORAGE_KEY);
            const parsed = existing ? JSON.parse(existing) : {};
            const completed = {
              ...parsed,
              completed: true,
              completedAt: new Date().toISOString(),
            };
            localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(completed));

            // Also update React context state
            completeOnboarding();

            // Wait 1.5s so user sees the 100% completion state, then navigate
            setTimeout(() => {
              onComplete();
            }, 1500);
          } catch (e) {
            console.error("Failed to persist onboarding completion", e);
            setSaveError("Failed to save your setup. Please try again.");
          }
        }
      }, stage.duration);
    }

    return () => clearTimeout(timeout);
  }, [currentStageIdx, completeOnboarding, onComplete]);

  const activeStage = STAGES[currentStageIdx];
  const StageIcon = activeStage?.icon || Sparkles;

  return (
    <div className="flex flex-col items-center justify-center text-center max-w-xl mx-auto py-8">
      {/* Central Visualizer */}
      <div className="relative flex items-center justify-center mb-10">
        {/* Pulsing Core Aura */}
        <motion.div
          animate={{ scale: [1, 1.25, 1], opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          className="absolute h-64 w-64 rounded-full bg-gradient-to-r from-accent via-[#00F0FF] to-purple-500 blur-[80px] opacity-40"
        />

        {/* Outer Orbit Ring */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
          className="h-44 w-44 rounded-full border border-dashed border-accent/40 flex items-center justify-center p-2"
        >
          {/* Inner Glowing Ring */}
          <div className="h-full w-full rounded-full border border-white/10 bg-white/[0.02] backdrop-blur-2xl flex items-center justify-center relative">
            <StageIcon className="h-14 w-14 text-accent animate-pulse" />
          </div>
        </motion.div>

        {/* Progress Percentage Badge */}
        <div className="absolute -bottom-3 rounded-full bg-accent px-3 py-1 font-mono text-xs font-bold text-white shadow-lg shadow-accent/30">
          {progress}%
        </div>
      </div>

      {/* Title */}
      <p className="eyebrow mb-2">FINAL STEP • COGNITIVE INITIALIZATION</p>
      <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-primary">
        Synthesizing Digital Twin
      </h2>
      <p className="mt-1.5 text-xs text-secondary">
        Configuring BizOS runtime for <strong className="text-primary">{data.businessName}</strong>
      </p>

      {/* Progress Bar */}
      <div className="w-full max-w-md bg-white/10 h-2 rounded-full overflow-hidden my-6 p-0.5 border border-white/5">
        <motion.div
          className="h-full bg-gradient-to-r from-accent via-[#00F0FF] to-emerald-400 rounded-full"
          initial={{ width: "0%" }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>

      {/* Stage Log List */}
      <div className="w-full max-w-md flex flex-col gap-2 bg-white/[0.02] border border-white/10 rounded-2xl p-4 text-left font-mono text-xs">
        {STAGES.map((s, idx) => {
          const isDone = idx < currentStageIdx || isFinished;
          const isCurrent = idx === currentStageIdx && !isFinished;

          return (
            <div
              key={s.id}
              className={`flex items-center justify-between transition-colors py-1 ${
                isDone
                  ? "text-emerald-400"
                  : isCurrent
                  ? "text-accent font-semibold"
                  : "text-tertiary opacity-40"
              }`}
            >
              <div className="flex items-center gap-2.5">
                {isDone ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                ) : isCurrent ? (
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
                    <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-accent" />
                  </span>
                ) : (
                  <div className="h-2 w-2 rounded-full bg-white/20 ml-0.5" />
                )}
                <span>{s.text}</span>
              </div>
              <span className="text-[10px] uppercase opacity-70">
                {isDone ? "COMPLETE" : isCurrent ? "RUNNING" : "QUEUED"}
              </span>
            </div>
          );
        })}
      </div>

      {/* Completion Banner */}
      <AnimatePresence>
        {isFinished && !saveError && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="mt-6 flex items-center gap-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-5 py-3 text-sm text-emerald-400 font-medium"
          >
            <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-400" />
            <span>✓ Digital Twin Created — Redirecting to Dashboard...</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Banner */}
      <AnimatePresence>
        {saveError && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 flex flex-col items-center gap-3 rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400"
          >
            <p>{saveError}</p>
            <button
              onClick={() => {
                setSaveError(null);
                try {
                  const existing = localStorage.getItem(ONBOARDING_STORAGE_KEY);
                  const parsed = existing ? JSON.parse(existing) : {};
                  localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify({
                    ...parsed,
                    completed: true,
                    completedAt: new Date().toISOString(),
                  }));
                  completeOnboarding();
                  setTimeout(() => onComplete(), 500);
                } catch (e) {
                  setSaveError("Still unable to save. Please refresh and try again.");
                }
              }}
              className="rounded-xl border border-red-500/40 px-4 py-1.5 text-xs font-medium text-red-400 hover:bg-red-500/10 transition-colors"
            >
              Retry
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
