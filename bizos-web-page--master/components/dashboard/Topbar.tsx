"use client";

import { Search } from "lucide-react";
import { useCognitiveState } from "@/lib/dashboard/state";

export default function Topbar() {
  const state = useCognitiveState();
  const activeAgents = state.agents.filter((a) => a.status !== "idle").length;

  return (
    <header className="sticky top-4 z-30 mb-6 flex items-center justify-between gap-4">
      <div>
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
          BizOS / Dashboard
        </p>
        <h1 className="mt-1 font-display text-[22px] font-medium text-ink">
          Cognitive overview
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <div className="glass-panel hidden items-center gap-2 px-3.5 py-2 sm:flex">
          <Search className="h-3.5 w-3.5 text-ink-faint" strokeWidth={1.6} />
          <input
            placeholder="Search runs, agents, memories…"
            className="w-48 bg-transparent text-[13px] text-ink placeholder:text-ink-faint focus:outline-none"
          />
        </div>

        <div className="glass-panel flex items-center gap-2 px-3.5 py-2">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-core-emerald opacity-60" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-core-emerald" />
          </span>
          <span className="font-mono text-[11px] text-ink-muted">
            {activeAgents} agents active
          </span>
        </div>

        <div className="flex h-9 w-9 items-center justify-center rounded-full border border-white/10 bg-gradient-to-br from-core-blue/30 to-core-violet/30 font-display text-[12px] text-ink">
          NS
        </div>
      </div>
    </header>
  );
}
