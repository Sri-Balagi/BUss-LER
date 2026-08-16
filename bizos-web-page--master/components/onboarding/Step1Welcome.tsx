"use client";

import React from "react";
import { motion } from "framer-motion";
import { Sparkles, Cpu, Layers, Brain, ArrowRight } from "lucide-react";

interface StepProps {
  onNext: () => void;
}

export function Step1Welcome({ onNext }: StepProps) {
  return (
    <div className="flex flex-col items-center text-center max-w-2xl mx-auto py-4">
      {/* Animated Icon Header */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="relative mb-8"
      >
        <div className="absolute inset-0 rounded-full bg-accent/20 blur-2xl animate-pulse-slow" />
        <div className="relative flex h-24 w-24 items-center justify-center rounded-3xl border border-accent/30 bg-accent/10 text-accent shadow-2xl backdrop-blur-xl">
          <Brain className="h-12 w-12" />
        </div>
      </motion.div>

      {/* Main Title & Subtitle */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <p className="eyebrow mb-3">STEP 1 OF 7 • INTRODUCTION</p>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight text-primary">
          Welcome to BizOS
        </h1>
        <p className="mt-4 text-base text-secondary leading-relaxed max-w-xl">
          BizOS creates an autonomous <span className="text-primary font-medium">Digital Twin</span> of your business — an AI cognitive layer that understands your workflows, orchestrates memory, manages knowledge, and executes tasks in real time.
        </p>
      </motion.div>

      {/* Features Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full text-left"
      >
        <div className="glass-panel p-4 rounded-2xl border border-white/10 bg-white/[0.03]">
          <Cpu className="h-6 w-6 text-accent mb-2" />
          <h3 className="text-sm font-medium text-primary">Cognitive Agents</h3>
          <p className="mt-1 text-xs text-secondary">Autonomous worker agents trained on your specific business context.</p>
        </div>

        <div className="glass-panel p-4 rounded-2xl border border-white/10 bg-white/[0.03]">
          <Brain className="h-6 w-6 text-[#00F0FF] mb-2" />
          <h3 className="text-sm font-medium text-primary">Memory &amp; Knowledge</h3>
          <p className="mt-1 text-xs text-secondary">Dynamic vector graph capturing every document, policy, and transaction.</p>
        </div>

        <div className="glass-panel p-4 rounded-2xl border border-white/10 bg-white/[0.03]">
          <Layers className="h-6 w-6 text-emerald-400 mb-2" />
          <h3 className="text-sm font-medium text-primary">Unified Execution</h3>
          <p className="mt-1 text-xs text-secondary">Seamlessly connects with your existing tools and APIs.</p>
        </div>
      </motion.div>

      {/* Next Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-10 w-full flex justify-center"
      >
        <button
          type="button"
          onClick={onNext}
          className="group flex h-12 items-center gap-2.5 rounded-full bg-accent px-8 text-sm font-medium text-white shadow-xl shadow-accent/25 transition-all hover:bg-accent-hover active:scale-[0.98]"
        >
          <span>Begin Setup</span>
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </button>
      </motion.div>
    </div>
  );
}
