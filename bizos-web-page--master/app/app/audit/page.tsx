"use client";

import { motion } from "framer-motion";
import { Activity, Clock } from "lucide-react";

import { useBusiness } from "@/lib/business-context";
import { NewAccountPage } from "@/components/NewAccountPage";

export default function AuditLayer() {
  const { isPrimaryAccount } = useBusiness();

  if (!isPrimaryAccount) {
    return <NewAccountPage />;
  }
  return (
    <main className="pl-24 pr-8 py-8 w-full min-h-screen flex items-center justify-center relative z-10">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel p-12 flex flex-col items-center text-center max-w-lg"
      >
        <div className="w-16 h-16 rounded-full bg-primary/5 flex items-center justify-center mb-6">
          <Activity className="w-8 h-8 text-accent" />
        </div>
        <h1 className="font-display text-3xl mb-4 text-primary">Agent Audit Stream</h1>
        <p className="font-body text-secondary mb-8">
          Real-time execution logs, decision traces, and historical replay for agent swarms are initializing. The live telemetry stream will be available soon.
        </p>
        
        <div className="flex items-center gap-2 px-4 py-2 rounded-full border border-[color:var(--border-color)] bg-primary/5">
          <Clock className="w-4 h-4 text-secondary" />
          <span className="font-mono text-xs uppercase tracking-widest text-secondary">Coming Soon</span>
        </div>
      </motion.div>
    </main>
  );
}
