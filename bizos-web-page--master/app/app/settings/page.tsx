"use client";

import { motion } from "framer-motion";
import { Settings, Wrench } from "lucide-react";

import { useBusiness } from "@/lib/business-context";
import { NewAccountPage } from "@/components/NewAccountPage";

export default function SettingsLayer() {
  const { isPrimaryAccount } = useBusiness();

  if (!isPrimaryAccount) {
    return <NewAccountPage />;
  }
  return (
    <main className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-all duration-200 ease-[0.16,1,0.3,1]">
      <div className="mx-auto max-w-[1440px] space-y-7">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-accent">
            BizOS / Settings
          </p>
        </motion.div>

        {/* Central Enterprise Glass Panel */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
          className="flex justify-center items-center pt-8 sm:pt-16"
        >
          <div className="glass-card p-8 sm:p-12 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1] flex flex-col items-center text-center max-w-lg w-full">
            <div className="w-16 h-16 rounded-2xl bg-[#0EA5E9]/10 border border-[#38BDF8]/30 flex items-center justify-center mb-6 text-[#0EA5E9] dark:text-[#38BDF8]">
              <Settings className="w-8 h-8" strokeWidth={1.75} />
            </div>

            <h1 className="font-display text-[24px] sm:text-[28px] font-semibold text-ink tracking-tight mb-3">
              System Preferences
            </h1>

            <p className="font-body text-sm sm:text-base text-ink-muted leading-relaxed mb-8 max-w-md font-medium">
              Global OS preferences, API key management, model selection, and access controls are currently locked down.
            </p>

            <div className="flex items-center gap-2.5 px-5 py-2 rounded-full border border-[#E2DAD0] dark:border-zinc-800 bg-white/90 dark:bg-zinc-800/90 shadow-sm transition-all duration-200 hover:border-[#38BDF8]">
              <Wrench className="w-4 h-4 text-[#0EA5E9] dark:text-[#38BDF8]" strokeWidth={1.75} />
              <span className="font-mono text-xs uppercase tracking-widest text-ink font-semibold">
                Coming Soon
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
