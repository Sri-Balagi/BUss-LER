"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useCognitiveState, type AuditEntry } from "@/lib/dashboard/state";

const TYPE_COLOR: Record<AuditEntry["type"], string> = {
  agent: "text-core-blue",
  memory: "text-core-cyan",
  decision: "text-core-emerald",
  infra: "text-core-violet",
};

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour12: false });
}

export default function AuditLog() {
  const state = useCognitiveState();

  return (
    <div className="glass-panel col-span-full p-7">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="eyebrow mb-2">Audit Log · live</p>
          <h2 className="font-display text-[19px] font-medium text-ink">System is talking</h2>
        </div>
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-core-cyan opacity-60" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-core-cyan" />
        </span>
      </div>

      <div className="max-h-[180px] overflow-y-auto rounded-lg border border-white/[0.06] bg-black/20 p-4 font-mono text-[12px] leading-relaxed">
        <AnimatePresence initial={false}>
          {state.auditLog.map((entry) => (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <span className="shrink-0 text-ink-faint">{formatTime(entry.ts)}</span>
              <span className={`shrink-0 ${TYPE_COLOR[entry.type]}`}>[{entry.type}]</span>
              <span className="text-ink-muted">{entry.text}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
