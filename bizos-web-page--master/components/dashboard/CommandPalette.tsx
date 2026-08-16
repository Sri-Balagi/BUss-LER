"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Search,
  LayoutDashboard,
  Workflow,
  Activity,
  Bot,
  Orbit,
  Share2,
  Target,
  GitBranch,
  Server,
  ScrollText,
  Settings,
  Sun,
  X,
} from "lucide-react";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

const COMMANDS = [
  { id: "dashboard", href: "/dashboard", label: "Dashboard Overview", icon: LayoutDashboard, section: "Navigation" },
  { id: "workflow", href: "/app/core", label: "Workflow Studio", icon: Workflow, section: "Navigation" },
  { id: "runtime", href: "/app/core", label: "Runtime Monitor", icon: Activity, section: "Navigation" },
  { id: "agents", href: "/app/core", label: "Agents Fleet", icon: Bot, section: "Navigation" },
  { id: "memory", href: "/app/memory", label: "Memory Galaxy", icon: Orbit, section: "Navigation" },
  { id: "knowledge", href: "/app/knowledge", label: "Knowledge Graph", icon: Share2, section: "Navigation" },
  { id: "goals", href: "/app/decision", label: "Goal Manager", icon: Target, section: "Navigation" },
  { id: "decisions", href: "/app/decision", label: "Decision Center", icon: GitBranch, section: "Navigation" },
  { id: "infra", href: "/app/infrastructure", label: "Infrastructure Health", icon: Server, section: "Navigation" },
  { id: "audit", href: "/app/audit", label: "Audit Stream Logs", icon: ScrollText, section: "Navigation" },
  { id: "settings", href: "/app/settings", label: "System Settings", icon: Settings, section: "Utilities" },
];

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const filteredCommands = COMMANDS.filter(
    (cmd) =>
      cmd.label.toLowerCase().includes(query.toLowerCase()) ||
      cmd.section.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          setQuery("");
          setSelectedIndex(0);
        }
      }
      if (!isOpen) return;

      if (e.key === "Escape") {
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % Math.max(1, filteredCommands.length));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % Math.max(1, filteredCommands.length));
      } else if (e.key === "Enter" && filteredCommands[selectedIndex]) {
        e.preventDefault();
        handleSelect(filteredCommands[selectedIndex].href);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, filteredCommands, selectedIndex]);

  const toggleTheme = () => {
    if (document.documentElement.classList.contains("dark")) {
      document.documentElement.classList.remove("dark");
    } else {
      document.documentElement.classList.add("dark");
    }
    onClose();
  };

  const handleSelect = (href?: string, action?: () => void) => {
    if (action) {
      action();
    } else if (href) {
      router.push(href);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/60 backdrop-blur-md"
        />

        {/* Command Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: -8 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: -8 }}
          transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full max-w-xl overflow-hidden rounded-[28px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 p-5 shadow-2xl backdrop-blur-2xl"
        >
          {/* Search Header */}
          <div className="flex items-center gap-3 border-b border-[#E2DAD0] dark:border-zinc-800 pb-3.5 px-2">
            <Search className="h-5 w-5 text-[#0EA5E9] shrink-0" strokeWidth={1.75} />
            <input
              type="text"
              autoFocus
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelectedIndex(0);
              }}
              placeholder="Type a command or search dashboard..."
              className="w-full bg-transparent font-medium text-sm text-ink placeholder:text-ink-muted focus:outline-none"
            />
            <button
              onClick={onClose}
              className="p-1 rounded-lg border border-[#E2DAD0] dark:border-zinc-700 bg-white/80 dark:bg-zinc-800 text-ink-muted hover:text-ink active:scale-95 transition-all duration-200 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]/50"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Quick Actions / Results List */}
          <div className="mt-3 max-h-80 overflow-y-auto space-y-1.5 scrollbar-none px-1">
            {/* Theme Toggle Command */}
            <div
              onClick={toggleTheme}
              className="flex items-center justify-between rounded-2xl px-3.5 py-2.5 cursor-pointer text-ink-muted hover:text-ink hover:bg-[#F0F9FF] dark:hover:bg-[#0F172A] border border-transparent hover:border-[#38BDF8] active:scale-[0.99] transition-all duration-200"
            >
              <div className="flex items-center gap-3">
                <Sun className="h-4 w-4 text-accent" strokeWidth={1.75} />
                <span className="text-xs font-semibold text-ink">Toggle Theme Mode (Light / Dark)</span>
              </div>
              <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-accent">Action</span>
            </div>

            {filteredCommands.map((cmd, idx) => {
              const Icon = cmd.icon;
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={cmd.id}
                  onClick={() => handleSelect(cmd.href)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between rounded-2xl px-3.5 py-2.5 cursor-pointer transition-all duration-200 ease-[0.16,1,0.3,1] ${
                    isSelected
                      ? "bg-[#F0F9FF] dark:bg-[#0F172A] text-[#0EA5E9] dark:text-[#38BDF8] border border-[#38BDF8]"
                      : "text-ink-muted hover:text-ink hover:bg-white/80 dark:hover:bg-zinc-800/80 border border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-4 w-4 ${isSelected ? "text-[#0EA5E9] dark:text-[#38BDF8]" : "text-ink-muted"}`} strokeWidth={1.75} />
                    <span className="text-xs font-semibold">{cmd.label}</span>
                  </div>
                  <span className="font-mono text-[10px] font-medium uppercase tracking-wider text-ink-muted">
                    {cmd.section}
                  </span>
                </div>
              );
            })}

            {filteredCommands.length === 0 && (
              <div className="py-8 text-center text-xs text-ink-muted font-light">
                No commands matching &ldquo;{query}&rdquo;
              </div>
            )}
          </div>

          {/* Footer Shortcuts */}
          <div className="mt-3 border-t border-[#E2DAD0] dark:border-zinc-800 pt-3 flex items-center justify-between px-2 font-mono text-[11px] text-ink-muted">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded border border-[#E2DAD0] dark:border-zinc-700 bg-white/80 dark:bg-zinc-800 text-[10px] font-semibold text-ink">↑↓</kbd> navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded border border-[#E2DAD0] dark:border-zinc-700 bg-white/80 dark:bg-zinc-800 text-[10px] font-semibold text-ink">↵</kbd> select
              </span>
            </div>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded border border-[#E2DAD0] dark:border-zinc-700 bg-white/80 dark:bg-zinc-800 text-[10px] font-semibold text-ink">ESC</kbd> close
            </span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
