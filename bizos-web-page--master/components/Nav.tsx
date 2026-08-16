"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const LINKS = [
  { href: "#features", label: "Features" },
  { href: "#architecture", label: "Architecture" },
  { href: "#solutions", label: "Solutions" },
  { href: "#pricing", label: "Pricing" },
];

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut", delay: 0.15 }}
      className="fixed inset-x-0 top-4 z-50 flex justify-center px-4"
    >
      <nav
        className={`glass-panel flex w-full max-w-4xl items-center justify-between px-5 py-2.5 transition-shadow duration-300 ${
          scrolled ? "shadow-glow-blue" : ""
        }`}
      >
        <a href="#top" className="flex items-center gap-2.5">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-core-cyan opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-core-cyan" />
          </span>
          <span className="font-display text-[15px] font-medium tracking-tight text-ink">
            BizOS
          </span>
        </a>

        <div className="hidden items-center gap-7 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[13px] text-ink-muted transition-colors hover:text-ink"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <a
            href="#docs"
            className="hidden text-[13px] text-ink-muted transition-colors hover:text-ink sm:block"
          >
            Docs
          </a>
          <a
            href="/dashboard"
            className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-1.5 text-[13px] text-ink transition-colors hover:border-core-cyan/40 hover:bg-core-cyan/[0.08]"
          >
            Log in
          </a>
        </div>
      </nav>
    </motion.header>
  );
}
