"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { FinalCTA } from "@/components/sections/FinalCTA";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function CTASection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-[#C8C5CC] dark:bg-[#12110F] text-primary" {...props}>
      <FinalCTA />
    </SectionWrapper>
  );
}

export default CTASection;
