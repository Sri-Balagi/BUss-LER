"use client";

import React, { useState } from "react";
import { useBusiness } from "@/lib/business-context";
import { useOnboarding } from "@/lib/onboarding-context";
import { Mail, Phone, CheckCircle2, Sparkles, ArrowRight } from "lucide-react";

export function NewAccountPage() {
  const { profile } = useBusiness();
  const { data } = useOnboarding();
  const [callRequested, setCallRequested] = useState(false);

  const businessName = data.businessName || profile.businessName || "Your Enterprise";
  const userEmail = profile.email || "your email";

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] p-4 sm:p-6">
      {/* Clean Card displaying ONLY Business Name & Contact Us Activation */}
      <div className="glass-panel w-full max-w-lg rounded-[28px] border-2 border-[#E6DFD3] dark:border-zinc-800 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 p-8 sm:p-10 shadow-[0_8px_32px_rgba(0,0,0,0.06)] backdrop-blur-xl space-y-7 text-center relative overflow-hidden transition-all duration-300">
        
        {/* Top Pill Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-300 font-mono text-[11px] font-semibold uppercase tracking-wider">
          <Sparkles className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400 animate-pulse" />
          <span>ENTERPRISE SETUP PENDING</span>
        </div>

        {/* Business Name Heading */}
        <div className="space-y-2">
          <h1 className="font-display text-3xl font-bold tracking-tight text-ink dark:text-white">
            {businessName}
          </h1>
          <p className="text-xs text-ink-muted dark:text-zinc-400 leading-relaxed max-w-sm mx-auto">
            Your account (<strong className="text-ink dark:text-white font-medium">{userEmail}</strong>) is registered. Please contact us to activate your live AI Digital Twin and workspace.
          </p>
        </div>

        {/* Contact Us Box ONLY */}
        <div className="rounded-2xl border border-amber-500/30 bg-[#FFFBEB] dark:bg-amber-950/20 p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-center gap-2 text-amber-900 dark:text-amber-300 font-bold text-sm">
            <Phone className="h-4 w-4 text-amber-600 dark:text-amber-400" />
            <span>Please Contact Us To Complete Activation</span>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-5 pt-1 text-xs font-medium">
            <div className="flex items-center gap-1.5 text-ink dark:text-white">
              <Mail className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0" />
              <span>Email: <strong className="text-amber-800 dark:text-amber-300">rsribalagi@gmail.com</strong></span>
            </div>
            <div className="flex items-center gap-1.5 text-ink dark:text-white">
              <Phone className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0" />
              <span>Phone: <strong className="text-amber-800 dark:text-amber-300">+91 98765 43210</strong></span>
            </div>
          </div>

          <div className="pt-2">
            {callRequested ? (
              <div className="inline-flex items-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-5 py-3 text-xs font-semibold text-emerald-700 dark:text-emerald-400 shadow-sm">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>Setup Call Requested! Our team will contact you shortly.</span>
              </div>
            ) : (
              <button
                onClick={() => setCallRequested(true)}
                className="inline-flex items-center gap-2 rounded-xl bg-accent hover:bg-accent/90 text-white px-6 py-3 text-xs font-bold shadow-md transition-all active:scale-95 cursor-pointer"
              >
                <Phone className="h-4 w-4" />
                <span>Request Immediate Setup Call</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Footer */}
        <p className="font-mono text-[11px] text-ink-muted dark:text-zinc-500">
          BizOS v6.0.0 · Dedicated Enterprise Setup
        </p>
      </div>
    </div>
  );
}
