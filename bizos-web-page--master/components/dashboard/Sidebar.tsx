"use client";

import { useState } from "react";
import { motion, AnimatePresence, LayoutGroup } from "framer-motion";
import { useRouter, usePathname } from "next/navigation";
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

import Link from "next/link";

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
  const router = useRouter();
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(false);
  const [active, setActive] = useState("dashboard");
  const [toast, setToast] = useState<string | null>(null);

  // Permanently visible on dashboard and utility surfaces (/dashboard & /app/*), hidden on public landing page site
  const isDashboardOrApp = pathname === "/dashboard" || pathname.startsWith("/dashboard/") || pathname.startsWith("/app/");
  if (!isDashboardOrApp) {
    return null;
  }

  function handleSelect(item: (typeof ITEMS)[number]) {
    if (item.id === "dashboard") {
      setActive("dashboard");
      router.push("/dashboard");
      return;
    }
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
        transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
        className="glass-panel fixed left-4 top-4 bottom-4 z-40 flex flex-col overflow-hidden py-4 border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.04)]"
      >
        <Link href="/dashboard" className="mb-6 flex items-center gap-3 px-5 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50 rounded-lg">
          <span className="relative flex h-2.5 w-2.5 shrink-0">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#0EA5E9] opacity-60 motion-reduce:animate-none" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#0EA5E9]" />
          </span>
          <AnimatePresence>
            {expanded && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="whitespace-nowrap font-display text-[15px] font-bold text-ink tracking-tight"
              >
                BizOS
              </motion.span>
            )}
          </AnimatePresence>
        </Link>

        <LayoutGroup>
          <nav className="flex flex-1 flex-col gap-1.5 px-3">
            {ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = active === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item)}
                  className="relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-colors cursor-pointer group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50 active:scale-[0.98]"
                >
                  {isActive && (
                    <motion.span
                      layoutId="sidebar-active"
                      className="absolute inset-0 rounded-xl border border-[#38BDF8] bg-[#F0F9FF] dark:bg-[#0F172A] shadow-sm"
                      transition={{ type: "spring", stiffness: 380, damping: 32 }}
                    />
                  )}
                  <Icon
                    className={`relative z-10 h-[18px] w-[18px] shrink-0 transition-colors duration-200 ${
                      isActive ? "text-[#0EA5E9] dark:text-[#38BDF8]" : "text-ink-muted group-hover:text-ink"
                    }`}
                    strokeWidth={1.75}
                  />
                  <AnimatePresence>
                    {expanded && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className={`relative z-10 whitespace-nowrap text-[13px] font-medium transition-colors duration-200 ${
                          isActive ? "text-ink font-semibold" : "text-ink-muted group-hover:text-ink"
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

        <div className="mt-2 border-t border-[#E6DFD3] dark:border-zinc-800 px-3 pt-3">
          <button
            onClick={() => handleSelect({ id: "settings", label: "Settings", icon: Settings, live: false })}
            className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-ink-muted transition-colors hover:text-ink cursor-pointer w-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50 active:scale-[0.98]"
          >
            <Settings className="h-[18px] w-[18px] shrink-0" strokeWidth={1.75} />
            <AnimatePresence>
              {expanded && (
                <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="whitespace-nowrap text-[13px] font-medium">
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
            className="glass-panel fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-2xl border-2 border-[#E6DFD3] dark:border-zinc-700 bg-white/95 dark:bg-zinc-900/95 px-5 py-3 text-[13px] font-medium text-ink shadow-xl backdrop-blur-xl"
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
