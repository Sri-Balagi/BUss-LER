"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useCognitiveState } from "@/lib/dashboard/state";

const GROUP_COLOR: Record<string, string> = {
  policy: "#0EA5E9",
  product: "#38BDF8",
  customer: "#8B5CF6",
  runbook: "#10B981",
};

export default function KnowledgeGraphWidget() {
  const state = useCognitiveState();
  const [hovered, setHovered] = useState<string | null>(null);

  const neighborsOf = (id: string) =>
    new Set(
      state.knowledgeEdges
        .filter(([a, b]) => a === id || b === id)
        .flatMap(([a, b]) => [a, b])
    );

  const highlighted = hovered ? neighborsOf(hovered) : null;
  const [activeFrom, activeTo] = state.knowledgeEdges[state.activeEdge];

  return (
    <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <p className="eyebrow mb-2 text-accent">Knowledge Graph · live</p>
      <h2 className="mb-4 font-display text-[20px] font-semibold text-ink tracking-tight">What agents are reading</h2>

      <svg viewBox="0 0 300 260" className="w-full h-auto rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/60 dark:bg-zinc-950/60 p-2">
        {state.knowledgeEdges.map(([a, b], i) => {
          const na = state.knowledgeNodes.find((n) => n.id === a)!;
          const nb = state.knowledgeNodes.find((n) => n.id === b)!;
          const isActive = i === state.activeEdge;
          const dim = highlighted && !(highlighted.has(a) && highlighted.has(b));
          return (
            <line
              key={`${a}-${b}`}
              x1={na.x}
              y1={na.y}
              x2={nb.x}
              y2={nb.y}
              stroke={isActive ? "#0EA5E9" : "rgba(161,161,170,0.3)"}
              strokeWidth={isActive ? 2 : 1}
              opacity={dim ? 0.15 : 1}
            />
          );
        })}

        <motion.circle
          key={state.activeEdge}
          r={3.5}
          fill="#0EA5E9"
          initial={{
            cx: state.knowledgeNodes.find((n) => n.id === activeFrom)!.x,
            cy: state.knowledgeNodes.find((n) => n.id === activeFrom)!.y,
          }}
          animate={{
            cx: state.knowledgeNodes.find((n) => n.id === activeTo)!.x,
            cy: state.knowledgeNodes.find((n) => n.id === activeTo)!.y,
          }}
          transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
        />

        {state.knowledgeNodes.map((n) => {
          const dim = highlighted && !highlighted.has(n.id) && hovered !== n.id;
          return (
            <g
              key={n.id}
              onMouseEnter={() => setHovered(n.id)}
              onMouseLeave={() => setHovered(null)}
              className="cursor-pointer"
            >
              <circle
                cx={n.x}
                cy={n.y}
                r={hovered === n.id ? 7 : 5}
                fill={GROUP_COLOR[n.group]}
                opacity={dim ? 0.2 : 0.95}
                style={{ transition: "r 0.15s ease, opacity 0.15s ease" }}
              />
              <text
                x={n.x}
                y={n.y - 11}
                textAnchor="middle"
                fontSize="8.5"
                fill={dim ? "rgba(113,113,122,0.4)" : "currentColor"}
                className="text-ink font-semibold"
                fontFamily="var(--font-mono)"
              >
                {n.label}
              </text>
            </g>
          );
        })}
      </svg>

      <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1.5 font-mono text-[10.5px] font-semibold uppercase tracking-wider text-ink-muted">
        {Object.entries(GROUP_COLOR).map(([group, color]) => (
          <span key={group} className="flex items-center gap-1.5 rounded-full border border-[#E2DAD0] dark:border-zinc-800 bg-white/80 dark:bg-zinc-800/80 px-2.5 py-0.5 shadow-sm">
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
            {group}
          </span>
        ))}
      </div>
    </div>
  );
}
