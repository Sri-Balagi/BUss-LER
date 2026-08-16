"use client";

import { motion } from "framer-motion";
import { useCognitiveState } from "@/lib/dashboard/state";

function RadialGauge({
  value,
  label,
  sub,
  color,
}: {
  value: number; // 0-1
  label: string;
  sub: string;
  color: string;
}) {
  const size = 84;
  const stroke = 6;
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="currentColor"
            className="text-[#E2DAD0] dark:text-zinc-800"
            strokeWidth={stroke}
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            animate={{ strokeDashoffset: circumference * (1 - value) }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-[13px] text-ink font-bold">{Math.round(value * 100)}%</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-[12.5px] text-ink font-semibold">{label}</p>
        <p className="font-mono text-[10.5px] text-ink-muted">{sub}</p>
      </div>
    </div>
  );
}

export default function InfrastructureHealth() {
  const { infra } = useCognitiveState();
  const workerLoad = infra.workers / infra.maxWorkers;

  return (
    <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <p className="eyebrow mb-2 text-accent">Infrastructure · live</p>
      <h2 className="mb-6 font-display text-[20px] font-semibold text-ink tracking-tight">System health</h2>

      <div className="grid grid-cols-2 gap-y-6">
        <RadialGauge value={infra.cpu} label="CPU" sub="cluster avg" color="#38BDF8" />
        <RadialGauge value={infra.memory} label="Memory" sub="cluster avg" color="#8B5CF6" />
        <RadialGauge
          value={workerLoad}
          label="Workers"
          sub={`${infra.workers} / ${infra.maxWorkers}`}
          color="#10B981"
        />
        <div className="flex flex-col items-center justify-center gap-2">
          <span className="font-display text-[30px] font-bold text-ink">
            {infra.queueDepth}
          </span>
          <div className="text-center">
            <p className="text-[12.5px] text-ink font-semibold">Queue depth</p>
            <p className="font-mono text-[10.5px] text-ink-muted">pending tasks</p>
          </div>
        </div>
      </div>
    </div>
  );
}
