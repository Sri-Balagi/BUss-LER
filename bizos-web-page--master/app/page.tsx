"use client";

import Nav from "@/components/Nav";
import { HeroSection } from "@/components/landing/HeroSection";
import { ProblemSection } from "@/components/landing/ProblemSection";
import { WhatIsBizOSSection } from "@/components/landing/WhatIsBizOSSection";
import { DecisionSection } from "@/components/landing/DecisionSection";
import { ArchitectureSection } from "@/components/landing/ArchitectureSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { CTASection } from "@/components/landing/CTASection";
import { Footer } from "@/components/sections/Footer";

export default function LandingPage() {
  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      const navOffset = 100;
      const elementPosition = el.getBoundingClientRect().top + window.scrollY;
      const offsetPosition = elementPosition - navOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  return (
    <main className="w-full min-h-screen overflow-y-auto scroll-smooth flex flex-col focus:outline-none bg-[#C8C5CC] dark:bg-[#12110F] relative">
      {/* Top Enterprise Navigation */}
      <Nav />

      {/* 1. Hero */}
      <HeroSection id="section-0" onNext={() => scrollToSection("section-1")} />

      {/* 2. Problem */}
      <ProblemSection id="section-1" onNext={() => scrollToSection("section-2")} />

      {/* 3. Solution */}
      <WhatIsBizOSSection id="section-2" onNext={() => scrollToSection("section-3")} />

      {/* 4. Pipeline */}
      <DecisionSection id="section-3" onNext={() => scrollToSection("section-4")} />

      {/* 5. Architecture */}
      <ArchitectureSection id="section-4" onNext={() => scrollToSection("section-5")} />

      {/* 6. Features */}
      <FeaturesSection id="section-5" onNext={() => scrollToSection("section-6")} />

      {/* 7. CTA */}
      <CTASection id="section-6" onNext={() => scrollToSection("section-footer")} />

      {/* 8. Footer */}
      <footer id="section-footer" className="w-full shrink-0 bg-[#C8C5CC] dark:bg-[#12110F]">
        <Footer />
      </footer>
    </main>
  );
}
