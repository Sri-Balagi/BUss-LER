"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Users,
  Database,
  Mail,
  Calendar,
  FileText,
  MessageSquare,
  CreditCard,
  BarChart3,
  UserCheck,
  Hash,
  GitBranch,
  Kanban,
  Cpu,
} from "lucide-react";

// Perfectly symmetrical 12-point circular radial orbit around center (50%, 50%)
const ENTERPRISE_APPS = [
  { id: "erp", name: "ERP", label: "SAP", icon: Database, x: 50, y: 14, delay: 0.4 },
  { id: "email", name: "Email", label: "Outlook", icon: Mail, x: 68, y: 19, delay: 0.8 },
  { id: "slack", name: "Slack", label: "Slack", icon: Hash, x: 81, y: 32, delay: 0.2 },
  { id: "docs", name: "Docs", label: "Notion", icon: FileText, x: 86, y: 50, delay: 0.3 },
  { id: "jira", name: "Jira", label: "Atlassian", icon: Kanban, x: 81, y: 68, delay: 0.5 },
  { id: "calendar", name: "Calendar", label: "Google", icon: Calendar, x: 68, y: 81, delay: 1.0 },
  { id: "analytics", name: "Analytics", label: "Mixpanel", icon: BarChart3, x: 50, y: 86, delay: 1.1 },
  { id: "github", name: "GitHub", label: "GitHub", icon: GitBranch, x: 32, y: 81, delay: 0.6 },
  { id: "billing", name: "Billing", label: "Stripe", icon: CreditCard, x: 19, y: 68, delay: 0.7 },
  { id: "support", name: "Support", label: "Zendesk", icon: MessageSquare, x: 14, y: 50, delay: 1.2 },
  { id: "hr", name: "HR", label: "Workday", icon: UserCheck, x: 19, y: 32, delay: 0.9 },
  { id: "crm", name: "CRM", label: "Salesforce", icon: Users, x: 32, y: 19, delay: 0 },
];

