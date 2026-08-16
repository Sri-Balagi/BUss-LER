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

    // faint static backdrop stars for atmosphere
    ctx.fillStyle = "rgba(231,236,243,0.12)";
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
      const alpha = Math.max(0.25, 1 - age / 40);
      const color = ev.kind === "write" ? "76,224,224" : "139,92,246";
      const isHovered = hovered === ev.id;

      ctx.beginPath();
      ctx.arc(ev.x, ev.y, isHovered ? 5 : 3, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color},${alpha})`;
      ctx.shadowColor = `rgba(${color},0.8)`;
      ctx.shadowBlur = isHovered ? 14 : 8;
      ctx.fill();
      ctx.shadowBlur = 0;
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
    <div className="glass-panel relative p-7">
      <p className="eyebrow mb-2">Memory Galaxy · live</p>
      <h2 className="mb-4 font-display text-[19px] font-medium text-ink">Recent activity</h2>

      <div className="relative">
        <canvas
          ref={canvasRef}
          style={{ width: WIDTH, height: HEIGHT }}
          onMouseMove={handleMove}
          onMouseLeave={() => setHovered(null)}
          className="w-full cursor-crosshair rounded-lg"
        />
        {hoveredEvent && (
          <div
            className="pointer-events-none absolute z-10 max-w-[180px] -translate-x-1/2 -translate-y-full rounded-lg border border-white/10 bg-panel px-3 py-2 text-[11.5px] text-ink shadow-panel"
            style={{ left: hoveredEvent.x, top: hoveredEvent.y - 10 }}
          >
            <span className="block font-mono text-[9.5px] uppercase tracking-wide text-ink-faint">
              {hoveredEvent.kind}
            </span>
            {hoveredEvent.label}
          </div>
        )}
      </div>
      <p className="mt-3 font-mono text-[10.5px] text-ink-faint">
        cyan = written · violet = retrieved · hover a star for detail
      </p>
    </div>
  );
}
