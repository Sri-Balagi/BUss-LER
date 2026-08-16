"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useCognitiveState } from "@/lib/dashboard/state";
import type { AgentStatus } from "@/lib/dashboard/state";

const STATUS_STYLE: Record<AgentStatus, { dot: string; text: string; label: string }> = {
  thinking: { dot: "bg-[#0EA5E9]", text: "text-[#0EA5E9] dark:text-[#38BDF8]", label: "Thinking" },
  executing: { dot: "bg-emerald-500", text: "text-emerald-600 dark:text-emerald-400", label: "Executing" },
  blocked: { dot: "bg-purple-500", text: "text-purple-600 dark:text-purple-400", label: "Blocked" },
  idle: { dot: "bg-zinc-400", text: "text-ink-muted", label: "Idle" },
};

export default function AgentFleet() {
  const state = useCognitiveState();
  const [selected, setSelected] = useState<string | null>(null);

  const agents = state.selectedStage
    ? state.agents.filter((a) => a.stage === state.selectedStage)
    : state.agents;

  const selectedAgent = state.agents.find((a) => a.id === selected) ?? null;

  return (
    <div className="glass-card col-span-1 md:col-span-2 lg:col-span-2 p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="eyebrow mb-2 text-accent">Agents · live</p>
          <h2 className="font-display text-[20px] font-semibold text-ink tracking-tight">Fleet</h2>
        </div>
        <span className="font-mono text-[11px] font-medium text-ink-muted px-3 py-1 rounded-full border border-[#E2DAD0] dark:border-zinc-700 bg-white/80 dark:bg-zinc-800 shadow-sm">
          {agents.length} of {state.agents.length} shown
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-3">
        <AnimatePresence mode="popLayout">
          {agents.map((agent) => {
            const style = STATUS_STYLE[agent.status];
            const isSel = selected === agent.id;
            return (
              <motion.button
                layout
                key={agent.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                onClick={() => setSelected(isSel ? null : agent.id)}
                className={`rounded-2xl border-2 p-4 text-left transition-all duration-200 ease-[0.16,1,0.3,1] hover:scale-[1.02] cursor-pointer ${
                  isSel
                    ? "border-[#38BDF8] bg-[#F0F9FF] dark:bg-[#0F172A] shadow-sm"
                    : "border-[#E2DAD0] dark:border-zinc-800 bg-white/90 dark:bg-zinc-800/80 hover:border-[#38BDF8]"
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
                  <span className="truncate font-display text-[14px] font-bold text-ink">{agent.name}</span>
                </div>
                <p className="mb-3 truncate text-[11.5px] text-ink-muted font-medium">{agent.role}</p>
                <div className="mb-2.5 h-1.5 w-full overflow-hidden rounded-full bg-[#E2DAD0] dark:bg-zinc-700">
                  <motion.div
                    animate={{ width: `${agent.confidence * 100}%` }}
                    transition={{ duration: 0.4 }}
                    className="h-full rounded-full bg-gradient-to-r from-[#0EA5E9] to-[#38BDF8]"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className={`font-mono text-[10px] font-bold uppercase tracking-wide ${style.text}`}>
                    {style.label}
                  </span>
                  <span className="font-mono text-[10px] font-medium text-ink-muted">{agent.stage}</span>
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
            className="mt-5 overflow-hidden rounded-2xl border-2 border-[#E2DAD0] dark:border-zinc-800 bg-white/90 dark:bg-zinc-800/90 p-4.5 shadow-sm"
          >
            <p className="mb-1 font-mono text-[11px] font-bold uppercase tracking-wide text-[#0EA5E9] dark:text-[#38BDF8]">
              {selectedAgent.name} · {Math.round(selectedAgent.confidence * 100)}% confidence
            </p>
            <p className="text-[13px] leading-relaxed text-ink-muted font-light">
              Currently in <span className="text-ink font-semibold">{selectedAgent.stage}</span>, status{" "}
              <span className="text-ink font-semibold">{selectedAgent.status}</span>. Reasoning traces and
              tool calls for this agent will appear here once Agents is wired up.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
