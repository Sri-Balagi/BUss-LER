"use client";

import { motion } from "framer-motion";
import { Layers, Network, CheckCircle2, ChevronRight } from "lucide-react";

import { useBusiness } from "@/lib/business-context";
import { NewAccountPage } from "@/components/NewAccountPage";

export default function DecisionLayer() {
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
          className="flex flex-col sm:flex-row sm:items-end justify-between gap-4"
        >
          <div>
            <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-accent">
              BizOS / Decision
            </p>
            <div className="flex items-center gap-3 mt-1">
              <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-600 dark:text-purple-400">
                <Layers className="w-6 h-6 sm:w-7 sm:h-7" strokeWidth={1.75} />
              </div>
              <h1 className="font-display text-[24px] md:text-[28px] font-semibold tracking-tight text-ink">
                Decision Engine
              </h1>
            </div>
            <p className="font-mono text-[11.5px] uppercase tracking-widest text-[#0EA5E9] dark:text-[#38BDF8] font-medium mt-1">
              Reasoning & Approvals
            </p>
          </div>

          {/* Engine Status Card */}
          <div className="glass-card px-5 py-2.5 rounded-full border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.04)] flex items-center gap-3 self-start sm:self-auto">
            <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent font-semibold">
              Engine Status
            </span>
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-purple-500 opacity-75 motion-reduce:animate-none" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-purple-500" />
              </span>
              <span className="font-mono text-xs font-bold text-ink uppercase tracking-wider">
                Optimal
              </span>
            </div>
          </div>
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-7">
          {/* Reasoning Tree */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-7 flex flex-col"
          >
            <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1] flex flex-col h-full">
              <p className="eyebrow mb-6 text-accent font-mono text-[11px] font-medium uppercase tracking-[0.18em]">
                Active Reasoning Tree
              </p>

              <div className="flex-1 border border-[#E2DAD0] dark:border-zinc-800 rounded-2xl bg-white/60 dark:bg-zinc-800/30 p-6 sm:p-8 flex flex-col justify-center items-center gap-6 overflow-x-auto">
                <ReasoningNode
                  title="Evaluate Infrastructure Scale"
                  confidence={85}
                  active
                />

                <div className="w-px h-8 bg-gradient-to-b from-purple-500 to-[#E2DAD0] dark:to-zinc-700" />

                <div className="flex flex-col sm:flex-row gap-6 w-full justify-center items-center">
                  <ReasoningNode
                    title="Historical Traffic Analysis"
                    confidence={92}
                    source="Memory Layer"
                  />
                  <ReasoningNode
                    title="Current CPU Saturation"
                    confidence={99}
                    source="Metrics Core"
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Confidence & Approvals */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-5 flex flex-col"
          >
            <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1] flex flex-col gap-8 h-full">
              {/* Execution Confidence */}
              <div>
                <p className="eyebrow mb-4 text-accent font-mono text-[11px] font-medium uppercase tracking-[0.18em]">
                  Execution Confidence
                </p>
                <div className="flex items-end gap-3 mb-3">
                  <span className="font-display text-5xl sm:text-6xl font-bold text-ink tracking-tight">
                    97%
                  </span>
                  <span className="font-mono text-sm text-ink-muted pb-2 font-medium">
                    / 100
                  </span>
                </div>
                <div className="w-full h-2 bg-[#E2DAD0] dark:bg-zinc-800 rounded-full overflow-hidden p-0.5">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-500 via-[#0EA5E9] to-emerald-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: "97%" }}
                    transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>
              </div>

              {/* Approval History */}
              <div className="flex-1 flex flex-col">
                <p className="eyebrow mb-4 text-accent font-mono text-[11px] font-medium uppercase tracking-[0.18em]">
                  Approval History
                </p>
                <div className="space-y-3 flex-1">
                  <ApprovalItem action="Scale Redis Cluster" time="2m ago" />
                  <ApprovalItem action="Purge Edge Cache" time="15m ago" />
                  <ApprovalItem action="Rotate Auth Keys" time="1h ago" />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  );
}

function ReasoningNode({
  title,
  confidence,
  source,
  active,
}: {
  title: string;
  confidence: number;
  source?: string;
  active?: boolean;
}) {
  return (
    <div
      className={`relative p-4 rounded-2xl border transition-all duration-200 w-full sm:w-[280px] ${
        active
          ? "border-purple-500/50 bg-purple-500/10 shadow-sm"
          : "border-[#E2DAD0] dark:border-zinc-700 bg-white/90 dark:bg-zinc-800/80 hover:border-[#38BDF8]"
      } flex flex-col gap-2`}
    >
      <div className="flex justify-between items-start gap-2">
        <span className="font-medium text-xs sm:text-sm text-ink leading-snug">{title}</span>
        <span
          className={`font-mono text-xs font-bold px-2 py-0.5 rounded-full ${
            active
              ? "text-purple-600 dark:text-purple-400 bg-purple-500/15"
              : "text-ink-muted bg-black/5 dark:bg-white/5"
          }`}
        >
          {confidence}%
        </span>
      </div>
      {source && (
        <div className="flex items-center gap-1.5 text-ink-muted mt-1">
          <Network className="w-3.5 h-3.5 text-[#0EA5E9]" strokeWidth={1.75} />
          <span className="font-mono text-[10px] uppercase tracking-wider font-semibold">
            {source}
          </span>
        </div>
      )}
    </div>
  );
}

function ApprovalItem({ action, time }: { action: string; time: string }) {
  return (
    <div className="flex items-center justify-between p-3.5 rounded-xl border border-[#E2DAD0] dark:border-zinc-800/80 bg-white/80 dark:bg-zinc-800/50 hover:bg-white dark:hover:bg-zinc-800 hover:border-[#38BDF8] active:scale-[0.98] transition-all duration-200 cursor-pointer group">
      <div className="flex items-center gap-3">
        <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" strokeWidth={1.75} />
        <span className="font-mono text-xs font-semibold text-ink">{action}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="font-mono text-[10.5px] text-ink-muted font-medium">{time}</span>
        <ChevronRight className="w-3.5 h-3.5 text-ink-muted group-hover:text-ink transition-colors" />
      </div>
    </div>
  );
}
