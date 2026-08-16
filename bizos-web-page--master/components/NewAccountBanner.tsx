"use client";

import React from "react";
import { useBusiness } from "@/lib/business-context";
import { Mail, Phone, CheckCircle2, Clock, Sparkles } from "lucide-react";

export function NewAccountBanner() {
  const { isPrimaryAccount, profile, requestOnboardingCall, callRequested } = useBusiness();

  if (isPrimaryAccount) {
    return null; // Hotel Balagi Bhavan has full direct hardcoded access with zero banners
  }

  return (
    <div className="mb-6 overflow-hidden rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-orange-500/5 to-transparent p-5 backdrop-blur-xl transition-all shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-amber-500/30 bg-amber-500/20 text-amber-400">
            <Clock className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-display text-base font-semibold text-primary">
                Enterprise Setup Pending — {profile.businessName}
              </h3>
              <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-0.5 text-[10px] font-medium text-amber-300">
                <Sparkles className="h-3 w-3" /> Request Queued
              </span>
            </div>
            <p className="mt-1 text-xs text-secondary leading-relaxed max-w-2xl">
              Your account (<span className="text-primary font-medium">{profile.email}</span>) has been verified! To construct your custom AI Knowledge Graph, 3D Memory Network, and POS/ERP connectors, our engineering team will connect with you.
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-4 text-xs font-medium text-amber-300/90">
              <div className="flex items-center gap-1.5">
                <Mail className="h-3.5 w-3.5 text-amber-400" />
                <span>Contact Email: <strong>{profile.contactEmail}</strong></span>
              </div>
              <div className="flex items-center gap-1.5">
                <Phone className="h-3.5 w-3.5 text-amber-400" />
                <span>Support Line: <strong>{profile.contactPhone}</strong></span>
              </div>
            </div>
          </div>
        </div>

        <div className="shrink-0 flex items-center">
          {callRequested ? (
            <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/20 px-4 py-2.5 text-xs font-medium text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
              <span>Call Requested! Team will reach out within 2 hours.</span>
            </div>
          ) : (
            <button
              onClick={requestOnboardingCall}
              className="group relative flex items-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2.5 text-xs font-semibold text-white shadow-lg transition-all hover:from-amber-400 hover:to-orange-400 active:scale-95"
            >
              <Phone className="h-3.5 w-3.5" />
              <span>Request Immediate Setup Call</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
