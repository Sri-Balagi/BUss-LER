"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, ShieldCheck, Zap } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center p-4 md:p-8">
      {/* Background glow ambient elements */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[450px] w-[450px] rounded-full bg-accent/15 blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 h-[350px] w-[350px] rounded-full bg-[#00F0FF]/10 blur-[100px]" />
      </div>

      {/* Header logo */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 mb-8 flex items-center gap-3"
      >
        <Link href="/" className="flex items-center gap-2.5 group">
          <span className="relative flex h-3 w-3">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-accent" />
          </span>
          <span className="font-display text-2xl font-semibold tracking-tight text-primary transition-colors group-hover:text-accent">
            BizOS
          </span>
          <span className="rounded-full bg-accent/10 border border-accent/20 px-2.5 py-0.5 font-mono text-[10px] text-accent tracking-widest">
            AI RUNTIME
          </span>
        </Link>
      </motion.div>

      {/* Auth Card Container */}
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="glass-panel p-6 sm:p-8 rounded-3xl shadow-2xl relative overflow-hidden border border-white/10 backdrop-blur-xl">
          {children}
        </div>
      </motion.div>

      {/* Footer info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="relative z-10 mt-8 flex flex-wrap items-center justify-center gap-6 font-mono text-xs text-secondary/70"
      >
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-accent" />
          <span>Enterprise Encryption</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Zap className="h-3.5 w-3.5 text-[#00F0FF]" />
          <span>Cognitive Core V2.4</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-accent" />
          <span>Autonomous AI Engine</span>
        </div>
      </motion.div>
    </div>
  );
}
