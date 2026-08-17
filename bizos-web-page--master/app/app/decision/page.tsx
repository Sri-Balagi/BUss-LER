"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  Layers,
  Network,
  CheckCircle2,
  ChevronRight,
  Clock,
  AlertTriangle,
  UtensilsCrossed,
  Sparkles,
  Zap,
  Check,
  X,
  TrendingUp,
  Brain,
  ShieldCheck,
  Building2,
  Calendar,
  Users,
} from "lucide-react";
import { useState } from "react";

// Hotel Balagi Bhavan Decision Scenarios
const SCENARIOS = [
  {
    id: "biryani-surge",
    title: "Weekend Biryani Surge & Stock Re-order",
    icon: UtensilsCrossed,
    confidence: 94,
    color: "#ED7D27",
    category: "Culinary & Inventory",
    root: {
      title: "Weekend Biryani Demand Surge Prediction",
      confidence: 94,
      detail: "Festival + pre-orders signal 60% demand spike over baseline",
    },
    branches: [
      {
        title: "Customer Order History (Last 90 Days)",
        confidence: 88,
        source: "Memory Layer",
        detail: "64 regulars ordered Biryani 3+ times on festival weekends",
        color: "#10B981",
      },
      {
        title: "Festival Calendar: Ganesh Chaturthi",
        confidence: 97,
        source: "Knowledge Layer",
        detail: "Historically +43% footfall at Balagi Bhavan",
        color: "#38BDF8",
      },
      {
        title: "Current Basmati & Spice Inventory",
        confidence: 91,
        source: "Supply Core",
        detail: "Basmati Stock: 45kg (Requires +30kg top-up)",
        color: "#A78BFA",
      },
    ],
    output: {
      action: "Prep 40 extra Biryani portions & auto-PO to Srinivas Traders for 30kg Basmati",
      impact: "Estimated +₹18,400 revenue",
    },
  },
  {
    id: "banquet-booking",
    title: "Balagi Mandapam Banquet (250 Pax)",
    icon: Building2,
    confidence: 98,
    color: "#A78BFA",
    category: "Banquet Operations",
    root: {
      title: "Sharma Family Wedding Banquet Confirmation",
      confidence: 98,
      detail: "250 Pax South Indian Buffet + Special Sweet Station",
    },
    branches: [
      {
        title: "Banquet Hall Availability (Hall A & B)",
        confidence: 100,
        source: "Knowledge Layer",
        detail: "Balagi Mandapam free 11:00 AM - 4:00 PM Saturday",
        color: "#A78BFA",
      },
      {
        title: "Extra Service Staff Roster",
        confidence: 95,
        source: "Staff Core",
        detail: "8 extra servers + Chef Venkatesh leading kitchen prep",
        color: "#10B981",
      },
      {
        title: "Sweet Station Ingredient Prep",
        confidence: 96,
        source: "Inventory Layer",
        detail: "Kaju Katli & Mysore Pak pre-batching scheduled",
        color: "#ED7D27",
      },
    ],
    output: {
      action: "Lock Balagi Mandapam booking & issue KOT to Central Kitchen",
      impact: "Contract Value: ₹1,25,000",
    },
  },
  {
    id: "express-tiffin",
    title: "Peak Lunch Express Tiffin Traffic Control",
    icon: Zap,
    confidence: 91,
    color: "#0EA5E9",
    category: "Floor Management",
    root: {
      title: "Express Dosa & Filter Coffee Queue Optimization",
      confidence: 91,
      detail: "12:30 PM lunch rush expected: 47 covers in 20 mins",
    },
    branches: [
      {
        title: "Table Turnover Rate (Tables 1-15)",
        confidence: 92,
        source: "Metrics Core",
        detail: "Average 22-min meal duration for tiffin customers",
        color: "#0EA5E9",
      },
      {
        title: "Dosa Batter Stock & Griddle Saturation",
        confidence: 89,
        source: "Kitchen Sensor",
        detail: "3 griddles active · Batter prep for 120 dosas ready",
        color: "#ED7D27",
      },
      {
        title: "Regular Customer Seating Preference",
        confidence: 93,
        source: "Memory Layer",
        detail: "Priority seating for Rajesh Kumar & VIP regular groups",
        color: "#10B981",
      },
    ],
    output: {
      action: "Open Express Counter 2 & enable QR Table Ordering",
      impact: "Reduced wait time by 8 mins",
    },
  },
];

