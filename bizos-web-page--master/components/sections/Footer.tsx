"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Cpu } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full border-t border-[color:var(--border-color)] bg-[#C8C5CC] dark:bg-[#12110F]">
      <div className="mx-auto max-w-6xl px-6 py-16 md:py-20">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-12 mb-16">
          {/* Brand Column */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="md:col-span-2 space-y-4"
          >
            <Link href="/" className="inline-flex items-center gap-3 group">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent text-white shadow-[0_2px_10px_rgba(232,123,42,0.3)] transition-transform duration-300 group-hover:scale-105">
                <Cpu className="h-5 w-5" strokeWidth={1.5} />
              </div>
              <span className="font-display text-[20px] font-semibold tracking-tight text-ink">
                Biz<span className="text-accent font-mono font-normal">OS</span>
              </span>
            </Link>
            <p className="text-[14px] leading-relaxed text-ink-muted font-light max-w-sm">
              The Artificial Intelligence Operating System. Transforming fragmented enterprise software into a single cognitive runtime.
            </p>
          </motion.div>

          {/* Nav Links Column 1 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-4"
          >
            <p className="font-mono text-[11px] uppercase tracking-widest text-ink font-semibold">Architecture</p>
            <ul className="space-y-2.5 text-[14px] text-ink-muted font-light">
              <li><Link href="#top" className="hover:text-ink transition-colors">Cognitive Runtime</Link></li>
              <li><Link href="#architecture" className="hover:text-ink transition-colors">Memory Galaxy</Link></li>
              <li><Link href="#features" className="hover:text-ink transition-colors">Agent Pipeline</Link></li>
              <li><Link href="#features" className="hover:text-ink transition-colors">Governance Stream</Link></li>
            </ul>
          </motion.div>

          {/* Nav Links Column 2 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-4"
          >
            <p className="font-mono text-[11px] uppercase tracking-widest text-ink font-semibold">Platform</p>
            <ul className="space-y-2.5 text-[14px] text-ink-muted font-light">
              <li><Link href="/dashboard" className="hover:text-ink transition-colors">Dashboard</Link></li>
              <li><Link href="/app/memory" className="hover:text-ink transition-colors">Memory Studio</Link></li>
              <li><Link href="/app/decision" className="hover:text-ink transition-colors">Decision Center</Link></li>
              <li><Link href="/app/audit" className="hover:text-ink transition-colors">Audit Ledger</Link></li>
            </ul>
          </motion.div>

          {/* Nav Links Column 3 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-4"
          >
            <p className="font-mono text-[11px] uppercase tracking-widest text-ink font-semibold">Company</p>
            <ul className="space-y-2.5 text-[14px] text-ink-muted font-light">
              <li><a href="mailto:hello@bizos.ai" className="hover:text-ink transition-colors">Contact Us</a></li>
              <li><Link href="/auth/signin" className="hover:text-ink transition-colors">Sign In</Link></li>
              <li><Link href="/auth/signup" className="hover:text-ink transition-colors">Create Account</Link></li>
            </ul>
          </motion.div>
        </div>

        {/* Bottom Bar */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="pt-8 border-t border-[color:var(--border-color)] flex flex-col md:flex-row items-center justify-between gap-4 text-[13px] text-ink-muted font-light"
        >
          <p>© {new Date().getFullYear()} BizOS Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span className="hover:text-ink transition-colors cursor-pointer">Privacy Policy</span>
            <span className="hover:text-ink transition-colors cursor-pointer">Terms of Service</span>
            <span className="hover:text-ink transition-colors cursor-pointer">Security Policy</span>
          </div>
        </motion.div>
      </div>
    </footer>
  );
}
