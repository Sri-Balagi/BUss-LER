"use client";

import React from "react";
import { useOnboarding } from "@/lib/onboarding-context";
import { Sparkles, ArrowRight, ArrowLeft, Lightbulb } from "lucide-react";

interface StepProps {
  onNext: () => void;
  onBack: () => void;
}

const EXAMPLE_TEXT =
  "I run a seafood restaurant with 18 employees. We purchase fish daily, manage reservations, and communicate with customers using WhatsApp.";

export function Step3AiDescription({ onNext, onBack }: StepProps) {
  const { data, updateData } = useOnboarding();

  const handleUseExample = () => {
    updateData({ aiDescription: EXAMPLE_TEXT });
  };

  return (
    <div className="flex flex-col max-w-2xl mx-auto py-2">
      <div className="text-center mb-6">
        <p className="eyebrow mb-2">STEP 3 OF 7 • AI KNOWLEDGE BASE</p>
        <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-primary">
          Describe Your Business
        </h2>
        <p className="mt-1.5 text-xs text-secondary max-w-lg mx-auto">
          Provide context in your own words. BizOS will parse this to configure your cognitive graph and autonomous agents.
        </p>
      </div>

      <div className="flex flex-col gap-4">
        {/* Prompt Card */}
        <div className="glass-panel p-4 rounded-2xl border border-accent/20 bg-accent/5 flex items-start gap-3">
          <Sparkles className="h-5 w-5 text-accent shrink-0 mt-0.5" />
          <div className="text-xs text-secondary leading-relaxed">
            <span className="font-semibold text-primary">How will this be used?</span> This will later be used by the backend AI to configure your Digital Twin, seed initial memory graphs, and auto-assign specialized agents to your operational workflows.
          </div>
        </div>

        {/* Textarea Label & Actions */}
        <div className="flex items-center justify-between mt-2">
          <label className="text-xs font-medium text-secondary">
            Describe your business in your own words
          </label>
          <button
            type="button"
            onClick={handleUseExample}
            className="flex items-center gap-1.5 text-xs text-accent hover:underline font-medium"
          >
            <Lightbulb className="h-3.5 w-3.5" />
            <span>Use example prompt</span>
          </button>
        </div>

        {/* Textarea */}
        <div className="relative">
          <textarea
            rows={6}
            value={data.aiDescription}
            onChange={(e) => updateData({ aiDescription: e.target.value })}
            placeholder="Describe what your company does, your key operational routines, team structure, customer communication channels, and primary workflows..."
            className="w-full rounded-2xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#1C1C1C] p-4 text-sm font-medium text-[#171717] dark:text-white placeholder:text-[#66635F] dark:placeholder:text-gray-400 focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none transition-all leading-relaxed shadow-sm"
          />
          <div className="absolute bottom-3 right-4 font-mono text-[11px] text-[#66635F] dark:text-gray-400">
            {data.aiDescription.length} characters
          </div>
        </div>

        {/* Example Callout */}
        <div className="rounded-xl border border-white/10 bg-white/[0.02] p-3 text-xs text-secondary">
          <span className="font-mono text-[10px] uppercase text-accent tracking-wider block mb-1">
            EXAMPLE INPUT:
          </span>
          <p className="italic text-tertiary">&ldquo;{EXAMPLE_TEXT}&rdquo;</p>
        </div>

        {/* Controls */}
        <div className="mt-6 flex items-center justify-between pt-4 border-t border-white/10">
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
            disabled={!data.aiDescription.trim()}
            className="flex h-11 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover disabled:opacity-50"
          >
            <span>Continue</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
