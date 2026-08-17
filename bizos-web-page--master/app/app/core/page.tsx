"use client";

import { motion } from "framer-motion";
import { Brain, UtensilsCrossed, CalendarDays, Cpu, ShieldCheck, ChefHat } from "lucide-react";

const THOUGHT_STREAM = [
  {
    time: "12:47:03",
    action: "Weekend Specials Menu Published",
    detail: "Hyderabadi Dum Biryani + Paneer Handi featured",
    state: "emerald",
  },
  {
    time: "12:46:58",
    action: "Low Stock Alert → Auto-Reorder Triggered",
    detail: "Chicken (5kg below threshold) → Srinivas Traders notified",
    state: "amber",
  },
  {
    time: "12:46:44",
    action: "VIP Regulars Detected — Table Prep Started",
    detail: "Rajesh Kumar, Meera Pillai, Suresh family — preferences loaded",
    state: "sky",
  },
  {
    time: "12:46:30",
    action: "Lunch Peak Predicted: 47 covers in 20 min",
    detail: "Kitchen alerted · 3 extra staff rostered",
    state: "purple",
  },
  {
    time: "12:46:15",
    action: "AI Upsell Suggestion Fired",
    detail: "Dal Makhani Combo recommended to 12 current tables",
    state: "emerald",
  },
  {
    time: "12:45:50",
    action: "Catering Event Confirmed",
    detail: "Saturday 80-pax corporate lunch — Sharma & Associates",
    state: "sky",
  },
];

const STATUS_ROWS = [
  { icon: Brain,            label: "Menu Intelligence",  value: "Optimal",  color: "emerald" },
  { icon: UtensilsCrossed,  label: "Order Processing",   value: "47 Active", color: "sky" },
  { icon: CalendarDays,     label: "Table Management",   value: "Syncing",  color: "sky" },
  { icon: ChefHat,          label: "Kitchen Comms",      value: "Secured",  color: "emerald" },
];

const CORE_METRICS = [
  { label: "Orders Today",        value: "183",    delta: "+12% vs yesterday" },
  { label: "Avg. Ticket Value",   value: "₹847",   delta: "Upsell active" },
  { label: "Table Turnover",      value: "2.4x",   delta: "Peak lunch" },
  { label: "AI Decisions Today",  value: "34",     delta: "94% accepted" },
];

