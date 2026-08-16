"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useOnboarding } from "@/lib/onboarding-context";
import {
  Building2,
  Boxes,
  Zap,
  CheckCircle2,
  X,
  Brain,
} from "lucide-react";

function WelcomeBannerContent() {
  const searchParams = useSearchParams();
  const { data } = useOnboarding();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (searchParams.get("welcome") === "true" || data.completed) {
      setVisible(true);
    }
  }, [searchParams, data.completed]);

  if (!visible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -20, scale: 0.98 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="mb-8 w-full"
      >
        <div className="glass-panel p-6 sm:p-8 rounded-[28px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 shadow-[0_8px_32px_rgba(0,0,0,0.04)] relative overflow-hidden backdrop-blur-xl transition-all duration-200 ease-[0.16,1,0.3,1]">
          {/* Background Decorative Glow */}
          <div className="absolute top-0 right-0 h-48 w-48 bg-accent/10 rounded-full blur-3xl pointer-events-none" />

          {/* Close button */}
          <button
            onClick={() => setVisible(false)}
            className="absolute top-5 right-5 flex h-8 w-8 items-center justify-center rounded-full border border-[#E2DAD0] dark:border-zinc-700 bg-white/80 dark:bg-zinc-800 text-ink-muted hover:text-ink hover:border-[#38BDF8] active:scale-95 transition-all duration-200 ease-[0.16,1,0.3,1] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50 cursor-pointer"
            title="Dismiss Welcome Banner"
          >
            <X className="h-4 w-4" />
          </button>

          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DAD0] dark:border-zinc-800 pb-6 mb-6">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent text-white shadow-md shrink-0 mt-1">
                <Brain className="h-6 w-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="eyebrow">DIGITAL TWIN INITIALIZED</span>
                  <span className="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-2.5 py-0.5 font-mono text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold">
                    ONLINE
                  </span>
                </div>
                <h2 className="font-display text-2xl font-semibold tracking-tight text-ink mt-1">
                  Welcome to your BizOS Environment, {data.businessName || "Partner"}!
                </h2>
                <p className="text-xs text-ink-muted mt-1 font-light">
                  Your cognitive engine is live and configured based on your onboarding profile.
                </p>
              </div>
            </div>
          </div>

          {/* Summary Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Business Profile */}
            <div className="flex flex-col gap-2 rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/80 dark:bg-zinc-800/80 p-4.5 shadow-sm">
              <span className="text-[11px] font-mono text-ink-muted uppercase tracking-wider flex items-center gap-1.5 font-medium">
                <Building2 className="h-3.5 w-3.5 text-accent" />
                Business Profile
              </span>
              <div className="text-sm font-bold text-ink">{data.businessName}</div>
              <div className="text-xs text-ink-muted">{data.industry} • {data.businessType}</div>
              <div className="text-[11px] text-ink-faint font-mono">{data.companySize} • {data.timezone}</div>
            </div>

            {/* Selected Modules */}
            <div className="flex flex-col gap-2 rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/80 dark:bg-zinc-800/80 p-4.5 shadow-sm">
              <span className="text-[11px] font-mono text-ink-muted uppercase tracking-wider flex items-center gap-1.5 font-medium">
                <Boxes className="h-3.5 w-3.5 text-[#0EA5E9]" />
                Active Modules ({data.selectedModules.length})
              </span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {data.selectedModules.slice(0, 6).map((m) => (
                  <span
                    key={m}
                    className="rounded-full border border-[#E2DAD0] dark:border-zinc-700 bg-[#FAF7F2] dark:bg-zinc-900 px-2.5 py-0.5 text-[11px] font-medium text-ink"
                  >
                    {m}
                  </span>
                ))}
                {data.selectedModules.length > 6 && (
                  <span className="rounded-full bg-accent/15 text-accent border border-accent/20 px-2 py-0.5 text-[10px] font-mono font-semibold">
                    +{data.selectedModules.length - 6} more
                  </span>
                )}
              </div>
            </div>

            {/* Integrations */}
            <div className="flex flex-col gap-2 rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/80 dark:bg-zinc-800/80 p-4.5 shadow-sm">
              <span className="text-[11px] font-mono text-ink-muted uppercase tracking-wider flex items-center gap-1.5 font-medium">
                <Zap className="h-3.5 w-3.5 text-emerald-500" />
                Connected Tools ({data.selectedIntegrations.length})
              </span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {data.selectedIntegrations.length > 0 ? (
                  data.selectedIntegrations.map((i) => (
                    <span
                      key={i}
                      className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-medium text-emerald-600 dark:text-emerald-400"
                    >
                      {i}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-ink-muted italic">No integrations connected yet</span>
                )}
              </div>
            </div>
          </div>

          {/* Suggested Next Actions */}
          <div className="rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/90 dark:bg-zinc-800/90 p-4.5 shadow-sm">
            <span className="text-xs font-mono uppercase tracking-wider text-ink-muted block mb-3 font-medium">
              Suggested Next Actions
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="flex items-center gap-3 rounded-xl border border-[#E2DAD0] dark:border-zinc-700 bg-[#FAF7F2] dark:bg-zinc-900 p-3 text-xs text-ink font-medium hover:border-[#38BDF8] active:scale-[0.98] transition-all duration-200 ease-[0.16,1,0.3,1] cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50">
                <CheckCircle2 className="h-4 w-4 text-accent shrink-0" />
                <span>Verify Agent Fleet Assignments</span>
              </div>
              <div className="flex items-center gap-3 rounded-xl border border-[#E2DAD0] dark:border-zinc-700 bg-[#FAF7F2] dark:bg-zinc-900 p-3 text-xs text-ink font-medium hover:border-[#38BDF8] active:scale-[0.98] transition-all duration-200 ease-[0.16,1,0.3,1] cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50">
                <CheckCircle2 className="h-4 w-4 text-[#0EA5E9] shrink-0" />
                <span>Upload Initial Knowledge Runbooks</span>
              </div>
              <div className="flex items-center gap-3 rounded-xl border border-[#E2DAD0] dark:border-zinc-700 bg-[#FAF7F2] dark:bg-zinc-900 p-3 text-xs text-ink font-medium hover:border-[#38BDF8] active:scale-[0.98] transition-all duration-200 ease-[0.16,1,0.3,1] cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                <span>Test Live Decision Engine</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

export default function WelcomeBanner() {
  return (
    <Suspense fallback={null}>
      <WelcomeBannerContent />
    </Suspense>
  );
}
