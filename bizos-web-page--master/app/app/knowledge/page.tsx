"use client";

import { KnowledgeUniverseVisualizer } from "@/components/knowledge-universe";
import { motion } from "framer-motion";
import { Hexagon } from "lucide-react";

import { useBusiness } from "@/lib/business-context";
import { NewAccountPage } from "@/components/NewAccountPage";

export default function KnowledgeLayer() {
  const { isPrimaryAccount } = useBusiness();

  if (!isPrimaryAccount) {
    return <NewAccountPage />;
  }
  return (
    <main className="w-full min-h-screen relative bg-deep-space overflow-hidden">
      <KnowledgeUniverseVisualizer />
      
      {/* Overlay UI */}
      <div className="absolute inset-0 pointer-events-none p-8 pl-24 flex flex-col justify-between z-10">
        
        {/* Header */}
        <motion.div 
          className="pointer-events-auto"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <Hexagon className="w-8 h-8 text-cognition-knowledge" />
            <h1 className="font-display text-4xl text-primary">Knowledge Layer</h1>
          </div>
          <p className="font-mono text-sm tracking-widest uppercase text-cognition-knowledge ml-11">
            Semantic Entity Graph
          </p>
        </motion.div>

        {/* Legend */}
        <motion.div 
          className="pointer-events-auto w-[300px] self-end"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="glass-panel p-4 flex flex-col gap-3">
            <h3 className="eyebrow">Graph Status</h3>
            <div className="flex justify-between items-center text-sm font-mono">
              <span className="text-secondary">Nodes Active</span>
              <span className="text-primary font-bold">1,024</span>
            </div>
            <div className="flex justify-between items-center text-sm font-mono">
              <span className="text-secondary">Relationships</span>
              <span className="text-primary font-bold">4,592</span>
            </div>
            <div className="flex justify-between items-center text-sm font-mono">
              <span className="text-secondary">Sync State</span>
              <span className="text-cognition-knowledge">Realtime</span>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
