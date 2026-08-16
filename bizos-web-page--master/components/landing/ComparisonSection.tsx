"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { Comparison } from "@/components/sections/Comparison";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function ComparisonSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-deep-space text-primary" {...props}>
      <Comparison />
    </SectionWrapper>
  );
}

export default ComparisonSection;
