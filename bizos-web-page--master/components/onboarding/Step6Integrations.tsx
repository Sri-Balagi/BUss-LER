"use client";

import React from "react";
import { useOnboarding } from "@/lib/onboarding-context";
import { ArrowRight, ArrowLeft, Check, Plus } from "lucide-react";

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

  const selectAll = () => {
    updateData({ selectedIntegrations: INTEGRATIONS.map((i) => i.name) });
  };

  const clearAll = () => {
    updateData({ selectedIntegrations: [] });
  };

  return (
    <div className="flex flex-col max-w-3xl mx-auto py-2">
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
            className="text-accent hover:underline font-medium"
          >
            Select Popular
          </button>
          <span className="text-white/20">•</span>
          <button
            type="button"
            onClick={clearAll}
            className="text-secondary hover:text-primary transition-colors"
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
          className="flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-5 text-sm font-medium text-primary hover:bg-white/[0.08] transition-all"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onNext}
            className="flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-5 text-sm font-medium text-secondary hover:text-primary hover:bg-white/[0.08] transition-all"
          >
            <span>Skip for now</span>
          </button>

          <button
            type="button"
            onClick={onNext}
            className="flex h-11 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover"
          >
            <span>Generate Twin</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
