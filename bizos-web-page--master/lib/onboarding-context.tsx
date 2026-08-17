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
  businessName: "Acme Dynamics",
  industry: "Technology & Software",
  businessType: "B2B SaaS",
  country: "United States",
  timezone: "UTC-5 (Eastern Time)",
  companySize: "11-50 employees",
  annualRevenue: "$1M - $5M",
  aiDescription:
    "We provide enterprise AI operations and decision automation software to mid-market businesses. Our team manages customer communications, project pipelines, and billing across multiple channels.",
  selectedModules: [
    "Inventory",
    "CRM",
    "Finance",
    "HR",
    "Sales",
    "Analytics",
    "Customer Support",
  ],
  aiPreferenceMode: "copilot",
  communicationStyle: "professional",
  selectedIntegrations: ["Gmail", "Slack", "WhatsApp", "Stripe", "GitHub"],
  completed: false,
};

interface OnboardingContextType {
  data: OnboardingData;
  updateData: (fields: Partial<OnboardingData>) => void;
  toggleModule: (moduleName: string) => void;
  toggleIntegration: (integrationName: string) => void;
  completeOnboarding: () => void;
  resetOnboarding: () => void;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);
const ONBOARDING_STORAGE_KEY = "bizos_onboarding_data";

export function OnboardingProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<OnboardingData>(DEFAULT_ONBOARDING);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      if (saved) {
        setData(JSON.parse(saved));
      }
    } catch (e) {
      console.error("Failed to load onboarding state", e);
    }
  }, []);

  const updateData = (fields: Partial<OnboardingData>) => {
    setData((prev) => {
      const next = { ...prev, ...fields };
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const toggleModule = (moduleName: string) => {
    setData((prev) => {
      const exists = prev.selectedModules.includes(moduleName);
      const nextModules = exists
        ? prev.selectedModules.filter((m) => m !== moduleName)
        : [...prev.selectedModules, moduleName];
      const next = { ...prev, selectedModules: nextModules };
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const toggleIntegration = (integrationName: string) => {
    setData((prev) => {
      const exists = prev.selectedIntegrations.includes(integrationName);
      const nextIntegrations = exists
        ? prev.selectedIntegrations.filter((i) => i !== integrationName)
        : [...prev.selectedIntegrations, integrationName];
      const next = { ...prev, selectedIntegrations: nextIntegrations };
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const completeOnboarding = () => {
    setData((prev) => {
      const next = { ...prev, completed: true, completedAt: new Date().toISOString() };
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const resetOnboarding = () => {
    setData(DEFAULT_ONBOARDING);
    localStorage.removeItem(ONBOARDING_STORAGE_KEY);
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
