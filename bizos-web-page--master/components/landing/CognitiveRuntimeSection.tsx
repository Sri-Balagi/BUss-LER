"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { CognitiveCore } from "@/components/sections/CognitiveCore";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function CognitiveRuntimeSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-deep-space text-primary" {...props}>
      <CognitiveCore />
    </SectionWrapper>
  );
}

export default CognitiveRuntimeSection;
