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
        className="flex w-full items-center gap-2 py-2 text-left"
        style={{ paddingLeft: depth * 16 }}
      >
        {hasChildren ? (
          <motion.span animate={{ rotate: open ? 90 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronRight className="h-3.5 w-3.5 text-ink-faint" />
          </motion.span>
        ) : (
          <span className="w-3.5" />
        )}
        <span className={`flex-1 truncate text-[13px] ${depth === 0 ? "text-ink" : "text-ink-muted"}`}>
          {goal.label}
        </span>
        <span className="w-9 shrink-0 text-right font-mono text-[10.5px] text-ink-faint">
          {Math.round(goal.progress * 100)}%
        </span>
      </button>
      <div className="ml-[22px] mr-1 h-1 overflow-hidden rounded-full bg-white/[0.06]" style={{ marginLeft: depth * 16 + 22 }}>
        <motion.div
          animate={{ width: `${goal.progress * 100}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="h-full rounded-full bg-gradient-to-r from-core-violet to-core-cyan"
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
    <div className="glass-panel col-span-full p-7">
      <p className="eyebrow mb-2">Goal Manager · live</p>
      <h2 className="mb-4 font-display text-[19px] font-medium text-ink">What it's working toward</h2>

      <div className="grid gap-x-8 sm:grid-cols-3">
        {state.goals.map((goal) => (
          <GoalRow key={goal.id} goal={goal} depth={0} />
        ))}
      </div>
    </div>
  );
}
