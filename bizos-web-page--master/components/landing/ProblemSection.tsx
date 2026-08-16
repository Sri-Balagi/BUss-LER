"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { Problem } from "@/components/sections/Problem";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function ProblemSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-[#BCB9C0] dark:bg-[#161513] text-primary" {...props}>
      <Problem />
    </SectionWrapper>
  );
}

export default ProblemSection;