export default function CoreDashboard() {
  return (
    <main className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-all duration-200 ease-[0.16,1,0.3,1]">
      <div className="mx-auto max-w-[1440px] space-y-7">

        {/* Page Header */}
        <div>
          <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-accent">
            Hotel Balagi Bhavan / AI Runtime
          </p>
          <h1 className="mt-1 font-display text-[24px] md:text-[28px] font-semibold tracking-tight text-ink">
            Core Runtime
          </h1>
          <p className="font-mono text-[11px] text-ink-muted mt-0.5">
            Live AI orchestration for Balagi Bhavan's daily operations
          </p>
        </div>

        {/* Quick Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {CORE_METRICS.map(({ label, value, delta }) => (
            <div
              key={label}
              className="glass-card p-5 rounded-[20px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 backdrop-blur-xl shadow-sm hover:-translate-y-0.5 hover:shadow-md transition-all duration-200"
            >
              <p className="font-mono text-[10px] uppercase tracking-widest text-ink-muted mb-1">{label}</p>
              <p className="font-display text-[28px] font-bold text-ink tracking-tight">{value}</p>
              <p className="font-mono text-[10px] mt-1" style={{ color: "#ED7D27" }}>{delta}</p>
            </div>
          ))}
        </motion.div>

        {/* 3-Column Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-7">

          {/* Left: Cognitive Core */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-4 flex flex-col gap-6"
          >
            <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1]">
              <p className="eyebrow mb-4 text-accent">Cognitive Core</p>

              {/* Status Ring — 94% efficiency during lunch peak */}
              <div className="flex flex-col items-center justify-center my-4">
                <div className="relative w-44 h-44 flex items-center justify-center">
                  <motion.div
                    className="absolute inset-0 rounded-full border opacity-40"
                    style={{ borderColor: "rgba(237,125,39,0.3)" }}
                    animate={{ scale: [1, 1.12, 1], opacity: [0.3, 0.1, 0.3] }}
                    transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
                  />
                  <svg className="w-full h-full -rotate-90">
                    <circle cx="88" cy="88" r="78" fill="none" stroke="currentColor" strokeWidth="6" className="text-[#E2DAD0] dark:text-zinc-800" />
                    <motion.circle
                      cx="88" cy="88" r="78" fill="none"
                      stroke="#ED7D27" strokeWidth="6" strokeLinecap="round"
                      strokeDasharray="490" strokeDashoffset="29"
                      initial={{ strokeDashoffset: 490 }}
                      animate={{ strokeDashoffset: 29 }}
                      transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                    />
                  </svg>
                  <div className="absolute text-center">
                    <span className="block font-display text-[32px] font-bold text-ink">94%</span>
                    <span className="block font-mono text-[10px] uppercase tracking-widest text-ink-muted font-semibold mt-0.5">
                      Efficiency
                    </span>
                  </div>
                </div>
                <p className="font-mono text-[10px] text-ink-muted mt-2 uppercase tracking-wider">Lunch Peak — Max Throughput</p>
              </div>

              {/* Status Rows */}
              <div className="w-full space-y-3 mt-6">
                {STATUS_ROWS.map(({ icon: Icon, label, value, color }) => (
                  <StatusRow key={label} icon={Icon} label={label} value={value} color={color} />
                ))}
              </div>
            </div>
          </motion.div>

          {/* Center: Live Cognitive Activity */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-4 flex flex-col"
          >
            <div className="glass-card min-h-[380px] p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1] flex flex-col relative overflow-hidden h-full">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(237,125,39,0.05)_0%,transparent_70%)] pointer-events-none" />

              <p className="eyebrow mb-5 text-accent relative z-10">Live Operations Feed</p>

              <div className="flex-1 flex flex-col gap-3 relative z-10">
                {/* Live order ticker */}
                {[
                  { table: "T-04", order: "2× Chicken Biryani, 1× Raita", status: "KOT Sent", color: "#10B981" },
                  { table: "T-11", order: "Veg Thali × 4 (Sharma family)", status: "Preparing", color: "#ED7D27" },
                  { table: "T-07", order: "Masala Dosa × 2, Filter Coffee × 2", status: "Ready", color: "#38BDF8" },
                  { table: "T-02", order: "Mutton Rogan Josh, Butter Naan × 3", status: "Served", color: "#A78BFA" },
                ].map(({ table, order, status, color }) => (
                  <div key={table} className="flex items-start justify-between p-3 rounded-xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/70 dark:bg-zinc-800/40">
                    <div>
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="font-mono text-[10px] font-bold" style={{ color }}>{table}</span>
                        <span className="font-mono text-[9px] text-ink-muted uppercase tracking-wider">{status}</span>
                      </div>
                      <p className="font-mono text-[11px] text-ink leading-snug">{order}</p>
                    </div>
                    <span className="w-2 h-2 rounded-full mt-1.5 shrink-0" style={{ background: color }} />
                  </div>
                ))}

                {/* AI System Status */}
                <div className="mt-2 p-3 rounded-xl border border-[#E2DAD0] dark:border-zinc-800 bg-white/40 dark:bg-zinc-800/20 flex items-center gap-3">
                  <Cpu className="w-5 h-5 shrink-0" style={{ color: "#ED7D27" }} strokeWidth={1.75} />
                  <div>
                    <p className="font-mono text-[10px] text-ink-muted uppercase tracking-wider">AI Runtime Status</p>
                    <p className="font-mono text-[12px] font-bold text-ink">All Systems Nominal · 34 decisions today</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right: ThoughtStream */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-4 flex flex-col"
          >
            <div className="glass-card p-7 backdrop-blur-xl bg-[#FAF7F2]/95 dark:bg-zinc-900/95 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.06)] hover:-translate-y-0.5 rounded-[28px] transition-all duration-200 ease-[0.16,1,0.3,1] flex flex-col h-full">
              <p className="eyebrow mb-6 text-accent">Cognitive Timeline</p>

              <div className="flex-1 space-y-5 relative before:absolute before:inset-y-0 before:left-3 before:w-px before:bg-[#E2DAD0] dark:before:bg-zinc-800">
                {THOUGHT_STREAM.map((event, i) => (
                  <TimelineEvent key={i} {...event} />
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  );
}

function StatusRow({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) {
  const badgeColors: Record<string, string> = {
    emerald: "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    sky: "text-[#0EA5E9] dark:text-[#38BDF8] bg-[#F0F9FF] dark:bg-[#0F172A] border-[#38BDF8]/40",
    amber: "text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/30",
    purple: "text-purple-600 dark:text-purple-400 bg-purple-500/10 border-purple-500/30",
  };
  return (
    <div className="flex items-center justify-between font-mono text-[12px] p-2.5 rounded-xl border border-[#E2DAD0] dark:border-zinc-800/80 bg-white/80 dark:bg-zinc-800/50 shadow-sm transition-all duration-200 hover:border-[#ED7D27]">
      <div className="flex items-center gap-2.5 text-ink">
        <Icon className="w-4 h-4 text-ink-muted" strokeWidth={1.75} />
        <span className="uppercase tracking-wider font-semibold">{label}</span>
      </div>
      <span className={`font-mono text-[10.5px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${badgeColors[color]}`}>
        {value}
      </span>
    </div>
  );
}

function TimelineEvent({ time, action, detail, state }: { time: string; action: string; detail?: string; state: string }) {
  const dotColors: Record<string, string> = {
    emerald: "bg-emerald-500",
    sky: "bg-[#0EA5E9]",
    purple: "bg-purple-500",
    amber: "bg-amber-500",
  };
  return (
    <div className="relative pl-8 group">
      <div className={`absolute left-[9px] top-1.5 h-2.5 w-2.5 rounded-full ${dotColors[state]} shadow-sm group-hover:scale-125 transition-transform duration-200`} />
      <div className="font-mono text-[10.5px] text-ink-muted font-medium mb-0.5">{time}</div>
      <div className="text-[13px] font-semibold text-ink leading-snug">{action}</div>
      {detail && <div className="text-[11.5px] text-ink-muted font-light mt-0.5">{detail}</div>}
    </div>
  );
}
