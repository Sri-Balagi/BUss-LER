"use client";

import { useState } from "react";
import { MemoryGalaxyVisualizer } from "@/components/memory-galaxy";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Brain, Clock, ChevronRight, X, Sparkles } from "lucide-react";

export default function MemoryLayer() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedItem, setSelectedItem] = useState<any>(null);

  const retrievals = [
    {
      id: "r1",
      title: "Aavin Milk & Ghee Procurement SLA",
      category: "Sourcing",
      timestamp: "1h ago",
      details: "Guaranteed 5:00 AM daily delivery of 150L fresh Aavin buffalo milk and 45kg pure cow ghee at ₹48/L with quality verification.",
    },
    {
      id: "r2",
      title: "South Indian Special Thali Recipe Standard",
      category: "Kitchen SOP",
      timestamp: "3h ago",
      details: "14-item thali portion specs: Sambar tamarind ratio 1:4, Appalam oil temp locked at 180°C, Payasam cashew roast 30s.",
    },
    {
      id: "r3",
      title: "Banquet Hall A Booking (Dr. Radhakrishnan — 65 Guests)",
      category: "Banquet Sales",
      timestamp: "5h ago",
      details: "65 Guests confirmed for Sunday 1:00 PM lunch. Mini Tiffin + Sweet combo with welcome Badam Milk.",
    },
    {
      id: "r4",
      title: "Table 12 VIP Guest Preference (Sundaram Family)",
      category: "Guest Desk",
      timestamp: "12m ago",
      details: "Requests extra ghee on Rava Dosa, zero green chili in Sambhar, and quiet corner seating in Hall A.",
    },
    {
      id: "r5",
      title: "Swiggy & Zomato POS Order Batching",
      category: "POS Gateway",
      timestamp: "1d ago",
      details: "Auto-compensation triggered if KDS ticket prep exceeds 25 minutes during Friday peak dinner surge.",
    },
  ];

  const filtered = retrievals.filter(
    (item) =>
      searchQuery === "" ||
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <main className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-all duration-200 ease-[0.16,1,0.3,1] relative overflow-hidden bg-[#FAF7F2] dark:bg-zinc-950">
      {/* 3D Obsidian Memory Graph Canvas (Fully Uncovered Center Stage) */}
      <MemoryGalaxyVisualizer
        onNodeClick={(node: any) =>
          setSelectedItem({
            title: node.label,
            category: node.category || "Memory Node",
            timestamp: "Realtime",
            details: `Connected 3D Memory Node: ${node.label}. Live synchronized across Hotel Balagi Bhavan operational graph.`,
          })
        }
      />

      {/* Overlay UI (Compact Top-Left & Bottom Cards) */}
      <div className="relative z-10 mx-auto max-w-[1440px] pointer-events-none space-y-7">
        {/* Page Header */}
        <motion.div
          className="pointer-events-auto"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-accent">
            BizOS / Memory
          </p>
          <h1 className="mt-1 font-display text-[24px] md:text-[28px] font-semibold tracking-tight text-ink">
            Memory Layer
          </h1>
          <p className="mt-1 font-mono text-[11.5px] uppercase tracking-widest text-[#ED7D27] font-medium">
            Hotel Balagi Bhavan Connected Semantic Graph
          </p>
        </motion.div>

        {/* Compact Floating Glass Command Card */}
        <motion.div
          className="pointer-events-auto w-full max-w-md"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <div className="glass-card p-6 flex flex-col gap-4 rounded-[28px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 shadow-[0_8px_32px_rgba(0,0,0,0.06)] backdrop-blur-xl hover:border-[#ED7D27] transition-all">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#ED7D27]" strokeWidth={1.75} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Query Hotel Balagi Bhavan index..."
                className="w-full bg-white/90 dark:bg-zinc-800/90 border border-[#E2DAD0] dark:border-zinc-700 rounded-xl py-2.5 pl-10 pr-4 text-sm font-mono text-ink placeholder:text-ink-muted focus:outline-none focus:border-[#ED7D27] focus-visible:ring-2 focus-visible:ring-[#ED7D27]/50 transition-colors"
              />
            </div>

            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <h3 className="eyebrow text-accent font-mono text-[11px] font-medium uppercase tracking-[0.18em]">
                  Recent Retrievals
                </h3>
                <span className="font-mono text-[10.5px] text-[#ED7D27] font-bold">
                  {filtered.length} Indexed
                </span>
              </div>

              <div className="flex flex-col gap-1.5 max-h-[220px] overflow-y-auto pr-1">
                {filtered.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    className="flex items-center justify-between gap-3 group cursor-pointer p-2.5 rounded-xl hover:bg-white/90 dark:hover:bg-zinc-800/80 active:scale-[0.98] transition-all duration-200 border border-transparent hover:border-[#E2DAD0] dark:hover:border-zinc-700"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#ED7D27] group-hover:scale-125 transition-transform shrink-0" />
                      <span className="font-mono text-xs text-ink-muted group-hover:text-ink font-semibold truncate">
                        {item.title}
                      </span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-ink-muted group-hover:text-[#ED7D27] shrink-0 transition-colors" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Floating Bottom Status Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 glass-card px-6 py-2.5 rounded-full border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 backdrop-blur-xl shadow-lg flex items-center gap-4 z-20 pointer-events-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#ED7D27] opacity-75" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#ED7D27]" />
        </span>
        <span className="font-mono text-xs tracking-widest text-ink font-bold uppercase">
          Obsidian Memory Links Active
        </span>
        <span className="font-mono text-xs text-ink-muted">|</span>
        <span className="font-mono text-xs text-ink-muted font-medium">Scroll to traverse 3D nodes</span>
      </motion.div>

      {/* Memory Detail Modal */}
      <AnimatePresence>
        {selectedItem && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm pointer-events-auto">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="glass-card p-7 rounded-[32px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2] dark:bg-zinc-900 shadow-2xl max-w-md w-full space-y-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span className="font-mono text-[10.5px] font-bold uppercase tracking-wider px-3 py-1 rounded-full border border-[#ED7D27]/30 text-[#ED7D27] bg-[#ED7D27]/10">
                    {selectedItem.category}
                  </span>
                  <h3 className="font-display text-lg font-semibold text-ink mt-3 leading-snug">
                    {selectedItem.title}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedItem(null)}
                  className="p-2 rounded-xl hover:bg-black/5 dark:hover:bg-white/10 text-ink-muted hover:text-ink transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <p className="font-mono text-xs text-ink leading-relaxed p-4 rounded-2xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/80 dark:bg-zinc-800/50 font-medium">
                {selectedItem.details}
              </p>

              <div className="flex items-center justify-between font-mono text-xs text-ink-muted pt-2">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-[#ED7D27]" />
                  Recorded {selectedItem.timestamp}
                </span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400 uppercase">
                  Verified Record
                </span>
              </div>

              <button
                onClick={() => setSelectedItem(null)}
                className="w-full py-2.5 rounded-xl bg-[#ED7D27] hover:bg-[#ED7D27]/90 text-white font-mono text-xs font-bold transition-colors shadow-sm mt-2"
              >
                Close Record
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </main>
  );
}
