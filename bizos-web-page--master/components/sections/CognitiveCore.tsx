"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

// Configuration
const COLORS = {
  memory: "76, 224, 224",    // Cyan
  knowledge: "139, 92, 246", // Violet
  reasoning: "237, 125, 39", // Orange (Accent)
  goal: "52, 211, 153",      // Emerald
  agent: "255, 255, 255",    // White
};

type Node = {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  type: "memory" | "knowledge" | "goal";
  radius: number;
  pulse?: number;
  connections: number[]; // IDs of connected nodes
};

type Bridge = {
  from: number;
  to: number;
  life: number; // 1.0 down to 0
  maxLife: number;
};

type Agent = {
  from: number;
  to: number;
  progress: number;
  speed: number;
};

export function CognitiveCore() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth * window.devicePixelRatio;
        canvas.height = parent.clientHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }
    };
    resize();
    window.addEventListener("resize", resize);

    // State
    const nodes: Node[] = [];
    const bridges: Bridge[] = [];
    const agents: Agent[] = [];
    let frame = 0;
    
    // Initialize Nodes
    const w = canvas.width / window.devicePixelRatio;
    const h = canvas.height / window.devicePixelRatio;

    // Knowledge (stable, central-ish network)
    for (let i = 0; i < 15; i++) {
      nodes.push({
        id: nodes.length,
        x: w * 0.3 + Math.random() * w * 0.4,
        y: h * 0.3 + Math.random() * h * 0.4,
        vx: (Math.random() - 0.5) * 0.1,
        vy: (Math.random() - 0.5) * 0.1,
        type: "knowledge",
        radius: 3,
        connections: [],
      });
    }

    // Memory (drifting, clustering around edges)
    for (let i = 0; i < 30; i++) {
      nodes.push({
        id: nodes.length,
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        type: "memory",
        radius: 2,
        connections: [],
      });
    }

    // Goals (fixed, pulsing)
    for (let i = 0; i < 3; i++) {
      nodes.push({
        id: nodes.length,
        x: w * 0.8 + (Math.random() - 0.5) * 100,
        y: h * 0.2 + (Math.random() - 0.5) * 100,
        vx: 0,
        vy: 0,
        type: "goal",
        radius: 6,
        pulse: Math.random() * Math.PI * 2,
        connections: [],
      });
    }

    // Connect Knowledge rigidly
    const kNodes = nodes.filter(n => n.type === "knowledge");
    for (let i = 0; i < kNodes.length; i++) {
      for (let j = i + 1; j < kNodes.length; j++) {
        const dx = kNodes[i].x - kNodes[j].x;
        const dy = kNodes[i].y - kNodes[j].y;
        if (Math.sqrt(dx * dx + dy * dy) < 150) {
          kNodes[i].connections.push(kNodes[j].id);
        }
      }
    }

    let rafId: number;
    const render = () => {
      frame++;
      const currentW = canvas.width / window.devicePixelRatio;
      const currentH = canvas.height / window.devicePixelRatio;

      ctx.clearRect(0, 0, currentW, currentH);

      // Update & Draw Nodes
      nodes.forEach(n => {
        if (n.type === "memory") {
          n.x += n.vx;
          n.y += n.vy;
          // Boundary bounce
          if (n.x < 0 || n.x > currentW) n.vx *= -1;
          if (n.y < 0 || n.y > currentH) n.vy *= -1;
          
          // Gentle clustering behavior (move towards center slowly)
          n.vx += (currentW/2 - n.x) * 0.00001;
          n.vy += (currentH/2 - n.y) * 0.00001;
        } else if (n.type === "knowledge") {
          n.x += n.vx;
          n.y += n.vy;
          // Soft boundary
          if (n.x < currentW * 0.2 || n.x > currentW * 0.8) n.vx *= -1;
          if (n.y < currentH * 0.2 || n.y > currentH * 0.8) n.vy *= -1;
        } else if (n.type === "goal") {
          n.pulse! += 0.05;
        }

        ctx.beginPath();
        let currentRadius = n.radius;
        if (n.type === "goal") {
          currentRadius += Math.sin(n.pulse!) * 2;
          ctx.shadowBlur = 15 + Math.sin(n.pulse!) * 10;
          ctx.shadowColor = `rgba(${COLORS.goal}, 0.8)`;
        } else {
          ctx.shadowBlur = 5;
          ctx.shadowColor = `rgba(${COLORS[n.type]}, 0.5)`;
        }
        
        ctx.arc(n.x, n.y, Math.max(1, currentRadius), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${COLORS[n.type]}, 0.9)`;
        ctx.fill();
        ctx.shadowBlur = 0; // Reset
      });

      // Draw Knowledge network
      ctx.lineWidth = 1;
      kNodes.forEach(n => {
        n.connections.forEach(targetId => {
          const t = nodes[targetId];
          ctx.beginPath();
          ctx.moveTo(n.x, n.y);
          ctx.lineTo(t.x, t.y);
          ctx.strokeStyle = `rgba(${COLORS.knowledge}, 0.15)`;
          ctx.stroke();
        });
      });

      // Spawn temporary reasoning bridges
      if (Math.random() < 0.05) {
        const memoryNodes = nodes.filter(n => n.type === "memory");
        if (memoryNodes.length > 0 && kNodes.length > 0) {
          const m = memoryNodes[Math.floor(Math.random() * memoryNodes.length)];
          const k = kNodes[Math.floor(Math.random() * kNodes.length)];
          bridges.push({ from: m.id, to: k.id, life: 1, maxLife: 100 + Math.random() * 100 });
        }
      }
      
      // Spawn agents moving towards goals
      if (Math.random() < 0.02) {
        const goalNodes = nodes.filter(n => n.type === "goal");
        if (kNodes.length > 0 && goalNodes.length > 0) {
          const k = kNodes[Math.floor(Math.random() * kNodes.length)];
          const g = goalNodes[Math.floor(Math.random() * goalNodes.length)];
          agents.push({ from: k.id, to: g.id, progress: 0, speed: 0.005 + Math.random() * 0.01 });
          // Add a reasoning bridge to support the agent
          bridges.push({ from: k.id, to: g.id, life: 1, maxLife: 200 });
        }
      }

      // Update and Draw Reasoning Bridges
      for (let i = bridges.length - 1; i >= 0; i--) {
        const b = bridges[i];
        b.life -= 1 / b.maxLife;
        if (b.life <= 0) {
          bridges.splice(i, 1);
          continue;
        }
        const from = nodes[b.from];
        const to = nodes[b.to];
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.strokeStyle = `rgba(${COLORS.reasoning}, ${b.life * 0.4})`;
        ctx.stroke();
      }

      // Update and Draw Agents
      for (let i = agents.length - 1; i >= 0; i--) {
        const a = agents[i];
        a.progress += a.speed;
        
        const from = nodes[a.from];
        const to = nodes[a.to];
        
        if (a.progress >= 1) {
          // Execution flash!
          ctx.beginPath();
          ctx.arc(to.x, to.y, 15, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${COLORS.agent}, 0.8)`;
          ctx.fill();
          agents.splice(i, 1);
          continue;
        }

        const ax = from.x + (to.x - from.x) * a.progress;
        const ay = from.y + (to.y - from.y) * a.progress;

        ctx.beginPath();
        ctx.arc(ax, ay, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${COLORS.agent}, 1)`;
        ctx.shadowBlur = 10;
        ctx.shadowColor = `rgba(${COLORS.agent}, 1)`;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      rafId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <section className="relative mx-auto max-w-6xl px-6 py-28 border-t border-white/[0.04]">
      <div className="mb-12">
        <p className="eyebrow mb-4">See Intelligence In Motion</p>
        <h2 className="font-display text-[32px] md:text-[40px] font-medium leading-tight text-ink">
          The Cognitive Core.
        </h2>
      </div>

      <div className="relative w-full aspect-[4/3] md:aspect-[21/9] rounded-3xl glass-panel border border-white/[0.06] overflow-hidden bg-black/40">
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full"
          style={{ width: "100%", height: "100%" }}
        />
        
        {/* Overlay Legend */}
        <div className="absolute top-6 left-6 flex flex-col gap-3 pointer-events-none">
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-[#4CE0E0]" />
            <span className="font-mono text-[10px] uppercase tracking-widest text-white/50">Memory clusters</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-[#8B5CF6]" />
            <span className="font-mono text-[10px] uppercase tracking-widest text-white/50">Knowledge stabilization</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-[#ED7D27]" />
            <span className="font-mono text-[10px] uppercase tracking-widest text-white/50">Reasoning bridges</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-[#34D399]" />
            <span className="font-mono text-[10px] uppercase tracking-widest text-white/50">Active goals</span>
          </div>
        </div>
      </div>
    </section>
  );
}
