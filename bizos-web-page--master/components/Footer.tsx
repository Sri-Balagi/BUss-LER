"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

const COLUMNS = [
  {
    heading: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "Architecture", href: "#architecture" },
      { label: "Solutions", href: "#solutions" },
      { label: "Pricing", href: "#pricing" },
    ],
  },
  {
    heading: "Company",
    links: [
      { label: "About", href: "#about" },
      { label: "Docs", href: "#docs" },
      { label: "Contact", href: "#contact" },
    ],
  },
];

export default function Footer() {
  return (
    <footer id="contact" className="relative mx-auto max-w-6xl px-6 pb-16 pt-8">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="glass-panel mb-16 flex flex-col items-start justify-between gap-8 overflow-hidden p-10 sm:flex-row sm:items-center sm:p-14"
      >
        <div>
          <p className="eyebrow mb-4">About / Contact</p>
          <h2 className="max-w-md font-display text-[28px] font-medium leading-tight text-ink sm:text-[34px]">
            Ready to watch it think?
          </h2>
          <p className="mt-3 max-w-sm text-[14px] leading-relaxed text-ink-muted">
            Write to{" "}
            <a href="mailto:hello@bizos.ai" className="text-ink underline decoration-white/20 underline-offset-4">
              hello@bizos.ai
            </a>{" "}
            and we'll set up a walkthrough of a live run.
          </p>
        </div>
        <a
          href="mailto:hello@bizos.ai"
          className="group flex shrink-0 items-center gap-2 rounded-full bg-ink px-7 py-3.5 text-[14px] font-medium text-void transition-transform hover:scale-[1.02]"
        >
          Request access
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
        </a>
      </motion.div>

      <div className="flex flex-col gap-10 border-t border-white/[0.06] pt-10 sm:flex-row sm:justify-between">
        <div className="max-w-xs">
          <span className="font-display text-[15px] font-medium text-ink">BizOS</span>
          <p className="mt-3 text-[13px] leading-relaxed text-ink-muted">
            An operating system for the parts of a business that used to
            require a person to think first.
          </p>
        </div>

        <div className="flex gap-16">
          {COLUMNS.map((col) => (
            <div key={col.heading} id={col.heading === "Company" ? "about" : undefined}>
              <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
                {col.heading}
              </span>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      id={link.label === "Docs" ? "docs" : undefined}
                      className="text-[13px] text-ink-muted transition-colors hover:text-ink"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <p className="mt-12 font-mono text-[11px] text-ink-faint">
        © {new Date().getFullYear()} BizOS. All systems nominal.
      </p>
    </footer>
  );
}
