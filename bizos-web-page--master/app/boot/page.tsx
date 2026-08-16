"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { ShieldCheck, Cpu, Database, Network, Sparkles, CheckCircle2, Bot } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useOnboarding } from "@/lib/onboarding-context";

interface BootStep {
  title: string;
  detail: string;
  icon: React.ElementType;
}

export default function BootPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const router = useRouter();
  const { user } = useAuth();
  const { data } = useOnboarding();

  const isBalagi = user?.email?.toLowerCase().trim() === "rsribalagi@gmail.com";
  const businessName = isBalagi
    ? "Hotel Balagi Bhavan"
    : (data.businessName && data.businessName.trim() ? data.businessName : `${user?.name || "Custom"} Business`);

  const BOOT_STEPS: BootStep[] = [
    {
      title: "Security Token & Account Verified",
      detail: `AES-256 encrypted authentication vault for ${user?.email || "user"}`,
      icon: ShieldCheck,
    },
    {
      title: `Initializing Digital Twin for ${businessName}`,
      detail: "Configuring domain ontology, business rules & entity mappings",
      icon: Cpu,
    },
    {
      title: "Processing Business Profile & Integration Questionnaire",
      detail: `Registering requested modules: ${data.selectedModules?.slice(0, 3).join(", ") || "POS, Inventory, CRM"}`,
      icon: Database,
    },
    {
      title: "Queuing Connectors & Knowledge Graph Request",
      detail: `Configuring API endpoints for ${data.selectedIntegrations?.slice(0, 2).join(", ") || "Gmail, Drive"}`,
      icon: Network,
    },
    {
      title: isBalagi ? "Deploying Autonomous Agent Fleet" : "Preparing Enterprise Onboarding Portal",
      detail: isBalagi ? "South Indian Fine Dining POS & SLA agent online" : "Packaging setup manifest for implementation team",
      icon: Bot,
    },
    {
      title: isBalagi ? "Digital Twin Online — Launching BizOS" : "Setup Manifest Created — Redirecting",
      detail: isBalagi ? "Opening Hotel Balagi Bhavan operational dashboard..." : "Opening enterprise support contact portal...",
      icon: Sparkles,
    },
  ];

  useEffect(() => {
    // Step progression
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < BOOT_STEPS.length - 1) {
          return prev + 1;
        }
        clearInterval(interval);
        return prev;
      });
    }, 550);

    // Smooth progress bar
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 3;
      });
    }, 70);

    return () => {
      clearInterval(interval);
      clearInterval(progressInterval);
    };
  }, [BOOT_STEPS.length]);

  // Redirect to dashboard when boot sequence completes
  useEffect(() => {
    if (progress >= 100) {
      const timer = setTimeout(() => {
        router.push("/dashboard");
      }, 700);
      return () => clearTimeout(timer);
    }
  }, [progress, router]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950 p-6 selection:bg-accent/30 text-primary">
      {/* Background Ambient Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-amber-950/20 via-zinc-950 to-zinc-950 pointer-events-none" />

      <div className="w-full max-w-xl relative space-y-8">
        {/* Header Branding */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-400 text-xs font-mono font-medium tracking-wide">
            <Sparkles className="h-3.5 w-3.5 animate-spin text-amber-400" />
            <span>SYNTHESIZING DIGITAL TWIN</span>
          </div>

          <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight text-white">
            Synthesizing {businessName}
          </h1>

          <p className="text-xs text-zinc-400 max-w-md mx-auto">
            Configuring cognitive memory nodes and enterprise parameters for <span className="text-amber-400 font-semibold">{user?.email || "rsribalagi@gmail.com"}</span>.
          </p>
        </div>

        {/* Progress Card */}
        <div className="rounded-2xl border border-white/10 bg-zinc-900/80 p-6 backdrop-blur-xl shadow-2xl space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-zinc-400">Setup Status</span>
              <span className="text-amber-400 font-bold">{Math.round(progress)}%</span>
            </div>
            <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-amber-500 via-orange-500 to-emerald-400"
                style={{ width: `${progress}%` }}
                transition={{ duration: 0.1 }}
              />
            </div>
          </div>

          {/* Boot Steps List */}
          <div className="space-y-3">
            {BOOT_STEPS.map((step, idx) => {
              const Icon = step.icon as React.ComponentType<{ className?: string }>;
              const isDone = idx < activeStep || progress >= 100;
              const isCurrent = idx === activeStep && progress < 100;

              return (
                <div
                  key={idx}
                  className={`flex items-start gap-3.5 p-3 rounded-xl border transition-all duration-300 ${
                    isCurrent
                      ? "border-amber-500/40 bg-amber-500/10 shadow-sm"
                      : isDone
                      ? "border-white/5 bg-white/[0.02]"
                      : "border-transparent opacity-30"
                  }`}
                >
                  <div
                    className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
                      isDone
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : isCurrent
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/40 animate-pulse"
                        : "bg-white/5 text-zinc-500"
                    }`}
                  >
                    {isDone ? <CheckCircle2 className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
                  </div>

                  <div className="space-y-0.5 flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className={`text-xs font-semibold ${isCurrent ? "text-amber-300" : isDone ? "text-white" : "text-zinc-500"}`}>
                        {step.title}
                      </h4>
                      {isDone && (
                        <span className="font-mono text-[10px] text-emerald-400 font-bold uppercase tracking-wider">
                          READY
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-zinc-400 truncate">{step.detail}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer info */}
        <p className="text-center font-mono text-[11px] text-zinc-500">
          BizOS v6.0.0 · Dedicated Enterprise Setup Hub
        </p>
      </div>
    </div>
  );
}
