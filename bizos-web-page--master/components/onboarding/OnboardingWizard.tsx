"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

import { Step1Welcome } from "./Step1Welcome";
import { Step2BusinessInfo } from "./Step2BusinessInfo";
import { Step3AiDescription } from "./Step3AiDescription";
import { Step4ModuleSelection } from "./Step4ModuleSelection";
import { Step5AiPreferences } from "./Step5AiPreferences";
import { Step6Integrations } from "./Step6Integrations";
import { Step7DigitalTwinCreation } from "./Step7DigitalTwinCreation";

const STEP_TITLES = [
  "Welcome",
  "Business Profile",
  "AI Description",
  "Modules",
  "AI Preferences",
  "Integrations",
  "Digital Twin",
];

export function OnboardingWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);

  const nextStep = () => setStep((prev) => Math.min(prev + 1, 7));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

  const handleComplete = () => {
    // Redirect user to the Digital Twin Creation Boot sequence
    router.push("/boot");
  };

  return (
    <div className="flex flex-col w-full max-w-4xl mx-auto">
      {/* Progress Bar Header (hidden on step 7) */}
      {step < 7 && (
        <div className="mb-8 flex flex-col gap-3">
          <div className="flex items-center justify-between px-1">
            <span className="font-mono text-xs text-secondary">
              STEP <strong className="text-accent">{step}</strong> OF 7 — {STEP_TITLES[step - 1]}
            </span>
            <span className="font-mono text-xs text-tertiary">
              {Math.round((step / 7) * 100)}% Complete
            </span>
          </div>

          {/* Stepper Indicator */}
          <div className="flex items-center gap-1.5 w-full">
            {STEP_TITLES.map((title, idx) => {
              const current = idx + 1;
              const isCompleted = current < step;
              const isCurrent = current === step;

              return (
                <div
                  key={title}
                  onClick={() => {
                    if (isCompleted) setStep(current);
                  }}
                  className={`h-2 flex-1 rounded-full transition-all duration-300 ${
                    isCompleted
                      ? "bg-accent cursor-pointer"
                      : isCurrent
                      ? "bg-accent shadow-glow-thought"
                      : "bg-white/10"
                  }`}
                  title={`${current}. ${title}`}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Step Content Container */}
      <div className="glass-panel p-6 sm:p-10 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-xl relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {step === 1 && <Step1Welcome onNext={nextStep} />}
            {step === 2 && <Step2BusinessInfo onNext={nextStep} onBack={prevStep} />}
            {step === 3 && <Step3AiDescription onNext={nextStep} onBack={prevStep} />}
            {step === 4 && <Step4ModuleSelection onNext={nextStep} onBack={prevStep} />}
            {step === 5 && <Step5AiPreferences onNext={nextStep} onBack={prevStep} />}
            {step === 6 && <Step6Integrations onNext={nextStep} onBack={prevStep} />}
            {step === 7 && <Step7DigitalTwinCreation onComplete={handleComplete} />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
