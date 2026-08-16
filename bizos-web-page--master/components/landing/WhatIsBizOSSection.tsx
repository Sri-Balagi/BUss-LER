"use client";
import React from "react";
import SectionWrapper from "./SectionWrapper";
import { WhatIsBizOS } from "@/components/sections/WhatIsBizOS";

interface LandingSectionProps {
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export function WhatIsBizOSSection(props: LandingSectionProps) {
  return (
    <SectionWrapper className="bg-[#C8C5CC] dark:bg-[#12110F] text-primary" {...props}>
      <WhatIsBizOS />
    </SectionWrapper>
  );
}

export default WhatIsBizOSSection;
