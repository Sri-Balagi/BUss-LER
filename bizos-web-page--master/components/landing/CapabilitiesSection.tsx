"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { Capabilities } from "@/components/sections/Capabilities";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function CapabilitiesSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-deep-space text-primary" {...props}>
      <Capabilities />
    </SectionWrapper>
  );
}

export default CapabilitiesSection;
