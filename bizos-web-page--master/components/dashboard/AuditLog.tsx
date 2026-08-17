"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useCognitiveState, type AuditEntry } from "@/lib/dashboard/state";

const TYPE_COLOR: Record<AuditEntry["type"], string> = {
  agent: "text-[#0EA5E9] dark:text-[#38BDF8]",
  memory: "text-[#0EA5E9] dark:text-[#38BDF8]",
  decision: "text-emerald-600 dark:text-emerald-400",
  infra: "text-purple-600 dark:text-purple-400",
};

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour12: false });
}

export default function AuditLog() {
  const state = useCognitiveState();

  return (
    <div className="glass-card col-span-1 md:col-span-2 lg:col-span-4 p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="eyebrow mb-2 text-accent">Audit Log · live</p>
          <h2 className="font-display text-[20px] font-semibold text-ink tracking-tight">System is talking</h2>
        </div>
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75 motion-reduce:animate-none" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-accent" />
        </span>
      </div>

      <div className="max-h-[190px] overflow-y-auto rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/90 dark:bg-zinc-950/90 p-4.5 font-mono text-[12px] leading-relaxed shadow-inner">
        <AnimatePresence initial={false}>
          {state.auditLog.map((entry) => (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 py-0.5"
            >
              <span className="shrink-0 text-ink-muted font-medium">{formatTime(entry.ts)}</span>
              <span className={`shrink-0 font-bold ${TYPE_COLOR[entry.type]}`}>[{entry.type}]</span>
              <span className="text-ink font-light">{entry.text}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
