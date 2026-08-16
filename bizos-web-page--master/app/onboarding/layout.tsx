"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ShieldCheck, Cpu } from "lucide-react";

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center p-4 sm:p-8">
      {/* Background ambient lighting */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full bg-accent/10 blur-[140px]" />
        <div className="absolute bottom-10 right-10 h-[350px] w-[350px] rounded-full bg-[#00F0FF]/10 blur-[120px]" />
      </div>

      {/* Top Navbar */}
      <header className="relative z-10 w-full max-w-4xl mb-8 flex items-center justify-between px-2">
        <Link href="/" className="flex items-center gap-2.5 group">
          <span className="relative flex h-3 w-3">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-accent" />
          </span>
          <span className="font-display text-xl font-semibold tracking-tight text-primary transition-colors group-hover:text-accent">
            BizOS
          </span>
          <span className="rounded-full bg-white/10 px-2 py-0.5 font-mono text-[10px] text-secondary">
            ONBOARDING WIZARD
          </span>
        </Link>

        <div className="flex items-center gap-4 text-xs font-mono text-tertiary">
          <span className="flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5 text-accent" />
            Digital Twin Setup
          </span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 w-full">{children}</main>
    </div>
  );
}
