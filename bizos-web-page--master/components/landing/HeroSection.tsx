"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { Hero } from "@/components/sections/Hero";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function HeroSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-[#C8C5CC] dark:bg-[#12110F] text-primary" {...props}>
      <Hero />
    </SectionWrapper>
  );
}

export default HeroSection;
