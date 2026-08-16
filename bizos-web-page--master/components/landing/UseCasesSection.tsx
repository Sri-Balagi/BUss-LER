"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { UseCases } from "@/components/sections/UseCases";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function UseCasesSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-deep-space text-primary" {...props}>
      <UseCases />
    </SectionWrapper>
  );
}

export default UseCasesSection;
