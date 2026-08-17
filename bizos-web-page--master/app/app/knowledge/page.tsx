"use client";

import { KnowledgeUniverseVisualizer } from "@/components/knowledge-universe";
import { motion } from "framer-motion";
import { Hexagon, UtensilsCrossed, Users, BookOpen, Truck, Star, CalendarDays, ChefHat } from "lucide-react";
import { useState } from "react";

const ENTITY_CATEGORIES = [
  { icon: UtensilsCrossed, label: "Menu Items",          count: 89,  color: "#ED7D27", bg: "rgba(237,125,39,0.12)" },
  { icon: Users,           label: "Regular Customers",   count: 64,  color: "#10B981", bg: "rgba(16,185,129,0.12)" },
  { icon: BookOpen,        label: "Recipes & Ingredients", count: 73, color: "#38BDF8", bg: "rgba(56,189,248,0.12)" },
  { icon: ChefHat,         label: "Staff & Roles",       count: 28,  color: "#A78BFA", bg: "rgba(167,139,250,0.12)" },
  { icon: Truck,           label: "Vendors & Suppliers", count: 22,  color: "#F87171", bg: "rgba(248,113,113,0.12)" },
  { icon: Star,            label: "Seasonal Specials",   count: 16,  color: "#FBBF24", bg: "rgba(251,191,36,0.12)" },
  { icon: CalendarDays,    label: "Bookings & Events",   count: 20,  color: "#2DD4BF", bg: "rgba(45,212,191,0.12)" },
];

const RECENT_LINKS = [
  { from: "Chicken Biryani", to: "Basmati Rice (Vendor: Srinivas Traders)", strength: 98 },
  { from: "Rajesh Kumar (Regular)", to: "Table 4 — Window Seat Preference", strength: 94 },
  { from: "Dal Makhani", to: "Allergen: Dairy, Gluten", strength: 100 },
  { from: "Ganesh Chaturthi", to: "Increased Puja Thali Demand", strength: 87 },
  { from: "Chef Venkatesh", to: "Chettinad Specials Expertise", strength: 92 },
];

export default function KnowledgeLayer() {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  return (
    <main className="w-full min-h-screen relative bg-deep-space overflow-hidden">
      <KnowledgeUniverseVisualizer />

      {/* Overlay UI */}
      <div className="absolute inset-0 pointer-events-none p-6 pl-24 flex flex-col justify-between z-10">

        {/* Header */}
        <motion.div
          className="pointer-events-auto"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="flex items-center gap-3 mb-1">
            <Hexagon className="w-8 h-8" style={{ color: "#ED7D27" }} />
            <h1 className="font-display text-4xl text-primary">Knowledge Layer</h1>
          </div>
          <p className="font-mono text-sm tracking-widest uppercase ml-11" style={{ color: "#ED7D27" }}>
            Hotel Balagi Bhavan — Semantic Entity Graph
          </p>
          <div className="ml-11 mt-2 flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-75" style={{ background: "#ED7D27" }} />
              <span className="relative inline-flex h-2 w-2 rounded-full" style={{ background: "#ED7D27" }} />
            </span>
            <span className="font-mono text-xs text-secondary uppercase tracking-widest">Live Graph · 312 nodes · 1,847 relationships</span>
          </div>
        </motion.div>

        {/* Right Side Panels */}
        <div className="pointer-events-auto self-end flex flex-col gap-4 w-[300px]">

          {/* Entity Categories */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.05 }}
          >
            <div className="glass-panel p-4 flex flex-col gap-2 rounded-2xl">
              <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-secondary mb-1">Entity Categories</h3>
              {ENTITY_CATEGORIES.map(({ icon: Icon, label, count, color, bg }) => (
                <button
                  key={label}
                  onClick={() => setActiveCategory(activeCategory === label ? null : label)}
                  className="flex items-center justify-between w-full px-3 py-2 rounded-xl transition-all duration-200 hover:scale-[1.02]"
                  style={{
                    background: activeCategory === label ? bg : "rgba(255,255,255,0.04)",
                    border: `1px solid ${activeCategory === label ? color : "rgba(255,255,255,0.08)"}`,
                  }}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-3.5 h-3.5" style={{ color }} strokeWidth={1.75} />
                    <span className="font-mono text-[11px] text-primary">{label}</span>
                  </div>
                  <span className="font-mono text-[11px] font-bold" style={{ color }}>{count}</span>
                </button>
              ))}
            </div>
          </motion.div>

          {/* Graph Stats */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <div className="glass-panel p-4 flex flex-col gap-3 rounded-2xl">
              <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-secondary">Graph Status</h3>
              {[
                { label: "Nodes Active",       value: "312",      highlight: false },
                { label: "Relationships",       value: "1,847",    highlight: false },
                { label: "Avg. Confidence",     value: "94.2%",    highlight: false },
                { label: "Last Sync",           value: "2s ago",   highlight: false },
                { label: "Sync State",          value: "Realtime", highlight: true  },
              ].map(({ label, value, highlight }) => (
                <div key={label} className="flex justify-between items-center text-sm font-mono">
                  <span className="text-secondary">{label}</span>
                  <span className={highlight ? "font-bold" : "text-primary font-bold"}
                    style={highlight ? { color: "#ED7D27" } : {}}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Recent Entity Links */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
          >
            <div className="glass-panel p-4 flex flex-col gap-2.5 rounded-2xl">
              <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-secondary mb-1">Recent Knowledge Links</h3>
              {RECENT_LINKS.map(({ from, to, strength }) => (
                <div key={from} className="flex flex-col gap-0.5 p-2 rounded-lg" style={{ background: "rgba(255,255,255,0.03)" }}>
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] text-primary truncate max-w-[200px]">{from}</span>
                    <span className="font-mono text-[9px] font-bold ml-2" style={{ color: strength > 95 ? "#10B981" : "#ED7D27" }}>{strength}%</span>
                  </div>
                  <span className="font-mono text-[9px] text-secondary truncate">→ {to}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  );
}