export function Problem() {
  const [hoveredSys, setHoveredSys] = useState<number | null>(null);

  return (
    <section className="relative w-full border-t border-[color:var(--border-color)] bg-section-alt">
      <div className="mx-auto max-w-6xl px-6 py-24 md:py-36 grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-20 items-center">
        {/* Left Side: Text Content */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
        >
          <h2 className="font-display text-[42px] md:text-[56px] font-semibold leading-[1.1] tracking-tight text-ink mb-8">
            Software wasn't designed to think.
          </h2>
          <div className="space-y-8 text-[16px] md:text-[18px] leading-relaxed text-ink-muted font-light">
            <motion.p
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.65, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            >
              Businesses don't suffer from a lack of software. They suffer from software that never shares what it knows.
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.65, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
            >
              Every application owns a piece of the truth. Your CRM knows who the customer is. Your issue tracker knows they are frustrated. Your billing system knows they are churning.
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.65, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
            >
              BizOS bridges every enterprise system into a unified intelligence engine where operations flow seamlessly and decisions are synchronized in real time.
            </motion.p>
          </div>
        </motion.div>

        {/* Right Side: Positive BIZOS CORE Intelligence Mesh Illustration */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="relative h-[500px] sm:h-[540px] w-full glass-panel overflow-hidden flex items-center justify-center p-6 sm:p-8 rounded-[32px] bg-[#FAF7F2]/90 dark:bg-zinc-900 border-2 border-[#E6DFD3] dark:border-zinc-800 shadow-[0_8px_32px_rgba(0,0,0,0.04)] hover:shadow-[0_16px_36px_rgba(0,0,0,0.08)] hover:border-[#38BDF8] hover:-translate-y-1 transition-all duration-300 ease-out"
        >
          {/* Soft background grid & radial light glow centered at (50%, 50%) */}
          <div className="absolute inset-0 bg-[radial-gradient(#E2DAD0_1px,transparent_1px)] [background-size:24px_24px] opacity-40 pointer-events-none" />
          <motion.div
            style={{ left: "50%", top: "50%" }}
            animate={{ x: "-50%", y: "-50%", scale: [1, 1.08, 1], opacity: [0.25, 0.4, 0.25] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            className="absolute w-[360px] h-[360px] rounded-full bg-[#0EA5E9]/[0.08] blur-[80px] pointer-events-none"
          />

          {/* SVG Canvas for Active Data Streams & Sync Particles */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            {ENTERPRISE_APPS.map((app) => (
              <g key={app.id}>
                {/* Glowing active connection stream line to center (50%, 50%) */}
                <line
                  x1={`${app.x}%`}
                  y1={`${app.y}%`}
                  x2="50%"
                  y2="50%"
                  stroke="#38BDF8"
                  strokeWidth="1.75"
                  strokeDasharray="5 5"
                  strokeOpacity="0.5"
                />

                {/* Active Sync Node Badge '✓' halfway to center */}
                <circle
                  cx={`${(app.x + 50) / 2}%`}
                  cy={`${(app.y + 50) / 2}%`}
                  r="6.5"
                  fill="#F0F9FF"
                  stroke="#0EA5E9"
                  strokeWidth="1.5"
                />
                <text
                  x={`${(app.x + 50) / 2}%`}
                  y={`${(app.y + 50) / 2}%`}
                  fill="#0EA5E9"
                  fontSize="8"
                  fontWeight="bold"
                  textAnchor="middle"
                  dominantBaseline="central"
                >
                  ✓
                </text>

                {/* Moving active data particle flowing inward into BizOS Core */}
                <motion.circle
                  r="3.5"
                  fill="#0EA5E9"
                  initial={{ opacity: 0 }}
                  animate={{
                    cx: [`${app.x}%`, "50%"],
                    cy: [`${app.y}%`, "50%"],
                    opacity: [0, 0.95, 0],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    delay: app.delay,
                    ease: "linear",
                  }}
                />
              </g>
            ))}
          </svg>

          {/* Center Nucleus: "BIZOS CORE" Positive Intelligence Engine Node */}
          <motion.div
            style={{ left: "50%", top: "50%" }}
            animate={{ x: "-50%", y: "-50%", scale: [1, 1.04, 1] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="absolute z-10 flex flex-col items-center justify-center p-3 rounded-full border-2 border-[#0EA5E9] bg-[#F0F9FF] dark:bg-zinc-900 shadow-[0_4px_20px_rgba(0,0,0,0.06)] text-center w-28 h-28 sm:w-30 sm:h-30"
          >
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute inset-[-6px] rounded-full border-2 border-dashed border-[#38BDF8]/60 pointer-events-none"
            />
            <div className="flex h-7.5 w-7.5 items-center justify-center rounded-full bg-[#E0F2FE] text-[#0EA5E9] mb-1 shadow-sm">
              <Cpu className="h-4.5 w-4.5" />
            </div>
            <span className="font-mono text-[11px] sm:text-[12px] font-bold uppercase tracking-wider text-[#0284C7]">
              BizOS Core
            </span>
            <span className="text-[9px] font-mono text-ink-muted/85 mt-0.5 font-medium">
              12 Systems Synchronized
            </span>
          </motion.div>

          {/* Orbiting Enterprise Application Cards */}
          {ENTERPRISE_APPS.map((app, i) => {
            const Icon = app.icon;
            const isFocused = hoveredSys === i;
            const isBlurred = hoveredSys !== null && !isFocused;

            return (
              <div
                key={app.id}
                style={{
                  position: "absolute",
                  left: `${app.x}%`,
                  top: `${app.y}%`,
                  transform: "translate(-50%, -50%)",
                  zIndex: 20,
                }}
              >
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  onMouseEnter={() => setHoveredSys(i)}
                  onMouseLeave={() => setHoveredSys(null)}
                  transition={{
                    duration: 0.6,
                    delay: 0.3 + i * 0.05,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  animate={
                    isFocused
                      ? { y: -4, scale: 1.08 }
                      : { y: [0, -4, 0] }
                  }
                  className={`cursor-pointer transition-all duration-300 ${
                    isBlurred ? "opacity-35 blur-[1.5px] scale-90" : "opacity-100"
                  }`}
                >
                  <div
                    className={`flex items-center gap-2 px-2.5 sm:px-3 py-1.5 rounded-2xl border-2 transition-all duration-300 ${
                      isFocused
                        ? "border-[#38BDF8] bg-[#F0F9FF] dark:bg-[#0F172A] shadow-[0_10px_24px_rgba(0,0,0,0.08)] text-[#0EA5E9]"
                        : "border-[#E2DAD0] dark:border-zinc-800 bg-white/95 dark:bg-zinc-900 shadow-[0_4px_16px_rgba(0,0,0,0.05)] hover:border-[#38BDF8] dark:hover:border-[#38BDF8] hover:bg-[#F0F9FF] hover:shadow-[0_8px_20px_rgba(0,0,0,0.06)]"
                    }`}
                  >
                    <div
                      className={`flex h-6.5 w-6.5 items-center justify-center rounded-xl border transition-colors duration-300 ${
                        isFocused
                          ? "bg-[#E0F2FE] border-[#38BDF8] text-[#0EA5E9]"
                          : "bg-[#F5F1E8] dark:bg-zinc-800 border-[#E2DAD0] text-ink-muted"
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5" strokeWidth={1.5} />
                    </div>
                    <div className="text-left">
                      <p className="text-[11.5px] font-bold leading-none text-ink">
                        {app.name}
                      </p>
                      <p className="text-[9px] font-mono text-ink-muted/80 mt-0.5">
                        {app.label}
                      </p>
                    </div>

                    {/* Active Emerald Green Connected Status Indicator */}
                    <span className="h-1.5 w-1.5 rounded-full bg-[#10B981] animate-pulse" />
                  </div>
                </motion.div>
              </div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
