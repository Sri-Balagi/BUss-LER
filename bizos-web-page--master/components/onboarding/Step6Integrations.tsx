"use client";

import React, { useState } from "react";
import { useOnboarding } from "@/lib/onboarding-context";
import { useBusiness } from "@/lib/business-context";
import { ArrowRight, ArrowLeft, Check, Plus, Shield, ExternalLink, Lock } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface StepProps {
  onNext: () => void;
  onBack: () => void;
}

interface IntegrationDef {
  name: string;
  category: string;
  badge?: string;
  color: string;
}

const INTEGRATIONS: IntegrationDef[] = [
  { name: "Gmail", category: "Email & Comm", color: "from-red-500/20 to-orange-500/20" },
  { name: "Google Drive", category: "Docs & Memory", color: "from-green-500/20 to-emerald-500/20" },
  { name: "Outlook", category: "Email & Comm", color: "from-blue-500/20 to-cyan-500/20" },
  { name: "Slack", category: "Team Messaging", color: "from-purple-500/20 to-pink-500/20" },
  { name: "WhatsApp", category: "Customer Support", color: "from-emerald-500/20 to-teal-500/20" },
  { name: "Stripe", category: "Finance & Billing", color: "from-indigo-500/20 to-purple-500/20" },
  { name: "Shopify", category: "E-commerce", color: "from-lime-500/20 to-emerald-500/20" },
  { name: "GitHub", category: "Engineering", color: "from-gray-500/20 to-slate-500/20" },
  { name: "Jira", category: "Project Tracking", color: "from-blue-600/20 to-cyan-600/20" },
  { name: "Salesforce", category: "Enterprise CRM", color: "from-sky-500/20 to-blue-500/20" },
  { name: "QuickBooks", category: "Accounting", color: "from-green-600/20 to-emerald-600/20" },
];

