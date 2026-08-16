"use client";

import { useEffect, useRef, useState } from "react";
import { useCognitiveState } from "@/lib/dashboard/state";

const WIDTH = 300;
const HEIGHT = 230;

export default function MemoryActivity() {
  const state = useCognitiveState();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = WIDTH * dpr;
    canvas.height = HEIGHT * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    // Faint static backdrop stars for atmosphere
    ctx.fillStyle = "rgba(14,165,233,0.15)";
    for (let i = 0; i < 26; i++) {
      const x = (i * 37) % WIDTH;
      const y = (i * 53) % HEIGHT;
      ctx.beginPath();
      ctx.arc(x, y, 0.8, 0, Math.PI * 2);
      ctx.fill();
    }

    const now = Date.now();
    state.memoryEvents.forEach((ev) => {
      const age = (now - ev.ts) / 1000;
      const alpha = Math.max(0.3, 1 - age / 40);
      const color = ev.kind === "write" ? "14,165,233" : "139,92,246";
      const isHovered = hovered === ev.id;

      ctx.beginPath();
      ctx.arc(ev.x, ev.y, isHovered ? 5.5 : 3.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color},${alpha})`;
      ctx.fill();
    });
  }, [state.memoryEvents, hovered]);

  function handleMove(e: React.MouseEvent<HTMLCanvasElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    let closest: string | null = null;
    let closestD = 14;
    state.memoryEvents.forEach((ev) => {
      const d = Math.hypot(ev.x - x, ev.y - y);
      if (d < closestD) {
        closestD = d;
        closest = ev.id;
      }
    });
    setHovered(closest);
  }

  const hoveredEvent = state.memoryEvents.find((e) => e.id === hovered) ?? null;

  return (
    <div className="glass-card relative p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:border-[#38BDF8] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
      <p className="eyebrow mb-2 text-accent">Memory Galaxy · live</p>
      <h2 className="mb-4 font-display text-[20px] font-semibold text-ink tracking-tight">Recent activity</h2>

      <div className="relative">
        <canvas
          ref={canvasRef}
          style={{ width: WIDTH, height: HEIGHT }}
          onMouseMove={handleMove}
          onMouseLeave={() => setHovered(null)}
          className="w-full cursor-crosshair rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/60 dark:bg-zinc-950/60"
        />
        {hoveredEvent && (
          <div
            className="pointer-events-none absolute z-10 max-w-[180px] -translate-x-1/2 -translate-y-full rounded-xl border border-[#E2DAD0] dark:border-zinc-700 bg-white/95 dark:bg-zinc-900/95 px-3 py-2 text-[11.5px] text-ink shadow-lg backdrop-blur-md transition-all duration-150"
            style={{ left: hoveredEvent.x, top: hoveredEvent.y - 10 }}
          >
            <span className="block font-mono text-[9.5px] uppercase tracking-wide text-[#0EA5E9] font-bold">
              {hoveredEvent.kind}
            </span>
            <span className="font-medium">{hoveredEvent.label}</span>
          </div>
        )}
      </div>
      <p className="mt-3 font-mono text-[10.5px] text-ink-muted">
        cyan = written · violet = retrieved · hover a star for detail
      </p>
    </div>
  );
}
