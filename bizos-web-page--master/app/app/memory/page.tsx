"use client";

import { MemoryGalaxyVisualizer } from "@/components/memory-galaxy";
import { motion } from "framer-motion";
import { Search } from "lucide-react";

export default function MemoryLayer() {
  return (
    <main className="w-full min-h-screen relative bg-deep-space overflow-hidden">
      <MemoryGalaxyVisualizer />
      
      {/* Overlay UI */}
      <div className="absolute inset-0 pointer-events-none p-8 pl-24 flex flex-col justify-between z-10">
        
        {/* Header */}
        <motion.div 
          className="pointer-events-auto"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="font-display text-4xl mb-2 text-primary">Memory Layer</h1>
          <p className="font-mono text-sm tracking-widest uppercase text-cognition-memory">
            Navigating Semantic Space
          </p>
        </motion.div>

        {/* Search / Command */}
        <motion.div 
          className="pointer-events-auto w-[400px]"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="glass-panel p-4 flex flex-col gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-tertiary" />
              <input 
                type="text" 
                placeholder="Query semantic index..." 
                className="w-full bg-black/20 border border-white/5 rounded-lg py-2 pl-10 pr-4 text-sm font-mono text-primary placeholder:text-tertiary focus:outline-none focus:border-cognition-memory transition-colors"
              />
            </div>
            
            <div className="space-y-2">
              <h3 className="eyebrow">Recent Retrievals</h3>
              <div className="flex flex-col gap-2">
                <RetrievalItem text="Enterprise SSO Architecture v2" />
                <RetrievalItem text="Kubernetes scaling policies" />
                <RetrievalItem text="User interaction history [Q3]" />
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}

function RetrievalItem({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 group cursor-pointer">
      <div className="w-1.5 h-1.5 rounded-full bg-cognition-memory/30 group-hover:bg-cognition-memory group-hover: transition-all" />
      <span className="font-mono text-xs text-secondary group-hover:text-primary transition-colors truncate">
        {text}
      </span>
    </div>
  );
}