// Initial Approvals List
const INITIAL_APPROVALS = [
  {
    id: 1,
    action: "Increase Chicken Biryani prep by 40 portions",
    time: "4m ago",
    confidence: 94,
    impact: "High",
    status: "approved",
    category: "Kitchen",
    reason: "Festival weekend + 3 pre-orders confirmed by Sharma family",
  },
  {
    id: 2,
    action: "Auto-PO: 30kg Basmati Rice to Srinivas Traders",
    time: "12m ago",
    confidence: 91,
    impact: "High",
    status: "approved",
    category: "Inventory",
    reason: "Current stock at 45kg (below 60kg weekend threshold)",
  },
  {
    id: 3,
    action: "SMS promo: 'Weekend Special – Hyderabadi Dum Biryani'",
    time: "18m ago",
    confidence: 88,
    impact: "Medium",
    status: "approved",
    category: "Marketing",
    reason: "Targeting 92 regular customers with Biryani order history",
  },
  {
    id: 4,
    action: "Reserve Table 7 & 8 for VIP Family Booking",
    time: "45m ago",
    confidence: 100,
    impact: "Low",
    status: "approved",
    category: "Floor",
    reason: "Confirmed booking: 12 pax at 1:30 PM Saturday",
  },
  {
    id: 5,
    action: "Feature Dal Tadka as Friday Special Combo",
    time: "Pending",
    confidence: 79,
    impact: "Medium",
    status: "pending",
    category: "Menu",
    reason: "Lentil surplus + high 4.8★ rating in last 3 Fridays",
  },
  {
    id: 6,
    action: "Extend closing time to 11:30 PM on Ganesh Chaturthi",
    time: "Pending",
    confidence: 83,
    impact: "High",
    status: "pending",
    category: "Operations",
    reason: "Late temple procession traffic predicted near Balagi Bhavan",
  },
];

