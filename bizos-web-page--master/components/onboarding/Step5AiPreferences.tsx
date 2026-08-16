"use client";

import React from "react";
import { useOnboarding } from "@/lib/onboarding-context";
import { Bot, Cpu, Zap, MessageSquare, ArrowRight, ArrowLeft, Check } from "lucide-react";

interface StepProps {
  onNext: () => void;
  onBack: () => void;
}

const AI_MODES = [
  {
    id: "assistant",
    name: "AI Assistant",
    desc: "Provides suggestions and drafts actions for your approval. Best for cautious oversight.",
    icon: Bot,
    badge: null,
  },
  {
    id: "copilot",
    name: "AI Copilot",
    desc: "Collaborates alongside your team in real time, auto-completing routine workflows.",
    icon: Cpu,
    badge: "Recommended",
  },
  {
    id: "autonomous",
    name: "Autonomous Mode",
    desc: "Full self-driving AI runtime executing actions independently based on company policies.",
    icon: Zap,
    badge: "Coming Soon",
  },
] as const;

const STYLES = [
  {
    id: "professional",
    name: "Professional",
    desc: "Formal, concise, and executive-ready communications.",
  },
  {
    id: "friendly",
    name: "Friendly",
    desc: "Warm, empathetic, and conversational tone.",
  },
  {
    id: "technical",
    name: "Technical",
    desc: "Data-dense, precise, and engineering-oriented logs.",
  },
] as const;

export function Step5AiPreferences({ onNext, onBack }: StepProps) {
  const { data, updateData } = useOnboarding();

  return (
    <div className="flex flex-col max-w-2xl mx-auto py-2">
      <div className="text-center mb-6">
        <p className="eyebrow mb-2">STEP 5 OF 7 • AI BEHAVIOR</p>
        <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-primary">
          AI Operating Preferences
        </h2>
        <p className="mt-1.5 text-xs text-secondary max-w-lg mx-auto">
          Configure how BizOS agents interact with your team and handle operational decisions.
        </p>
      </div>

      <div className="flex flex-col gap-6">
        {/* AI Operating Mode */}
        <div>
          <label className="text-xs font-mono uppercase tracking-wider text-tertiary block mb-3">
            1. Select AI Operating Mode
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {AI_MODES.map((mode) => {
              const Icon = mode.icon;
              const isSelected = data.aiPreferenceMode === mode.id;
              const isComingSoon = mode.badge === "Coming Soon";

              return (
                <div
                  key={mode.id}
                  onClick={() => {
                    if (!isComingSoon) {
                      updateData({ aiPreferenceMode: mode.id as any });
                    }
                  }}
                  className={`relative flex flex-col p-4 rounded-2xl border transition-all duration-300 ${
                    isComingSoon
                      ? "opacity-60 cursor-not-allowed border-white/5 bg-white/[0.01]"
                      : isSelected
                      ? "border-accent/40 bg-accent/[0.08] shadow-lg cursor-pointer"
                      : "border-white/10 bg-white/[0.03] hover:border-white/20 cursor-pointer"
                  }`}
                >
                  {mode.badge && (
                    <span
                      className={`absolute top-3 right-3 rounded-full px-2 py-0.5 text-[9px] font-mono tracking-wider ${
                        mode.badge === "Recommended"
                          ? "bg-accent/20 text-accent border border-accent/30"
                          : "bg-white/10 text-tertiary border border-white/10"
                      }`}
                    >
                      {mode.badge}
                    </span>
                  )}

                  <div
                    className={`flex h-9 w-9 items-center justify-center rounded-xl mb-3 ${
                      isSelected ? "bg-accent text-white" : "bg-white/10 text-secondary"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </div>

                  <h3 className="text-sm font-medium text-primary flex items-center justify-between">
                    {mode.name}
                  </h3>
                  <p className="mt-1.5 text-[11px] text-secondary leading-snug">{mode.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Communication Style */}
        <div>
          <label className="text-xs font-mono uppercase tracking-wider text-tertiary block mb-3">
            2. Choose AI Communication Style
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {STYLES.map((st) => {
              const isSelected = data.communicationStyle === st.id;

              return (
                <div
                  key={st.id}
                  onClick={() => updateData({ communicationStyle: st.id as any })}
                  className={`flex flex-col p-4 rounded-2xl border cursor-pointer transition-all duration-300 ${
                    isSelected
                      ? "border-accent/40 bg-accent/[0.08] shadow-lg"
                      : "border-white/10 bg-white/[0.03] hover:border-white/20"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <MessageSquare
                      className={`h-4 w-4 ${isSelected ? "text-accent" : "text-tertiary"}`}
                    />
                    {isSelected && (
                      <div className="flex h-4 w-4 items-center justify-center rounded-full bg-accent text-white">
                        <Check className="h-2.5 w-2.5 stroke-[3]" />
                      </div>
                    )}
                  </div>
                  <h3 className="text-sm font-medium text-primary">{st.name}</h3>
                  <p className="mt-1 text-[11px] text-secondary leading-snug">{st.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Controls */}
        <div className="mt-4 flex items-center justify-between pt-4 border-t border-white/10">
          <button
            type="button"
            onClick={onBack}
            className="flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-5 text-sm font-medium text-primary hover:bg-white/[0.08] transition-all"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back</span>
          </button>

          <button
            type="button"
            onClick={onNext}
            className="flex h-11 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover"
          >
            <span>Continue</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
