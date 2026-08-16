"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export interface OnboardingData {
  // Step 2: Business Info
  businessName: string;
  industry: string;
  businessType: string;
  country: string;
  timezone: string;
  companySize: string;
  annualRevenue?: string;

  // Step 3: AI Business Description
  aiDescription: string;

  // Step 4: Module Selection
  selectedModules: string[];

  // Step 5: AI Preferences
  aiPreferenceMode: "assistant" | "copilot" | "autonomous";
  communicationStyle: "professional" | "friendly" | "technical";

  // Step 6: Integrations
  selectedIntegrations: string[];

  // Completion
  completed: boolean;
  completedAt?: string;
}

const DEFAULT_ONBOARDING: OnboardingData = {
  businessName: "",
  industry: "Enterprise Operations",
  businessType: "Commercial Enterprise",
  country: "India",
  timezone: "UTC+5:30 (India Standard Time)",
  companySize: "10-50 Staff",
  annualRevenue: "",
  aiDescription:
    "Enterprise AI Digital Twin setup for business operations, CRM, POS billing, inventory management, and automated workflows.",
  selectedModules: [
    "Inventory",
    "CRM",
    "POS Billing",
    "Finance",
    "Customer Support",
  ],
  aiPreferenceMode: "copilot",
  communicationStyle: "professional",
  selectedIntegrations: ["Gmail", "Google Drive", "WhatsApp"],
  completed: false,
};

interface OnboardingContextType {
  data: OnboardingData;
  updateData: (fields: Partial<OnboardingData>) => void;
  toggleModule: (moduleName: string) => void;
  toggleIntegration: (integrationName: string) => void;
  completeOnboarding: () => Promise<void>;
  resetOnboarding: () => void;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);
const ONBOARDING_STORAGE_KEY = "bizos_onboarding_data";

export function OnboardingProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<OnboardingData>(DEFAULT_ONBOARDING);

  useEffect(() => {
    try {
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(DEFAULT_ONBOARDING));
    } catch (e) {
      console.error("Failed to load onboarding state", e);
    }
  }, []);

  const persist = (next: OnboardingData) => {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(next));
    return next;
  };

  const updateData = (fields: Partial<OnboardingData>) => {
    setData((prev) => persist({ ...prev, ...fields }));
  };

  const toggleModule = (moduleName: string) => {
    setData((prev) => {
      const exists = prev.selectedModules.includes(moduleName);
      const nextModules = exists
        ? prev.selectedModules.filter((m) => m !== moduleName)
        : [...prev.selectedModules, moduleName];
      return persist({ ...prev, selectedModules: nextModules });
    });
  };

  const toggleIntegration = (integrationName: string) => {
    setData((prev) => {
      const exists = prev.selectedIntegrations.includes(integrationName);
      const nextIntegrations = exists
        ? prev.selectedIntegrations.filter((i) => i !== integrationName)
        : [...prev.selectedIntegrations, integrationName];
      return persist({ ...prev, selectedIntegrations: nextIntegrations });
    });
  };

  const completeOnboarding = async () => {
    const completed = { ...data, completed: true, completedAt: new Date().toISOString() };
    setData(persist(completed));
  };

  const resetOnboarding = () => {
    setData(DEFAULT_ONBOARDING);
    localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(DEFAULT_ONBOARDING));
  };

  return (
    <OnboardingContext.Provider
      value={{
        data,
        updateData,
        toggleModule,
        toggleIntegration,
        completeOnboarding,
        resetOnboarding,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const ctx = useContext(OnboardingContext);
  if (!ctx) {
    throw new Error("useOnboarding must be used within an OnboardingProvider");
  }
  return ctx;
}