export default function DecisionLayer() {
  const [activeScenarioId, setActiveScenarioId] = useState("biryani-surge");
  const [approvals, setApprovals] = useState(INITIAL_APPROVALS);
  const [selectedApprovalId, setSelectedApprovalId] = useState<number | null>(5);

  const activeScenario = SCENARIOS.find((s) => s.id === activeScenarioId) || SCENARIOS[0];

  const handleApprove = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setApprovals((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: "approved" } : item))
    );
  };

  const handleReject = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setApprovals((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: "rejected" } : item))
    );
  };

  const totalDecisions = approvals.length;
  const approvedCount = approvals.filter((a) => a.status === "approved").length;
  const pendingCount = approvals.filter((a) => a.status === "pending").length;

  return (
    <main className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-colors duration-300 bg-[#FAF7F2] dark:bg-deep-space">
      <div className="mx-auto max-w-[1440px] space-y-7">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="flex flex-col sm:flex-row sm:items-end justify-between gap-4"
        >
          <div>
            <p className="font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-[#ED7D27]">
              Hotel Balagi Bhavan / Decision Intelligence
            </p>
            <div className="flex items-center gap-3 mt-1">
              <div className="p-2.5 rounded-xl bg-orange-100 dark:bg-orange-950/60 border border-orange-300 dark:border-orange-700/60 text-[#ED7D27] shadow-sm">
                <Layers className="w-6 h-6 sm:w-7 sm:h-7" strokeWidth={1.75} />
              </div>
              <h1 className="font-display text-[26px] md:text-[30px] font-bold tracking-tight text-zinc-900 dark:text-white">
                Decision Engine
              </h1>
            </div>
            <p className="font-mono text-[11.5px] uppercase tracking-widest font-semibold text-zinc-600 dark:text-zinc-400 mt-1">
              Automated Reasoning, Confidence Scoring & Operational Governance
            </p>
          </div>

          {/* Engine Status Badge */}
          <div className="px-5 py-2.5 rounded-full border-2 border-orange-200 dark:border-orange-800/60 bg-orange-50/90 dark:bg-orange-950/60 backdrop-blur-xl shadow-sm flex items-center gap-3 self-start sm:self-auto">
            <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-[#ED7D27] font-bold">
              Engine Status
            </span>
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#ED7D27] opacity-75" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#ED7D27]" />
              </span>
              <span className="font-mono text-xs font-bold text-zinc-900 dark:text-white uppercase tracking-wider">
                Optimal (94% Accuracy)
              </span>
            </div>
          </div>
        </motion.div>

        {/* Scenario Switcher Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.05 }}
          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 p-2 rounded-2xl bg-white/80 dark:bg-zinc-900/80 border border-zinc-200 dark:border-zinc-800 shadow-sm backdrop-blur-xl"
        >
          <span className="font-mono text-[10px] uppercase tracking-widest text-zinc-400 font-bold px-3 hidden sm:inline">
            Active Scenarios:
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 w-full">
            {SCENARIOS.map((sc) => {
              const Icon = sc.icon;
              const isActive = sc.id === activeScenarioId;
              return (
                <button
                  key={sc.id}
                  onClick={() => setActiveScenarioId(sc.id)}
                  className={`flex items-center justify-between gap-3 px-4 py-3 rounded-xl font-mono text-xs font-semibold transition-all duration-200 text-left ${
                    isActive
                      ? "bg-orange-100 dark:bg-orange-950/80 text-orange-950 dark:text-orange-100 border-2 border-[#ED7D27] shadow-sm scale-[1.01]"
                      : "bg-zinc-50/60 dark:bg-zinc-800/40 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 border border-zinc-200/80 dark:border-zinc-800"
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <Icon className="w-4 h-4 shrink-0" style={{ color: sc.color }} />
                    <span className="truncate">{sc.title}</span>
                  </div>
                  <span
                    className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0"
                    style={{ background: `${sc.color}20`, color: sc.color }}
                  >
                    {sc.confidence}%
                  </span>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Main Grid: Reasoning Tree & Approvals */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-7">

          {/* Left Column: Interactive Reasoning Tree */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="lg:col-span-7 flex flex-col"
          >
            <div className="glass-card p-6 sm:p-7 backdrop-blur-xl bg-white/90 dark:bg-zinc-900/90 border-2 border-zinc-200 dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] rounded-[28px] flex flex-col h-full">

              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="font-mono text-[11px] font-bold uppercase tracking-[0.18em] text-[#ED7D27]">
                    Live Reasoning Graph
                  </p>
                  <p className="font-mono text-[11px] text-zinc-500 dark:text-zinc-400">
                    Category: {activeScenario.category}
                  </p>
                </div>

                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800">
                  <Brain className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <span className="font-mono text-[10px] font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-widest">
                    Verified Reasoning
                  </span>
                </div>
              </div>

              {/* Animate Tree change on scenario switch */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeScenario.id}
                  initial={{ opacity: 0, scale: 0.97 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.97 }}
                  transition={{ duration: 0.25 }}
                  className="flex-1 border-2 border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/70 dark:bg-zinc-950/50 p-6 sm:p-7 flex flex-col items-center gap-5 overflow-x-auto"
                >
                  {/* Root Node */}
                  <div className="w-full sm:w-[340px] p-4 rounded-2xl bg-orange-100/90 dark:bg-orange-950/80 border-2 border-[#ED7D27] shadow-md shadow-orange-500/10 flex flex-col gap-1.5 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <Sparkles className="w-4 h-4 text-[#ED7D27]" />
                      <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-orange-900 dark:text-orange-200">
                        Root Hypothesis
                      </span>
                    </div>
                    <span className="font-display text-sm font-bold text-orange-950 dark:text-orange-50">
                      {activeScenario.root.title}
                    </span>
                    <span className="font-mono text-[10.5px] text-orange-800 dark:text-orange-300">
                      {activeScenario.root.detail}
                    </span>
                  </div>

                  <div className="w-0.5 h-6 bg-gradient-to-b from-[#ED7D27] to-zinc-400 dark:to-zinc-700" />

                  {/* Branch Nodes (3 Parallel Inputs) */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full">
                    {activeScenario.branches.map((branch, i) => (
                      <div
                        key={i}
                        className="p-3.5 rounded-xl border-2 bg-white dark:bg-zinc-900 shadow-sm flex flex-col gap-1.5 transition-all hover:scale-[1.02]"
                        style={{ borderColor: branch.color }}
                      >
                        <div className="flex items-center justify-between">
                          <span
                            className="font-mono text-[9px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full"
                            style={{ background: `${branch.color}20`, color: branch.color }}
                          >
                            {branch.source}
                          </span>
                          <span className="font-mono text-[10px] font-bold text-zinc-600 dark:text-zinc-300">
                            {branch.confidence}%
                          </span>
                        </div>
                        <span className="font-mono text-xs font-bold text-zinc-900 dark:text-zinc-100 leading-snug">
                          {branch.title}
                        </span>
                        <span className="font-mono text-[10px] text-zinc-500 dark:text-zinc-400 leading-tight">
                          {branch.detail}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="w-0.5 h-5 bg-gradient-to-b from-zinc-400 dark:from-zinc-700 to-emerald-500" />

                  {/* Output Node */}
                  <div className="w-full p-4 rounded-2xl bg-emerald-100/90 dark:bg-emerald-950/80 border-2 border-emerald-500 shadow-md flex items-start gap-3">
                    <CheckCircle2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" strokeWidth={2} />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-emerald-900 dark:text-emerald-300">
                          Recommended Action Output
                        </span>
                        <span className="font-mono text-[10px] font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-200/80 dark:bg-emerald-900/60 px-2 py-0.5 rounded-full">
                          {activeScenario.output.impact}
                        </span>
                      </div>
                      <p className="font-display text-sm font-bold text-emerald-950 dark:text-emerald-100 mt-1 leading-snug">
                        {activeScenario.output.action}
                      </p>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>

              {/* Confidence Progress Meter */}
              <div className="mt-6 pt-4 border-t border-zinc-200 dark:border-zinc-800">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-mono text-[11px] uppercase tracking-widest text-zinc-600 dark:text-zinc-400 font-bold">
                    Aggated Decision Confidence
                  </span>
                  <span className="font-display text-[22px] font-bold text-zinc-900 dark:text-white">
                    {activeScenario.confidence}%
                  </span>
                </div>
                <div className="w-full h-2.5 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden p-0.5">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ background: `linear-gradient(to right, #ED7D27, ${activeScenario.color})` }}
                    initial={{ width: 0 }}
                    animate={{ width: `${activeScenario.confidence}%` }}
                    transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right Column: Approvals & Interactive Action Queue */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.15 }}
            className="lg:col-span-5 flex flex-col"
          >
            <div className="glass-card p-6 sm:p-7 backdrop-blur-xl bg-white/90 dark:bg-zinc-900/90 border-2 border-zinc-200 dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] rounded-[28px] flex flex-col gap-5 h-full">

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-mono text-[11px] font-bold uppercase tracking-[0.18em] text-[#ED7D27]">
                    Operational Governance
                  </p>
                  <h3 className="font-display text-lg font-bold text-zinc-900 dark:text-white">
                    Action Approvals Queue
                  </h3>
                </div>

                <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-800">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                  <span className="font-mono text-[10px] font-bold text-amber-900 dark:text-amber-300 uppercase tracking-wider">
                    {pendingCount} Pending Approval
                  </span>
                </div>
              </div>

              {/* Action List */}
              <div className="flex-1 space-y-3 overflow-y-auto max-h-[440px] pr-1">
                {approvals.map((item) => {
                  const isSelected = item.id === selectedApprovalId;
                  const isPending = item.status === "pending";
                  const isApproved = item.status === "approved";
                  const isRejected = item.status === "rejected";

                  return (
                    <div
                      key={item.id}
                      onClick={() => setSelectedApprovalId(isSelected ? null : item.id)}
                      className={`rounded-2xl border-2 transition-all duration-200 cursor-pointer overflow-hidden ${
                        isSelected
                          ? "border-[#ED7D27] bg-orange-50/80 dark:bg-orange-950/40 shadow-sm"
                          : "border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-900/60 hover:border-zinc-400 dark:hover:border-zinc-700"
                      }`}
                    >
                      <div className="p-3.5 flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          {isApproved && (
                            <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" strokeWidth={2} />
                          )}
                          {isPending && (
                            <Clock className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" strokeWidth={2} />
                          )}
                          {isRejected && (
                            <X className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" strokeWidth={2} />
                          )}

                          <div>
                            <div className="flex items-center gap-2 mb-0.5">
                              <span className="font-mono text-[9.5px] font-bold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
                                {item.category}
                              </span>
                              <span
                                className={`font-mono text-[9px] font-bold px-2 py-0.2 rounded-full ${
                                  isApproved
                                    ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                    : isPending
                                    ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                                    : "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300"
                                }`}
                              >
                                {item.status.toUpperCase()}
                              </span>
                            </div>

                            <p className="font-mono text-xs font-bold text-zinc-900 dark:text-zinc-100 leading-snug">
                              {item.action}
                            </p>
                          </div>
                        </div>

                        {/* Interactive Action Buttons for Pending items */}
                        {isPending ? (
                          <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
                            <button
                              onClick={(e) => handleApprove(item.id, e)}
                              className="p-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-bold transition-transform active:scale-95 shadow-sm"
                              title="Approve Action"
                            >
                              <Check className="w-4 h-4" strokeWidth={2.5} />
                            </button>
                            <button
                              onClick={(e) => handleReject(item.id, e)}
                              className="p-1.5 rounded-lg bg-rose-500 hover:bg-rose-600 text-white font-bold transition-transform active:scale-95 shadow-sm"
                              title="Reject Action"
                            >
                              <X className="w-4 h-4" strokeWidth={2.5} />
                            </button>
                          </div>
                        ) : (
                          <ChevronRight
                            className={`w-4 h-4 text-zinc-400 shrink-0 transition-transform ${
                              isSelected ? "rotate-90" : ""
                            }`}
                          />
                        )}
                      </div>

                      {/* Expandable Reasoning Details */}
                      {isSelected && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          transition={{ duration: 0.2 }}
                          className="px-4 pb-3.5 pt-2 border-t border-zinc-200 dark:border-zinc-800 bg-white/40 dark:bg-zinc-950/40"
                        >
                          <div className="flex items-start gap-2">
                            <UtensilsCrossed className="w-4 h-4 text-[#ED7D27] shrink-0 mt-0.5" strokeWidth={2} />
                            <div>
                              <p className="font-mono text-[11px] font-bold text-zinc-900 dark:text-zinc-200">
                                AI Rationale:
                              </p>
                              <p className="font-mono text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5 leading-relaxed">
                                {item.reason}
                              </p>
                              <div className="flex items-center gap-4 mt-2 font-mono text-[10px] text-zinc-500">
                                <span>Confidence: {item.confidence}%</span>
                                <span>Impact Level: {item.impact}</span>
                                <span>Logged: {item.time}</span>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Stats Footer */}
              <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800 grid grid-cols-3 gap-3">
                <div className="text-center p-2.5 rounded-xl bg-zinc-100 dark:bg-zinc-800/60">
                  <p className="font-display text-xl font-bold text-zinc-900 dark:text-white">{totalDecisions}</p>
                  <p className="font-mono text-[9px] uppercase tracking-widest text-zinc-500 dark:text-zinc-400 font-semibold">Total Logged</p>
                </div>
                <div className="text-center p-2.5 rounded-xl bg-emerald-100/60 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800">
                  <p className="font-display text-xl font-bold text-emerald-800 dark:text-emerald-300">{approvedCount}</p>
                  <p className="font-mono text-[9px] uppercase tracking-widest text-emerald-700 dark:text-emerald-400 font-bold">Approved</p>
                </div>
                <div className="text-center p-2.5 rounded-xl bg-amber-100/60 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-800">
                  <p className="font-display text-xl font-bold text-amber-800 dark:text-amber-300">{pendingCount}</p>
                  <p className="font-mono text-[9px] uppercase tracking-widest text-amber-700 dark:text-amber-400 font-bold">Pending Signoff</p>
                </div>
              </div>

            </div>
          </motion.div>

        </div>
      </div>
    </main>
  );
}
