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
            stroke="rgba(255,255,255,0.06)"
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
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-[13px] text-ink">{Math.round(value * 100)}%</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-[12px] text-ink">{label}</p>
        <p className="font-mono text-[10.5px] text-ink-faint">{sub}</p>
      </div>
    </div>
  );
}

export default function InfrastructureHealth() {
  const { infra } = useCognitiveState();
  const workerLoad = infra.workers / infra.maxWorkers;

  return (
    <div className="glass-panel p-7">
      <p className="eyebrow mb-2">Infrastructure · live</p>
      <h2 className="mb-6 font-display text-[19px] font-medium text-ink">System health</h2>

      <div className="grid grid-cols-2 gap-y-6">
        <RadialGauge value={infra.cpu} label="CPU" sub="cluster avg" color="rgb(47,111,255)" />
        <RadialGauge value={infra.memory} label="Memory" sub="cluster avg" color="rgb(139,92,246)" />
        <RadialGauge
          value={workerLoad}
          label="Workers"
          sub={`${infra.workers} / ${infra.maxWorkers}`}
          color="rgb(52,211,153)"
        />
        <div className="flex flex-col items-center justify-center gap-2">
          <span className="font-display text-[30px] font-medium text-ink">
            {infra.queueDepth}
          </span>
          <div className="text-center">
            <p className="text-[12px] text-ink">Queue depth</p>
            <p className="font-mono text-[10.5px] text-ink-faint">pending tasks</p>
          </div>
        </div>
      </div>
    </div>
  );
}
