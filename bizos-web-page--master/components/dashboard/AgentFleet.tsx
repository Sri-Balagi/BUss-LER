"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useCognitiveState } from "@/lib/dashboard/state";
import type { AgentStatus } from "@/lib/dashboard/state";

const STATUS_STYLE: Record<AgentStatus, { dot: string; text: string; label: string }> = {
  thinking: { dot: "bg-core-blue", text: "text-core-blue", label: "Thinking" },
  executing: { dot: "bg-core-emerald", text: "text-core-emerald", label: "Executing" },
  blocked: { dot: "bg-core-violet", text: "text-core-violet", label: "Blocked" },
  idle: { dot: "bg-ink-faint", text: "text-ink-faint", label: "Idle" },
};

export default function AgentFleet() {
  const state = useCognitiveState();
  const [selected, setSelected] = useState<string | null>(null);

  const agents = state.selectedStage
    ? state.agents.filter((a) => a.stage === state.selectedStage)
    : state.agents;

  const selectedAgent = state.agents.find((a) => a.id === selected) ?? null;

  return (
    <div className="glass-panel col-span-full p-7 lg:col-span-2">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="eyebrow mb-2">Agents · live</p>
          <h2 className="font-display text-[19px] font-medium text-ink">Fleet</h2>
        </div>
        <span className="font-mono text-[11px] text-ink-faint">
          {agents.length} of {state.agents.length} shown
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <AnimatePresence mode="popLayout">
          {agents.map((agent) => {
            const style = STATUS_STYLE[agent.status];
            return (
              <motion.button
                layout
                key={agent.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                onClick={() => setSelected(selected === agent.id ? null : agent.id)}
                className={`rounded-xl border p-4 text-left transition-colors ${
                  selected === agent.id
                    ? "border-core-cyan/40 bg-core-cyan/[0.06]"
                    : "border-white/[0.06] bg-white/[0.02] hover:border-white/[0.14]"
                }`}
              >
                <div className="mb-3 flex items-center gap-2.5">
                  <span className="relative flex h-2 w-2 shrink-0">
                    {agent.status !== "idle" && (
                      <span
                        className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-60 ${style.dot}`}
                      />
                    )}
                    <span className={`relative inline-flex h-2 w-2 rounded-full ${style.dot}`} />
                  </span>
                  <span className="truncate font-display text-[14px] text-ink">{agent.name}</span>
                </div>
                <p className="mb-3 truncate text-[11.5px] text-ink-muted">{agent.role}</p>
                <div className="mb-2 h-1 w-full overflow-hidden rounded-full bg-white/[0.06]">
                  <motion.div
                    animate={{ width: `${agent.confidence * 100}%` }}
                    transition={{ duration: 0.5 }}
                    className="h-full rounded-full bg-gradient-to-r from-core-blue to-core-cyan"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className={`font-mono text-[10px] uppercase tracking-wide ${style.text}`}>
                    {style.label}
                  </span>
                  <span className="font-mono text-[10px] text-ink-faint">{agent.stage}</span>
                </div>
              </motion.button>
            );
          })}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
          >
            <p className="mb-1 font-mono text-[11px] uppercase tracking-wide text-core-cyan">
              {selectedAgent.name} · {Math.round(selectedAgent.confidence * 100)}% confidence
            </p>
            <p className="text-[13px] leading-relaxed text-ink-muted">
              Currently in <span className="text-ink">{selectedAgent.stage}</span>, status{" "}
              <span className="text-ink">{selectedAgent.status}</span>. Reasoning traces and
              tool calls for this agent will appear here once Agents is wired up.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