export function Step6Integrations({ onNext, onBack }: StepProps) {
  const { data, toggleIntegration, updateData } = useOnboarding();
  const { profile } = useBusiness();
  const [showGoogleAuthModal, setShowGoogleAuthModal] = useState(false);

  const userEmail = profile.email || "enterprise@company.com";

  const selectAll = () => {
    updateData({ selectedIntegrations: INTEGRATIONS.map((i) => i.name) });
  };

  const clearAll = () => {
    updateData({ selectedIntegrations: [] });
  };

  const handleProceed = () => {
    // Prompt for Google Auth Consent Permission Modal before completing step
    setShowGoogleAuthModal(true);
  };

  const handleGoogleAllow = () => {
    setShowGoogleAuthModal(false);
    onNext();
  };

  const handleGoogleDeny = () => {
    setShowGoogleAuthModal(false);
    onNext();
  };

  return (
    <div className="flex flex-col max-w-3xl mx-auto py-2 relative">
      <div className="text-center mb-6">
        <p className="eyebrow mb-2">STEP 6 OF 7 • ECOSYSTEM INTEGRATIONS</p>
        <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-primary">
          Connect Your Tools
        </h2>
        <p className="mt-1.5 text-xs text-secondary max-w-lg mx-auto">
          Select integrations for your Digital Twin to ingest live data streams. You can skip this step and configure them anytime later.
        </p>
      </div>

      {/* Select bar */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-mono text-tertiary">
          Connected: <strong className="text-accent">{data.selectedIntegrations.length}</strong> / {INTEGRATIONS.length} integrations
        </span>
        <div className="flex items-center gap-3 text-xs">
          <button
            type="button"
            onClick={selectAll}
            className="text-accent hover:underline font-medium cursor-pointer"
          >
            Select Popular
          </button>
          <span className="text-white/20">•</span>
          <button
            type="button"
            onClick={clearAll}
            className="text-secondary hover:text-primary transition-colors cursor-pointer"
          >
            Skip All
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {INTEGRATIONS.map((item) => {
          const isSelected = data.selectedIntegrations.includes(item.name);

          return (
            <div
              key={item.name}
              onClick={() => toggleIntegration(item.name)}
              className={`relative flex flex-col p-3.5 rounded-2xl border cursor-pointer transition-all duration-300 ${
                isSelected
                  ? "border-accent/40 bg-accent/[0.08] shadow-lg shadow-accent/5"
                  : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-display text-sm font-semibold text-primary">{item.name}</span>
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-full border transition-all ${
                    isSelected
                      ? "border-accent bg-accent text-white"
                      : "border-white/20 bg-transparent text-tertiary"
                  }`}
                >
                  {isSelected ? <Check className="h-3 w-3 stroke-[3]" /> : <Plus className="h-3 w-3" />}
                </div>
              </div>
              <span className="text-[10px] font-mono text-tertiary">{item.category}</span>
            </div>
          );
        })}
      </div>

      {/* Navigation */}
      <div className="mt-8 flex items-center justify-between pt-4 border-t border-white/10">
        <button
          type="button"
          onClick={onBack}
          className="flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-5 text-sm font-medium text-primary hover:bg-white/[0.08] transition-all cursor-pointer"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleProceed}
            className="flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-5 text-sm font-medium text-secondary hover:text-primary hover:bg-white/[0.08] transition-all cursor-pointer"
          >
            <span>Skip for now</span>
          </button>

          <button
            type="button"
            onClick={handleProceed}
            className="flex h-11 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover cursor-pointer"
          >
            <span>Generate Twin</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Google Auth Permission Modal */}
      <AnimatePresence>
        {showGoogleAuthModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white text-zinc-900 rounded-[28px] p-7 sm:p-8 max-w-md w-full shadow-2xl space-y-6 text-left border border-zinc-200"
            >
              {/* Google Brand Header */}
              <div className="flex items-center justify-between border-b border-zinc-100 pb-4">
                <div className="flex items-center gap-2.5">
                  <svg className="w-6 h-6" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                  </svg>
                  <span className="font-semibold text-sm text-zinc-700 font-sans">Sign in with Google</span>
                </div>
                <span className="text-xs text-zinc-400 font-mono">OAuth 2.0</span>
              </div>

              {/* Account Selection */}
              <div className="space-y-1">
                <h3 className="font-display text-lg font-bold text-zinc-900">
                  BizOS wants to access your Google Account
                </h3>
                <p className="text-xs text-zinc-500 font-mono">
                  Connecting account: <strong className="text-zinc-800">{userEmail}</strong>
                </p>
              </div>

              {/* Permissions list */}
              <div className="space-y-3 bg-zinc-50 rounded-2xl p-4 border border-zinc-200/80 text-xs">
                <p className="font-semibold text-zinc-700 flex items-center gap-1.5">
                  <Shield className="w-4 h-4 text-[#1A73E8]" />
                  This will allow BizOS to:
                </p>
                <ul className="space-y-2 text-zinc-600 pl-1">
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>Read, compose, and send emails from your Gmail account</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>See, edit, create, and delete files in your Google Drive</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>View and manage Google Calendar events and schedules</span>
                  </li>
                </ul>
              </div>

              {/* Security info */}
              <div className="flex items-center gap-2 text-[11px] text-zinc-500 font-mono">
                <Lock className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                <span>You can revoke access anytime in your Google Security settings.</span>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleGoogleDeny}
                  className="px-4 py-2.5 rounded-xl border border-zinc-300 text-xs font-semibold text-zinc-700 hover:bg-zinc-100 transition-colors cursor-pointer"
                >
                  Cancel & Skip
                </button>
                <button
                  type="button"
                  onClick={handleGoogleAllow}
                  className="px-5 py-2.5 rounded-xl bg-[#1A73E8] hover:bg-[#1557B0] text-xs font-semibold text-white shadow-md transition-all active:scale-95 cursor-pointer flex items-center gap-2"
                >
                  <span>Allow & Connect</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
