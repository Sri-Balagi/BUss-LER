"use client";

import { motion } from "framer-motion";
import { Brain, Server, Shield, Zap } from "lucide-react";

import { useBusiness } from "@/lib/business-context";
import { NewAccountPage } from "@/components/NewAccountPage";

export default function CoreDashboard() {
  const { isPrimaryAccount } = useBusiness();

  if (!isPrimaryAccount) {
    return <NewAccountPage />;
  }
  return (
    <main className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-all duration-200 ease-[0.16,1,0.3,1]">
      <div className="mx-auto max-w-[1440px] space-y-7">
        {/* Page Header */}
        <div>
          <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-accent">
            BizOS / Digital Twin
          </p>
          <h1 className="mt-1 font-display text-[24px] md:text-[28px] font-semibold tracking-tight text-ink">
            Core Runtime
          </h1>
        </div>

        {/* 3-Column Enterprise Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-7">
          {/* Left Column: AI Status Ring & Core Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-4 flex flex-col gap-6"
          >
            <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
              <p className="eyebrow mb-4 text-accent">Cognitive Core</p>

              {/* Status Ring Radial Gauge */}
              <div className="flex flex-col items-center justify-center my-4">
                <div className="relative w-44 h-44 flex items-center justify-center">
                  <motion.div
                    className="absolute inset-0 rounded-full border border-[#0EA5E9]/30 opacity-40"
                    animate={{ scale: [1, 1.15, 1], opacity: [0.3, 0.1, 0.3] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                  />
                  <svg className="w-full h-full -rotate-90">
                    <circle
                      cx="88"
                      cy="88"
                      r="78"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="6"
                      className="text-[#E2DAD0] dark:text-zinc-800"
                    />
                    <motion.circle
                      cx="88"
                      cy="88"
                      r="78"
                      fill="none"
                      stroke="#0EA5E9"
                      strokeWidth="6"
                      strokeLinecap="round"
                      strokeDasharray="490"
                      strokeDashoffset="10"
                      animate={{ strokeDashoffset: 10 }}
                      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                    />
                  </svg>
                  <div className="absolute text-center">
                    <span className="block font-display text-[32px] font-bold text-ink">98%</span>
                    <span className="block font-mono text-[10px] uppercase tracking-widest text-ink-muted font-semibold mt-0.5">
                      Efficiency
                    </span>
                  </div>
                </div>
              </div>

              {/* Status Rows */}
              <div className="w-full space-y-3 mt-6">
                <StatusRow icon={Brain} label="Cognitive" value="Optimal" color="emerald" />
                <StatusRow icon={Server} label="Memory" value="Syncing" color="sky" />
                <StatusRow icon={Zap} label="Decision" value="Active" color="purple" />
                <StatusRow icon={Shield} label="Security" value="Secured" color="emerald" />
              </div>
            </div>
          </motion.div>

          {/* Center Column: Live Cognitive Visualizer */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-4 flex flex-col"
          >
            <div className="glass-card min-h-[380px] p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1] flex flex-col items-center justify-center relative overflow-hidden text-center h-full">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(14,165,233,0.06)_0%,transparent_70%)] pointer-events-none" />
              <div className="relative z-10 px-4 py-8">
                <Brain className="w-16 h-16 text-[#0EA5E9] dark:text-[#38BDF8] mx-auto mb-5 animate-pulse motion-reduce:animate-none" strokeWidth={1.5} />
                <h2 className="font-display text-[22px] font-semibold text-ink tracking-tight mb-2">
                  Cognitive Network Idle
                </h2>
                <p className="font-mono text-[11.5px] uppercase tracking-widest text-ink-muted font-medium">
                  Awaiting Workflow Execution
                </p>
              </div>
            </div>
          </motion.div>

          {/* Right Column: ThoughtStream (Timeline) */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-4 flex flex-col"
          >
            <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1] flex flex-col h-full">
              <p className="eyebrow mb-6 text-accent">Cognitive Timeline</p>

              <div className="flex-1 space-y-5 relative before:absolute before:inset-y-0 before:left-3 before:w-px before:bg-[#E2DAD0] dark:before:bg-zinc-800">
                <TimelineEvent time="22:14:03" action="Execution Complete" state="emerald" />
                <TimelineEvent time="22:14:01" action="Decision Generated" state="emerald" detail="Confidence: 99.2%" />
                <TimelineEvent time="22:13:58" action="Reasoning Reached" state="sky" />
                <TimelineEvent time="22:13:54" action="Knowledge Retrieved" state="purple" detail="12 semantic clusters found" />
                <TimelineEvent time="22:13:50" action="Memory Accessed" state="purple" />
                <TimelineEvent time="22:13:48" action="Workflow Initiated" state="sky" />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  );
}

function StatusRow({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) {
  const badgeColors: Record<string, string> = {
    emerald: "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    sky: "text-[#0EA5E9] dark:text-[#38BDF8] bg-[#F0F9FF] dark:bg-[#0F172A] border-[#38BDF8]/40",
    purple: "text-purple-600 dark:text-purple-400 bg-purple-500/10 border-purple-500/30",
  };

  return (
    <div className="flex items-center justify-between font-mono text-[12px] p-2.5 rounded-xl border border-[#E2DAD0] dark:border-zinc-800/80 bg-white/80 dark:bg-zinc-800/50 shadow-sm transition-all duration-200 hover:border-[#38BDF8]">
      <div className="flex items-center gap-2.5 text-ink">
        <Icon className="w-4 h-4 text-ink-muted" strokeWidth={1.75} />
        <span className="uppercase tracking-wider font-semibold">{label}</span>
      </div>
      <span className={`font-mono text-[10.5px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${badgeColors[color]}`}>
        {value}
      </span>
    </div>
  );
}

function TimelineEvent({ time, action, state, detail }: { time: string; action: string; state: string; detail?: string }) {
  const dotColors: Record<string, string> = {
    emerald: "bg-emerald-500",
    sky: "bg-[#0EA5E9]",
    purple: "bg-purple-500",
  };

  return (
    <div className="relative pl-8 group">
      <div className={`absolute left-[9px] top-1.5 h-2.5 w-2.5 rounded-full ${dotColors[state]} shadow-sm group-hover:scale-125 transition-transform duration-200`} />
      <div className="font-mono text-[10.5px] text-ink-muted font-medium mb-0.5">{time}</div>
      <div className="text-[13.5px] font-semibold text-ink leading-snug">{action}</div>
      {detail && <div className="text-[12px] text-ink-muted font-light mt-0.5">{detail}</div>}
    </div>
  );
}
