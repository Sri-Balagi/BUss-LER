"use client";

import { motion } from "framer-motion";
import { Layers, Network, CheckCircle2, ChevronRight } from "lucide-react";

export default function DecisionLayer() {
  return (
    <main className="pl-24 pr-8 py-8 w-full min-h-screen flex flex-col gap-8 bg-deep-space">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex justify-between items-end"
      >
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Layers className="w-8 h-8 text-cognition-decision" />
            <h1 className="font-display text-4xl text-primary">Decision Engine</h1>
          </div>
          <p className="font-mono text-sm tracking-widest uppercase text-cognition-decision ml-11">
            Reasoning & Approvals
          </p>
        </div>

        <div className="glass-panel px-6 py-3 flex items-center gap-4">
          <span className="eyebrow">Engine Status</span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-cognition-decision animate-pulse-slow " />
            <span className="font-mono text-sm text-primary">Optimal</span>
          </div>
        </div>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6 flex-1">
        {/* Reasoning Tree */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="col-span-2 glass-panel p-6 flex flex-col"
        >
          <h3 className="eyebrow mb-6">Active Reasoning Tree</h3>
          <div className="flex-1 border border-white/5 rounded-xl bg-black/20 p-6 flex flex-col justify-center gap-8">
            <ReasoningNode 
              title="Evaluate Infrastructure Scale" 
              confidence={85} 
              active 
            />
            <div className="w-px h-8 bg-gradient-to-b from-cognition-decision to-white/10 ml-[150px]" />
            <div className="flex gap-16 ml-8">
              <ReasoningNode 
                title="Historical Traffic Analysis" 
                confidence={92} 
                source="Memory Layer" 
              />
              <ReasoningNode 
                title="Current CPU Saturation" 
                confidence={99} 
                source="Metrics Core" 
              />
            </div>
          </div>
        </motion.div>

        {/* Confidence & Approvals */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="glass-panel p-6 flex flex-col gap-8"
        >
          <div>
            <h3 className="eyebrow mb-6">Execution Confidence</h3>
            <div className="flex items-end gap-4 mb-2">
              <span className="font-display text-6xl text-cognition-decision ">97%</span>
              <span className="font-mono text-sm text-secondary pb-2">/ 100</span>
            </div>
            <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-cognition-decision"
                initial={{ width: 0 }}
                animate={{ width: "97%" }}
                transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
              />
            </div>
          </div>

          <div>
            <h3 className="eyebrow mb-4">Approval History</h3>
            <div className="space-y-4">
              <ApprovalItem action="Scale Redis Cluster" time="2m ago" />
              <ApprovalItem action="Purge Edge Cache" time="15m ago" />
              <ApprovalItem action="Rotate Auth Keys" time="1h ago" />
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}

function ReasoningNode({ title, confidence, source, active }: any) {
  return (
    <div className={`relative p-4 rounded-xl border ${active ? 'border-cognition-decision bg-cognition-decision/10 ' : 'border-white/10 bg-white/5'} flex flex-col gap-2 w-[300px]`}>
      <div className="flex justify-between items-start">
        <span className="font-medium text-sm text-primary">{title}</span>
        <span className={`font-mono text-xs ${active ? 'text-cognition-decision' : 'text-secondary'}`}>{confidence}%</span>
      </div>
      {source && (
        <div className="flex items-center gap-1 text-tertiary">
          <Network className="w-3 h-3" />
          <span className="font-mono text-[10px] uppercase tracking-wider">{source}</span>
        </div>
      )}
    </div>
  );
}

function ApprovalItem({ action, time }: any) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-colors cursor-pointer group">
      <div className="flex items-center gap-3">
        <CheckCircle2 className="w-4 h-4 text-cognition-decision" />
        <span className="font-mono text-xs text-primary">{action}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="font-mono text-[10px] text-tertiary">{time}</span>
        <ChevronRight className="w-3 h-3 text-tertiary group-hover:text-primary transition-colors" />
      </div>
    </div>
  );
}
