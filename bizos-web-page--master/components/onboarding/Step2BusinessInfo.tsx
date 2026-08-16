"use client";

import React, { useState } from "react";
import { useOnboarding } from "@/lib/onboarding-context";
import { CustomSelect } from "@/components/ui/custom-select";
import { Building2, Globe, Users, DollarSign, ArrowRight, ArrowLeft } from "lucide-react";

interface StepProps {
  onNext: () => void;
  onBack: () => void;
}

const INDUSTRIES = [
  "Technology & Software",
  "Retail & E-commerce",
  "Healthcare & Life Sciences",
  "Finance & Banking",
  "Hospitality & Restaurants",
  "Manufacturing & Logistics",
  "Professional Services",
  "Media & Entertainment",
  "Real Estate & Construction",
  "Education & Non-profit",
  "Other",
];

const BUSINESS_TYPES = [
  "B2B SaaS / Software",
  "B2C Product / Service",
  "Marketplace / Platform",
  "E-commerce / Retail",
  "Agency / Services",
  "Traditional Business",
  "Enterprise Hybrid",
];

const COMPANY_SIZES = [
  "1-10 employees",
  "11-50 employees",
  "51-200 employees",
  "201-500 employees",
  "500+ employees",
];

const REVENUE_RANGES = [
  "Under $100K",
  "$100K - $1M",
  "$1M - $5M",
  "$5M - $20M",
  "$20M+",
  "Prefer not to say",
];

const TIMEZONES = [
  "UTC-8 (Pacific Time)",
  "UTC-5 (Eastern Time)",
  "UTC+0 (Greenwich Mean Time)",
  "UTC+1 (Central European Time)",
  "UTC+5:30 (India Standard Time)",
  "UTC+8 (Singapore / China Standard Time)",
  "UTC+9 (Japan Standard Time)",
  "UTC+10 (Australian Eastern Time)",
];

export function Step2BusinessInfo({ onNext, onBack }: StepProps) {
  const { data, updateData } = useOnboarding();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!data.businessName || !data.industry) return;
    onNext();
  };

  return (
    <div className="flex flex-col max-w-2xl mx-auto py-2">
      <div className="text-center mb-6">
        <p className="eyebrow mb-2">STEP 2 OF 7 • BUSINESS PROFILE</p>
        <h2 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-primary">
          Business Information
        </h2>
        <p className="mt-1.5 text-xs text-secondary">
          Tell us about your organization to calibrate your Digital Twin.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Business Name & Industry */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-secondary">
              Business Name <span className="text-accent">*</span>
            </label>
            <div className="relative">
              <Building2 className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-tertiary" />
              <input
                type="text"
                required
                value={data.businessName}
                onChange={(e) => updateData({ businessName: e.target.value })}
                placeholder="e.g. Apex Ocean Seafood"
                className="h-11 w-full rounded-xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#1C1C1C] pl-10 pr-4 text-sm font-medium text-[#171717] dark:text-white placeholder:text-[#66635F] dark:placeholder:text-gray-400 focus:border-accent focus:outline-none transition-all shadow-sm"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-secondary">
              Industry <span className="text-accent">*</span>
            </label>
            <CustomSelect
              value={data.industry}
              onChange={(val) => updateData({ industry: val })}
              options={INDUSTRIES}
              placeholder="Select industry..."
            />
          </div>
        </div>

        {/* Business Type & Company Size */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-secondary">Business Type</label>
            <CustomSelect
              value={data.businessType}
              onChange={(val) => updateData({ businessType: val })}
              options={BUSINESS_TYPES}
              placeholder="Select business type..."
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-secondary">Company Size</label>
            <CustomSelect
              value={data.companySize}
              onChange={(val) => updateData({ companySize: val })}
              options={COMPANY_SIZES}
              placeholder="Select company size..."
            />
          </div>
        </div>

        {/* Country & Timezone */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-secondary">Country</label>
            <div className="relative">
              <Globe className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-tertiary" />
              <input
                type="text"
                value={data.country}
                onChange={(e) => updateData({ country: e.target.value })}
                placeholder="e.g. United States"
                className="h-11 w-full rounded-xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#1C1C1C] pl-10 pr-4 text-sm font-medium text-[#171717] dark:text-white placeholder:text-[#66635F] dark:placeholder:text-gray-400 focus:border-accent focus:outline-none transition-all shadow-sm"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-secondary">Primary Timezone</label>
            <CustomSelect
              value={data.timezone}
              onChange={(val) => updateData({ timezone: val })}
              options={TIMEZONES}
              placeholder="Select timezone..."
            />
          </div>
        </div>

        {/* Annual Revenue (Optional) */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-secondary flex items-center justify-between">
            <span>Annual Revenue (Optional)</span>
            <span className="text-[10px] text-tertiary">Helps optimize financial models</span>
          </label>
          <div className="relative">
            <DollarSign className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-tertiary z-20" />
            <CustomSelect
              value={data.annualRevenue || ""}
              onChange={(val) => updateData({ annualRevenue: val })}
              options={REVENUE_RANGES}
              placeholder="Select revenue range..."
              hasIcon={true}
            />
          </div>
        </div>

        {/* Navigation Controls */}
        <div className="mt-6 flex items-center justify-between pt-4 border-t border-white/10">
          <button
            type="button"
            onClick={onBack}
            className="flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-5 text-sm font-medium text-primary hover:bg-white/[0.08] transition-all"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back</span>
          </button>

          <button
            type="submit"
            disabled={!data.businessName || !data.industry}
            className="flex h-11 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover disabled:opacity-50"
          >
            <span>Continue</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
