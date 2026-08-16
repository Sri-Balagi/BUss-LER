"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { Architecture } from "@/components/sections/Architecture";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function ArchitectureSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-[#C8C5CC] dark:bg-[#12110F] text-primary" {...props}>
      <Architecture />
    </SectionWrapper>
  );
}

export default ArchitectureSection;
