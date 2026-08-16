"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, X, Clock } from "lucide-react";
import { useCognitiveState, useCognitiveActions } from "@/lib/dashboard/state";

function timeAgo(ts: number) {
  const mins = Math.round((Date.now() - ts) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  return `${Math.round(mins / 60)}h ago`;
}

export default function DecisionCenter() {
  const state = useCognitiveState();
  const { decide } = useCognitiveActions();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <p className="eyebrow mb-2 text-accent">Decision Center · live</p>
      <h2 className="mb-5 font-display text-[20px] font-semibold text-ink tracking-tight">Needs your call</h2>

      <div className="space-y-3.5">
        <AnimatePresence mode="popLayout">
          {state.decisions.map((d) => (
            <motion.div
              layout
              key={d.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              className="rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/90 dark:bg-zinc-800/80 p-4.5 transition-all duration-200 ease-[0.16,1,0.3,1] hover:border-[#38BDF8] shadow-sm"
            >
              <div className="mb-2 flex items-start justify-between gap-3">
                <p className="text-[13.5px] font-semibold leading-snug text-ink">{d.title}</p>
                <span className="shrink-0 font-mono text-[10.5px] font-bold text-[#0EA5E9] dark:text-[#38BDF8] bg-[#F0F9FF] dark:bg-[#0F172A] px-2.5 py-0.5 rounded-full border border-[#38BDF8]/40">
                  {Math.round(d.confidence * 100)}%
                </span>
              </div>
              <p className="mb-3 text-[12px] leading-relaxed text-ink-muted font-light">{d.reasoning}</p>

              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1 font-mono text-[10px] text-ink-muted font-medium" suppressHydrationWarning>
                  <Clock className="h-3 w-3" /> {mounted ? timeAgo(d.ts) : "just now"}
                </span>

                {d.status === "pending" ? (
                  <div className="flex gap-2">
                    <button
                      onClick={() => decide(d.id, "rejected")}
                      className="flex items-center gap-1 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-[11px] font-medium text-red-600 dark:text-red-400 transition-colors hover:bg-red-500/20 cursor-pointer"
                    >
                      <X className="h-3 w-3" /> Reject
                    </button>
                    <button
                      onClick={() => decide(d.id, "approved")}
                      className="flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/15 px-3 py-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400 transition-colors hover:bg-emerald-500/25 cursor-pointer shadow-sm"
                    >
                      <Check className="h-3 w-3" /> Approve
                    </button>
                  </div>
                ) : (
                  <span
                    className={`font-mono text-[10px] font-bold uppercase tracking-wide px-2.5 py-0.5 rounded-full ${
                      d.status === "approved" ? "text-emerald-600 dark:text-emerald-400 bg-emerald-500/15 border border-emerald-500/30" : "text-red-600 dark:text-red-400 bg-red-500/15 border border-red-500/30"
                    }`}
                  >
                    {d.status}
                  </span>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
