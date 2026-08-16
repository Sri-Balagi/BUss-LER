"use client";

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

  return (
    <div className="glass-panel p-7">
      <p className="eyebrow mb-2">Decision Center · live</p>
      <h2 className="mb-5 font-display text-[19px] font-medium text-ink">Needs your call</h2>

      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {state.decisions.map((d) => (
            <motion.div
              layout
              key={d.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
            >
              <div className="mb-2 flex items-start justify-between gap-3">
                <p className="text-[13.5px] leading-snug text-ink">{d.title}</p>
                <span className="shrink-0 font-mono text-[10px] text-ink-faint">
                  {Math.round(d.confidence * 100)}%
                </span>
              </div>
              <p className="mb-3 text-[12px] leading-relaxed text-ink-muted">{d.reasoning}</p>

              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1 font-mono text-[10px] text-ink-faint">
                  <Clock className="h-3 w-3" /> {timeAgo(d.ts)}
                </span>

                {d.status === "pending" ? (
                  <div className="flex gap-2">
                    <button
                      onClick={() => decide(d.id, "rejected")}
                      className="flex items-center gap-1 rounded-full border border-white/10 px-3 py-1 text-[11px] text-ink-muted transition-colors hover:border-red-400/30 hover:text-red-300"
                    >
                      <X className="h-3 w-3" /> Reject
                    </button>
                    <button
                      onClick={() => decide(d.id, "approved")}
                      className="flex items-center gap-1 rounded-full border border-core-emerald/30 bg-core-emerald/10 px-3 py-1 text-[11px] text-core-emerald transition-colors hover:bg-core-emerald/20"
                    >
                      <Check className="h-3 w-3" /> Approve
                    </button>
                  </div>
                ) : (
                  <span
                    className={`font-mono text-[10px] uppercase tracking-wide ${
                      d.status === "approved" ? "text-core-emerald" : "text-red-300"
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
