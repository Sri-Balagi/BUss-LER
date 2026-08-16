"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useCognitiveState } from "@/lib/dashboard/state";

const GROUP_COLOR: Record<string, string> = {
  policy: "rgb(47,111,255)",
  product: "rgb(76,224,224)",
  customer: "rgb(139,92,246)",
  runbook: "rgb(52,211,153)",
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
    <div className="glass-panel p-7">
      <p className="eyebrow mb-2">Knowledge Graph · live</p>
      <h2 className="mb-4 font-display text-[19px] font-medium text-ink">What agents are reading</h2>

      <svg viewBox="0 0 300 260" className="w-full">
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
              stroke={isActive ? "rgba(76,224,224,0.8)" : "rgba(124,135,152,0.25)"}
              strokeWidth={isActive ? 2 : 1}
              opacity={dim ? 0.15 : 1}
            />
          );
        })}

        <motion.circle
          key={state.activeEdge}
          r={3}
          fill="rgb(76,224,224)"
          initial={{
            cx: state.knowledgeNodes.find((n) => n.id === activeFrom)!.x,
            cy: state.knowledgeNodes.find((n) => n.id === activeFrom)!.y,
          }}
          animate={{
            cx: state.knowledgeNodes.find((n) => n.id === activeTo)!.x,
            cy: state.knowledgeNodes.find((n) => n.id === activeTo)!.y,
          }}
          transition={{ duration: 1.4, ease: "easeInOut" }}
          style={{ filter: "drop-shadow(0 0 4px rgba(76,224,224,0.9))" }}
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
                opacity={dim ? 0.2 : 0.9}
                style={{ transition: "r 0.15s ease, opacity 0.15s ease" }}
              />
              <text
                x={n.x}
                y={n.y - 11}
                textAnchor="middle"
                fontSize="8.5"
                fill={dim ? "rgba(231,236,243,0.25)" : "rgba(231,236,243,0.85)"}
                fontFamily="var(--font-mono)"
              >
                {n.label}
              </text>
            </g>
          );
        })}
      </svg>

      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-wide text-ink-faint">
        {Object.entries(GROUP_COLOR).map(([group, color]) => (
          <span key={group} className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
            {group}
          </span>
        ))}
      </div>
    </div>
  );
}
