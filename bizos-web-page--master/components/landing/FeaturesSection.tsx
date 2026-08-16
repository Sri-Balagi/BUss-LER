"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import Features from "@/components/Features";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function FeaturesSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-[#BCB9C0] dark:bg-[#161513] text-primary" {...props}>
      <Features />
    </SectionWrapper>
  );
}

export default FeaturesSection;
