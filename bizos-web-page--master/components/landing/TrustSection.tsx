"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { Trust } from "@/components/sections/Trust";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function TrustSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-deep-space text-primary" {...props}>
      <Trust />
    </SectionWrapper>
  );
}

export default TrustSection;
