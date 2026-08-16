"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { useCognitiveState, type Goal } from "@/lib/dashboard/state";

function GoalRow({ goal, depth }: { goal: Goal; depth: number }) {
  const [open, setOpen] = useState(depth === 0);
  const hasChildren = !!goal.children?.length;

  return (
    <div>
      <button
        onClick={() => hasChildren && setOpen((o) => !o)}
        className="flex w-full items-center gap-2 py-2 text-left cursor-pointer group rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50 active:scale-[0.99] transition-all duration-200"
        style={{ paddingLeft: depth * 16 }}
      >
        {hasChildren ? (
          <motion.span animate={{ rotate: open ? 90 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronRight className="h-3.5 w-3.5 text-ink-muted group-hover:text-ink" />
          </motion.span>
        ) : (
          <span className="w-3.5" />
        )}
        <span className={`flex-1 truncate text-[13px] font-medium ${depth === 0 ? "text-ink font-semibold" : "text-ink-muted group-hover:text-ink"}`}>
          {goal.label}
        </span>
        <span className="w-10 shrink-0 text-right font-mono text-[10.5px] font-semibold text-ink-muted">
          {Math.round(goal.progress * 100)}%
        </span>
      </button>
      <div className="ml-[22px] mr-1 h-1.5 overflow-hidden rounded-full bg-[#E2DAD0] dark:bg-zinc-800" style={{ marginLeft: depth * 16 + 22 }}>
        <motion.div
          animate={{ width: `${goal.progress * 100}%` }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="h-full rounded-full bg-gradient-to-r from-accent via-[#F97316] to-[#0EA5E9]"
        />
      </div>

      <AnimatePresence>
        {hasChildren && open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            {goal.children!.map((child) => (
              <GoalRow key={child.id} goal={child} depth={depth + 1} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function GoalManager() {
  const state = useCognitiveState();

  return (
    <div className="glass-card col-span-1 md:col-span-2 lg:col-span-4 p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <p className="eyebrow mb-2 text-accent">Goal Manager · live</p>
      <h2 className="mb-4 font-display text-[20px] font-semibold text-ink tracking-tight">What it's working toward</h2>

      <div className="grid gap-x-8 sm:grid-cols-3">
        {state.goals.map((goal) => (
          <GoalRow key={goal.id} goal={goal} depth={0} />
        ))}
      </div>
    </div>
  );
}
