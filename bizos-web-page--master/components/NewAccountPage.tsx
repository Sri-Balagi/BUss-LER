"use client";

import React, { useState } from "react";
import { useBusiness } from "@/lib/business-context";
import { useOnboarding } from "@/lib/onboarding-context";
import { Mail, Phone, CheckCircle2, Sparkles, ArrowRight, ShieldAlert } from "lucide-react";

export function NewAccountPage() {
  const { profile } = useBusiness();
  const { data } = useOnboarding();
  const [callRequested, setCallRequested] = useState(false);

  const businessName = data.businessName || profile.businessName || "Your Enterprise";
  const userEmail = profile.email || "your email";

  return (
    <div className="flex flex-col items-center justify-center min-h-[75vh] p-4 sm:p-6 w-full">
      {/* Centered Clean Card displaying ONLY Contact Navdeep for Customized BizOS */}
      <div className="glass-panel w-full max-w-xl rounded-[32px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 p-8 sm:p-10 shadow-[0_12px_40px_rgba(0,0,0,0.08)] backdrop-blur-2xl space-y-7 text-center relative overflow-hidden transition-all duration-300">
        
        {/* Top Glow & Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-300 font-mono text-[11px] font-bold uppercase tracking-wider">
          <Sparkles className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400 animate-pulse" />
          <span>Customized BizOS Activation</span>
        </div>

        {/* Business & Account Greeting */}
        <div className="space-y-3">
          <h1 className="font-display text-3xl font-bold tracking-tight text-ink dark:text-white">
            {businessName}
          </h1>
          <p className="text-sm font-mono text-amber-800 dark:text-amber-300 bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 max-w-md mx-auto leading-relaxed">
            Contact Navdeep via the number <strong className="text-ink dark:text-white font-bold">8438426511</strong> or the email <strong className="text-ink dark:text-white font-bold">iamlnavdeep@gmail.com</strong> for customized BizOS.
          </p>
        </div>

        {/* Contact Navdeep Box */}
        <div className="rounded-2xl border-2 border-amber-500/30 bg-white/80 dark:bg-zinc-800/80 p-6 space-y-5 shadow-sm text-left">
          <div className="flex items-center gap-2 text-ink dark:text-white font-display font-bold text-base border-b border-zinc-200 dark:border-zinc-700 pb-3">
            <ShieldAlert className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0" />
            <span>Dedicated Activation Contact</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
            <div className="flex flex-col gap-1 p-3 rounded-xl bg-amber-50 dark:bg-zinc-900 border border-amber-200 dark:border-zinc-700">
              <span className="text-ink-muted text-[10px] uppercase tracking-wider font-semibold">Phone Support</span>
              <div className="flex items-center gap-2 text-ink dark:text-white font-bold text-sm">
                <Phone className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0" />
                <a href="tel:8438426511" className="hover:underline">8438426511</a>
              </div>
            </div>

            <div className="flex flex-col gap-1 p-3 rounded-xl bg-amber-50 dark:bg-zinc-900 border border-amber-200 dark:border-zinc-700">
              <span className="text-ink-muted text-[10px] uppercase tracking-wider font-semibold">Direct Email</span>
              <div className="flex items-center gap-2 text-ink dark:text-white font-bold text-xs truncate">
                <Mail className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0" />
                <a href="mailto:iamlnavdeep@gmail.com" className="hover:underline truncate">iamlnavdeep@gmail.com</a>
              </div>
            </div>
          </div>

          <div className="pt-2 text-center">
            {callRequested ? (
              <div className="inline-flex items-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-5 py-3 text-xs font-semibold text-emerald-700 dark:text-emerald-400 shadow-sm w-full justify-center">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>Navdeep has been notified! You will receive a call shortly.</span>
              </div>
            ) : (
              <button
                onClick={() => setCallRequested(true)}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-accent hover:bg-accent/90 text-white px-6 py-3.5 text-xs font-bold shadow-md transition-all active:scale-95 cursor-pointer w-full"
              >
                <Phone className="h-4 w-4" />
                <span>Contact Navdeep For Customized Setup</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Account Metadata Footer */}
        <p className="font-mono text-[11px] text-ink-muted dark:text-zinc-500">
          Account: {userEmail} · BizOS Customized Enterprise Edition
        </p>
      </div>
    </div>
  );
}
