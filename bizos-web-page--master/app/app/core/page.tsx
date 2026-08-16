"use client";

import { motion } from "framer-motion";
import { Activity, Brain, Server, Shield, Zap } from "lucide-react";

export default function CoreDashboard() {
  return (
    <main className="pl-24 pr-8 py-8 w-full min-h-screen flex gap-8">
      {/* Left Column: AI Status Ring & Insights */}
      <div className="w-[300px] flex flex-col gap-6">
        <h1 className="font-display text-4xl mb-2">Core Runtime</h1>
        
        {/* Cognitive Core (Status Ring) */}
        <motion.div 
          className="glass-panel p-6 flex flex-col items-center gap-6"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.05 }}
        >
          <div className="relative w-48 h-48 flex items-center justify-center">
            {/* Ambient Pulsing Rings */}
            <motion.div 
              className="absolute inset-0 rounded-full border border-cognition-thought opacity-20"
              animate={{ scale: [1, 1.2, 1], opacity: [0.2, 0, 0.2] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div 
              className="absolute inset-2 rounded-full border border-cognition-decision opacity-30"
              animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.1, 0.3] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            />
            <svg className="w-full h-full -rotate-90">
              <circle cx="96" cy="96" r="88" fill="none" stroke="currentColor" strokeWidth="2" className="text-white/5" />
              <circle cx="96" cy="96" r="88" fill="none" stroke="currentColor" strokeWidth="4" strokeDasharray="553" strokeDashoffset="120" className="text-cognition-thought " />
            </svg>
            <div className="absolute text-center">
              <span className="block font-mono text-3xl text-primary font-bold">98%</span>
              <span className="block font-mono text-[10px] uppercase tracking-widest text-secondary mt-1">Efficiency</span>
            </div>
          </div>
          
          <div className="w-full space-y-3">
            <StatusRow icon={Brain} label="Cognitive" value="Optimal" color="thought" />
            <StatusRow icon={Server} label="Memory" value="Syncing" color="memory" />
            <StatusRow icon={Zap} label="Decision" value="Active" color="decision" />
            <StatusRow icon={Shield} label="Security" value="Secured" color="thought" />
          </div>
        </motion.div>
      </div>

      {/* Center Column: Live Cognitive Visualization */}
      <motion.div 
        className="flex-1 glass-panel relative overflow-hidden flex items-center justify-center"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(0,240,255,0.05)_0%,transparent_70%)] pointer-events-none" />
        <div className="text-center">
          <Brain className="w-16 h-16 text-cognition-thought mx-auto mb-4 animate-breathe " />
          <h2 className="font-display text-2xl mb-2">Cognitive Network Idle</h2>
          <p className="text-secondary font-mono text-sm uppercase tracking-widest">Awaiting Workflow Execution</p>
        </div>
      </motion.div>

      {/* Right Column: ThoughtStream (Timeline) */}
      <motion.div 
        className="w-[340px] glass-panel p-6 flex flex-col"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.15 }}
      >
        <h3 className="eyebrow mb-6">Cognitive Timeline</h3>
        <div className="flex-1 overflow-y-auto space-y-6 relative before:absolute before:inset-y-0 before:left-3 before:w-px before:bg-white/10">
          <TimelineEvent time="22:14:03" action="Execution Complete" state="decision" />
          <TimelineEvent time="22:14:01" action="Decision Generated" state="decision" detail="Confidence: 99.2%" />
          <TimelineEvent time="22:13:58" action="Reasoning Reached" state="thought" />
          <TimelineEvent time="22:13:54" action="Knowledge Retrieved" state="knowledge" detail="12 semantic clusters found" />
          <TimelineEvent time="22:13:50" action="Memory Accessed" state="memory" />
          <TimelineEvent time="22:13:48" action="Workflow Initiated" state="thought" />
        </div>
      </motion.div>
    </main>
  );
}

function StatusRow({ icon: Icon, label, value, color }: any) {
  return (
    <div className="flex items-center justify-between font-mono text-xs">
      <div className="flex items-center gap-2 text-secondary">
        <Icon className="w-4 h-4" />
        <span className="uppercase tracking-wider">{label}</span>
      </div>
      <span className={`text-cognition-${color} font-bold tracking-wider`}>{value}</span>
    </div>
  );
}

function TimelineEvent({ time, action, state, detail }: any) {
  return (
    <div className="relative pl-8">
      <div className={`absolute left-[9px] top-1.5 w-2 h-2 rounded-full bg-cognition-${state} `} />
      <div className="font-mono text-[10px] text-tertiary mb-1">{time}</div>
      <div className="text-sm font-medium text-primary">{action}</div>
      {detail && <div className="text-xs text-secondary mt-1">{detail}</div>}
    </div>
  );
}
