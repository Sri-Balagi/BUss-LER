"use client";

import { MemoryGalaxyVisualizer } from "@/components/memory-galaxy";
import { motion } from "framer-motion";
import { Search } from "lucide-react";

import { useBusiness } from "@/lib/business-context";
import { NewAccountPage } from "@/components/NewAccountPage";

export default function MemoryLayer() {
  const { isPrimaryAccount } = useBusiness();

  if (!isPrimaryAccount) {
    return <NewAccountPage />;
  }
  return (
    <main className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-all duration-200 ease-[0.16,1,0.3,1] relative overflow-hidden">
      <MemoryGalaxyVisualizer />

      {/* Overlay UI */}
      <div className="relative z-10 mx-auto max-w-[1440px] pointer-events-none space-y-7">
        {/* Header */}
        <motion.div
          className="pointer-events-auto"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        >
          <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-accent">
            BizOS / Memory
          </p>
          <h1 className="mt-1 font-display text-[24px] md:text-[28px] font-semibold tracking-tight text-ink">
            Memory Layer
          </h1>
          <p className="mt-1 font-mono text-[11.5px] uppercase tracking-widest text-[#0EA5E9] dark:text-[#38BDF8] font-medium">
            Navigating Semantic Space
          </p>
        </motion.div>



        {/* Search / Command Card */}
        <motion.div
          className="pointer-events-auto w-full max-w-md"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="glass-card p-6 flex flex-col gap-4 rounded-[28px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 backdrop-blur-xl transition-all duration-200 ease-[0.16,1,0.3,1]">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#0EA5E9]" strokeWidth={1.75} />
              <input
                type="text"
                placeholder="Query semantic index..."
                className="w-full bg-white/90 dark:bg-zinc-800/90 border border-[#E2DAD0] dark:border-zinc-700 rounded-xl py-2.5 pl-10 pr-4 text-sm font-mono text-ink placeholder:text-ink-muted focus:outline-none focus:border-[#38BDF8] focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50 transition-colors"
              />
            </div>

            <div className="space-y-2.5">
              <h3 className="eyebrow text-accent font-mono text-[11px] font-medium uppercase tracking-[0.18em]">
                Recent Retrievals
              </h3>
              <div className="flex flex-col gap-1.5">
                <RetrievalItem text="Enterprise SSO Architecture v2" />
                <RetrievalItem text="Kubernetes scaling policies" />
                <RetrievalItem text="User interaction history [Q3]" />
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}

function RetrievalItem({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 group cursor-pointer p-2 rounded-xl hover:bg-white/90 dark:hover:bg-zinc-800/80 active:scale-[0.98] transition-all duration-200 border border-transparent hover:border-[#E2DAD0] dark:hover:border-zinc-700">
      <div className="w-1.5 h-1.5 rounded-full bg-[#0EA5E9]/40 group-hover:bg-[#0EA5E9] dark:group-hover:bg-[#38BDF8] transition-all" />
      <span className="font-mono text-xs text-ink-muted group-hover:text-ink font-medium transition-colors truncate">
        {text}
      </span>
    </div>
  );
}
