"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { Pipeline } from "@/components/sections/Pipeline";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function DecisionSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-[#BCB9C0] dark:bg-[#161513] text-primary" {...props}>
      <Pipeline />
    </SectionWrapper>
  );
}

export default DecisionSection;
