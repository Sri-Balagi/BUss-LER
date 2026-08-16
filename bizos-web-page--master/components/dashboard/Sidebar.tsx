"use client";

import { useState } from "react";
import { motion, AnimatePresence, LayoutGroup } from "framer-motion";
import {
  LayoutDashboard,
  Workflow,
  Activity,
  Bot,
  Orbit,
  Share2,
  Target,
  GitBranch,
  Server,
  Gauge,
  ScrollText,
  Settings,
} from "lucide-react";

const ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, live: true },
  { id: "workflow", label: "Workflow Studio", icon: Workflow, live: false },
  { id: "runtime", label: "Runtime Monitor", icon: Activity, live: false },
  { id: "agents", label: "Agents", icon: Bot, live: false },
  { id: "memory", label: "Memory Galaxy", icon: Orbit, live: false },
  { id: "knowledge", label: "Knowledge Graph", icon: Share2, live: false },
  { id: "goals", label: "Goal Manager", icon: Target, live: false },
  { id: "decisions", label: "Decision Center", icon: GitBranch, live: false },
  { id: "infra", label: "Infrastructure", icon: Server, live: false },
  { id: "metrics", label: "Metrics", icon: Gauge, live: false },
  { id: "audit", label: "Audit Logs", icon: ScrollText, live: false },
];

export default function Sidebar() {
  const [expanded, setExpanded] = useState(false);
  const [active, setActive] = useState("dashboard");
  const [toast, setToast] = useState<string | null>(null);

  function handleSelect(item: (typeof ITEMS)[number]) {
    if (!item.live) {
      setToast(`${item.label} isn't wired up yet — dashboard is the only live surface so far.`);
      window.clearTimeout((handleSelect as any)._t);
      (handleSelect as any)._t = window.setTimeout(() => setToast(null), 2600);
      return;
    }
    setActive(item.id);
  }

  return (
    <>
      <motion.aside
        onMouseEnter={() => setExpanded(true)}
        onMouseLeave={() => setExpanded(false)}
        animate={{ width: expanded ? 216 : 72 }}
        transition={{ duration: 0.28, ease: "easeOut" }}
        className="glass-panel fixed left-4 top-4 bottom-4 z-40 flex flex-col overflow-hidden py-4"
      >
        <div className="mb-6 flex items-center gap-3 px-5">
          <span className="relative flex h-2 w-2 shrink-0">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-core-cyan opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-core-cyan" />
          </span>
          <AnimatePresence>
            {expanded && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="whitespace-nowrap font-display text-[14px] font-medium text-ink"
              >
                BizOS
              </motion.span>
            )}
          </AnimatePresence>
        </div>

        <LayoutGroup>
          <nav className="flex flex-1 flex-col gap-1 px-3">
            {ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = active === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item)}
                  className="relative flex items-center gap-3 rounded-xl px-2.5 py-2.5 text-left transition-colors"
                >
                  {isActive && (
                    <motion.span
                      layoutId="sidebar-active"
                      className="absolute inset-0 rounded-xl border border-core-cyan/20 bg-core-cyan/[0.08]"
                      transition={{ type: "spring", stiffness: 350, damping: 30 }}
                    />
                  )}
                  <Icon
                    className={`relative z-10 h-[18px] w-[18px] shrink-0 ${
                      isActive ? "text-core-cyan" : "text-ink-muted"
                    }`}
                    strokeWidth={1.6}
                  />
                  <AnimatePresence>
                    {expanded && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className={`relative z-10 whitespace-nowrap text-[13px] ${
                          isActive ? "text-ink" : "text-ink-muted"
                        }`}
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                  {!item.live && expanded && (
                    <span className="relative z-10 ml-auto font-mono text-[9px] uppercase tracking-wider text-ink-faint">
                      soon
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </LayoutGroup>

        <div className="mt-2 border-t border-white/[0.06] px-3 pt-3">
          <button
            onClick={() => handleSelect({ id: "settings", label: "Settings", icon: Settings, live: false })}
            className="flex items-center gap-3 rounded-xl px-2.5 py-2.5 text-ink-muted transition-colors hover:text-ink"
          >
            <Settings className="h-[18px] w-[18px] shrink-0" strokeWidth={1.6} />
            <AnimatePresence>
              {expanded && (
                <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="whitespace-nowrap text-[13px]">
                  Settings
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </motion.aside>

      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 12 }}
            className="glass-panel fixed bottom-6 left-1/2 z-50 -translate-x-1/2 px-5 py-3 text-[13px] text-ink-muted"
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
