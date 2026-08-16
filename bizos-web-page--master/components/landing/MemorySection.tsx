"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { MemoryGalaxyVisualizer } from "../memory-galaxy";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function MemorySection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-deep-space text-primary relative h-screen" {...props}>
      <MemoryGalaxyVisualizer />
    </SectionWrapper>
  );
}

export default MemorySection;
