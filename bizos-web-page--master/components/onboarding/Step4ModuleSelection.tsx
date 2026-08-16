"use client";

import React from "react";
import { useOnboarding } from "@/lib/onboarding-context";
import {
  Boxes,
  Users,
  DollarSign,
  UserCheck,
  TrendingUp,
  ShoppingCart,
  Megaphone,
  FolderKanban,
  Factory,
  Headphones,
  BarChart3,
  ArrowRight,
  ArrowLeft,
  Check,
} from "lucide-react";

interface StepProps {
  onNext: () => void;
  onBack: () => void;
}

interface ModuleDef {
  name: string;
  desc: string;
  icon: React.ComponentType<{ className?: string }>;
}

const MODULES: ModuleDef[] = [
  { name: "Inventory", desc: "Real-time stock tracking & automated reordering", icon: Boxes },
  { name: "CRM", desc: "Customer relationships, history & lead management", icon: Users },
  { name: "Finance", desc: "Automated billing, expense tracking & cash flow", icon: DollarSign },
  { name: "HR", desc: "Employee onboarding, scheduling & payroll sync", icon: UserCheck },
  { name: "Sales", desc: "Pipeline tracking, deals & automated proposals", icon: TrendingUp },
  { name: "Procurement", desc: "Vendor orders, purchase requests & supplier SLA", icon: ShoppingCart },
  { name: "Marketing", desc: "Campaign automation, content AI & lead generation", icon: Megaphone },
  { name: "Projects", desc: "Task allocation, deadlines & milestone monitoring", icon: FolderKanban },
  { name: "Manufacturing", desc: "Production lines, bill of materials & quality control", icon: Factory },
  { name: "Customer Support", desc: "Ticket resolution, WhatsApp & email response AI", icon: Headphones },
  { name: "Analytics", desc: "Real-time BI dashboards & cognitive insights", icon: BarChart3 },
];

export function Step4ModuleSelection({ onNext, onBack }: StepProps) {
  const { data, toggleModule, updateData } = useOnboarding();

  const selectAll = () => {
    updateData({ selectedModules: MODULES.map((m) => m.name) });
  };

  const clearAll = () => {
    updateData({ selectedModules: [] });
  };

  return (
    <div className="flex flex-col max-w-3xl mx-auto py-2">
      <div className="text-center mb-6">
        <p className="eyebrow mb-2">STEP 4 OF 7 • MODULE ARCHITECTURE</p>
        <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-primary">
          Select Operational Modules
        </h2>
        <p className="mt-1.5 text-xs text-secondary max-w-lg mx-auto">
          Enable or disable cognitive modules for your Digital Twin. You can adjust these anytime later in settings.
        </p>
      </div>

      {/* Select All / Clear All Bar */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-mono text-tertiary">
          Selected: <strong className="text-accent">{data.selectedModules.length}</strong> / {MODULES.length} modules
        </span>
        <div className="flex items-center gap-3 text-xs">
          <button
            type="button"
            onClick={selectAll}
            className="text-accent hover:underline font-medium"
          >
            Select All
          </button>
          <span className="text-white/20">•</span>
          <button
            type="button"
            onClick={clearAll}
            className="text-secondary hover:text-primary transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {MODULES.map((mod) => {
          const Icon = mod.icon;
          const isSelected = data.selectedModules.includes(mod.name);

          return (
            <div
              key={mod.name}
              onClick={() => toggleModule(mod.name)}
              className={`group relative flex flex-col p-4 rounded-2xl border cursor-pointer transition-all duration-300 ${
                isSelected
                  ? "border-accent/40 bg-accent/[0.08] shadow-lg shadow-accent/5"
                  : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-xl transition-colors ${
                    isSelected ? "bg-accent text-white" : "bg-white/10 text-secondary"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded-full border transition-all ${
                    isSelected
                      ? "border-accent bg-accent text-white"
                      : "border-white/20 bg-transparent opacity-60"
                  }`}
                >
                  {isSelected && <Check className="h-3 w-3 stroke-[3]" />}
                </div>
              </div>

              <h3 className="text-sm font-medium text-primary">{mod.name}</h3>
              <p className="mt-1 text-[11px] text-secondary leading-snug">{mod.desc}</p>
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

        <button
          type="button"
          onClick={onNext}
          disabled={data.selectedModules.length === 0}
          className="flex h-11 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover disabled:opacity-50"
        >
          <span>Continue</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
