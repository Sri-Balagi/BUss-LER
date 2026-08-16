"use client";

import { motion } from "framer-motion";
import { Circle, Globe, Hexagon, Layers, Cpu, Settings, Activity } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/app/core", icon: Circle, label: "Core Runtime", state: "thought" },
  { href: "/app/memory", icon: Globe, label: "Memory Layer", state: "memory" },
  { href: "/app/knowledge", icon: Hexagon, label: "Knowledge Layer", state: "knowledge" },
  { href: "/app/decision", icon: Layers, label: "Decision Layer", state: "decision" },
  { href: "/app/infrastructure", icon: Cpu, label: "Infrastructure", state: "warning" },
  { href: "/app/audit", icon: Activity, label: "Audit Stream", state: "thought" },
];

export function Navigator() {
  const pathname = usePathname();

  // Don't show navigator on the public landing page or boot sequence
  if (pathname === "/" || pathname === "/boot") return null;

  return (
    <motion.nav
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 250, damping: 25 }}
      className="fixed left-6 top-1/2 -translate-y-1/2 z-50 flex flex-col gap-4 p-3 glass-panel rounded-full"
    >
      {NAV_ITEMS.map((item) => {
        const isActive = pathname.startsWith(item.href);
        const Icon = item.icon;

        return (
          <Link key={item.href} href={item.href}>
            <motion.div
              className={`relative flex items-center justify-center w-12 h-12 rounded-full transition-colors ${
                isActive ? "bg-white/[0.08]" : "hover:bg-white/[0.04]"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon
                className={`w-5 h-5 transition-colors ${
                  isActive ? "text-primary" : "text-secondary"
                }`}
              />
              {isActive && (
                <motion.div
                  layoutId="navigator-indicator"
                  className="absolute inset-0 rounded-full"
                  style={{
                    boxShadow: `0 0 20px -5px var(--glow-${item.state}, #00F0FF)`,
                    border: `1px solid var(--glow-${item.state}, #00F0FF)`,
                  }}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
            </motion.div>
          </Link>
        );
      })}
      
      <div className="w-8 h-[1px] bg-white/[0.1] mx-auto my-2" />
      
      <Link href="/app/settings">
        <motion.div
          className="relative flex items-center justify-center w-12 h-12 rounded-full hover:bg-white/[0.04] transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Settings className="w-5 h-5 text-tertiary hover:text-secondary transition-colors" />
        </motion.div>
      </Link>
    </motion.nav>
  );
}
