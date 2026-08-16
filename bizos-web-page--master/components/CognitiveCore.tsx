"use client";

import { useEffect, useRef } from "react";

// The Cognitive Core is BizOS's signature visual: a sphere of nodes
// representing distributed reasoning. Signal pulses travel along the
// connections in the four subsystem colors (thinking / memory / knowledge
// / decision), so the shape itself narrates what the product does.

type Node3D = {
  x: number;
  y: number;
  z: number;
  connections: number[];
};

const SUBSYSTEM_COLORS = ["47,111,255", "76,224,224", "139,92,246", "52,211,153"];

function buildSphere(count: number): Node3D[] {
  const nodes: Node3D[] = [];
  const golden = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < count; i++) {
    const y = 1 - (i / (count - 1)) * 2;
    const radius = Math.sqrt(1 - y * y);
    const theta = golden * i;
    nodes.push({
      x: Math.cos(theta) * radius,
      y,
      z: Math.sin(theta) * radius,
      connections: [],
    });
  }
  // Connect each node to its ~3 nearest neighbours for a clean neural mesh
  for (let i = 0; i < nodes.length; i++) {
    const dists = nodes
      .map((n, j) => ({ j, d: i === j ? Infinity : dist(nodes[i], n) }))
      .sort((a, b) => a.d - b.d)
      .slice(0, 3);
    nodes[i].connections = dists.map((d) => d.j);
  }
  return nodes;
}

function dist(a: Node3D, b: Node3D) {
  return Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
}

export default function CognitiveCore({ size = 480 }: { size?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.scale(dpr, dpr);

    const nodes = buildSphere(46);
    const pulses: { from: number; to: number; t: number; color: string }[] = [];

    let angle = 0;
    let frame = 0;
    let raf = 0;
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function spawnPulse() {
      const from = Math.floor(Math.random() * nodes.length);
      const to = nodes[from].connections[Math.floor(Math.random() * nodes[from].connections.length)];
      const color = SUBSYSTEM_COLORS[Math.floor(Math.random() * SUBSYSTEM_COLORS.length)];
      pulses.push({ from, to, t: 0, color });
    }

    function render() {
      if (!ctx) return;
      frame++;
      angle += prefersReduced ? 0 : 0.0022;
      if (!prefersReduced && frame % 26 === 0 && pulses.length < 10) spawnPulse();

      ctx.clearRect(0, 0, size, size);

      const cx = size / 2;
      const cy = size / 2;
      const scale = size * 0.34;

      const projected = nodes.map((n) => {
        const cosA = Math.cos(angle);
        const sinA = Math.sin(angle);
        const x = n.x * cosA - n.z * sinA;
        const z = n.x * sinA + n.z * cosA;
        const y = n.y;
        const perspective = 1 / (1.8 - z * 0.6);
        return {
          x: cx + x * scale * perspective,
          y: cy + y * scale * perspective,
          z,
          perspective,
        };
      });

      // connections
      ctx.lineWidth = 1;
      nodes.forEach((n, i) => {
        n.connections.forEach((j) => {
          if (j < i) return;
          const a = projected[i];
          const b = projected[j];
          const depth = (a.z + b.z) / 2;
          const alpha = 0.05 + Math.max(0, depth) * 0.12;
          ctx.strokeStyle = `rgba(120,140,170,${alpha})`;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        });
      });

      // traveling pulses
      for (let i = pulses.length - 1; i >= 0; i--) {
        const p = pulses[i];
        p.t += prefersReduced ? 1 : 0.028;
        if (p.t >= 1) {
          pulses.splice(i, 1);
          continue;
        }
        const a = projected[p.from];
        const b = projected[p.to];
        const x = a.x + (b.x - a.x) * p.t;
        const y = a.y + (b.y - a.y) * p.t;
        const glowAlpha = Math.sin(p.t * Math.PI);
        ctx.beginPath();
        ctx.arc(x, y, 3.2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color},${0.9 * glowAlpha})`;
        ctx.shadowColor = `rgba(${p.color},0.9)`;
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // nodes
      projected.forEach((p) => {
        const r = 1.6 + p.perspective * 1.4;
        const alpha = 0.35 + Math.max(0, p.z) * 0.5;
        ctx.beginPath();
        ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(231,236,243,${alpha})`;
        ctx.fill();
      });

      raf = requestAnimationFrame(render);
    }

    render();
    return () => cancelAnimationFrame(raf);
  }, [size]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: size, height: size }}
      aria-hidden="true"
      className="pointer-events-none"
    />
  );
}
