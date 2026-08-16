"use client";

import { motion } from "framer-motion";
import { Shield, Lock, Eye, UserCheck, Server, Activity } from "lucide-react";

const TRUST_PILLARS = [
  {
    icon: Shield,
    title: "Privacy First",
    description: "Your business data is sandboxed, encrypted, and strictly isolated from public models.",
  },
  {
    icon: Lock,
    title: "Enterprise Security",
    description: "Role-based access controls and comprehensive audit logging built into the core.",
  },
  {
    icon: Eye,
    title: "Transparent Reasoning",
    description: "Every decision is traceable. Inspect the exact chain of thought that led to an outcome.",
  },
  {
    icon: UserCheck,
    title: "Human Oversight",
    description: "Configurable approval gates ensure humans authorize critical actions before execution.",
  },
  {
    icon: Server,
    title: "Scalable Architecture",
    description: "Designed to handle enterprise workloads seamlessly without degrading cognitive performance.",
  },
  {
    icon: Activity,
    title: "High Reliability",
    description: "Fault-tolerant agent orchestration ensures continuous operation even during complex workflows.",
  },
];

export function Trust() {
  return (
    <section className="relative mx-auto max-w-6xl px-6 py-28 border-t border-white/[0.04]">
      <div className="mb-16 text-center">
        <p className="eyebrow mb-4">Architecture of Trust</p>
        <h2 className="font-display text-[32px] md:text-[40px] font-medium leading-tight text-ink">
          Built for Confidence.
        </h2>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {TRUST_PILLARS.map((pillar, i) => (
          <motion.div
            key={pillar.title}
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.1, ease: "easeOut" }}
            className="glass-panel p-8"
          >
            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-white/[0.03] border border-white/[0.05]">
              <pillar.icon className="h-5 w-5 text-ink-muted" />
            </div>
            <h3 className="font-display text-[17px] font-medium text-ink mb-3">{pillar.title}</h3>
            <p className="text-[14px] leading-relaxed text-ink-muted">{pillar.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
