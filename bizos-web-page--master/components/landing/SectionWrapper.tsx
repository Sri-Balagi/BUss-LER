"use client";

import { motion } from "framer-motion";
import React, { ReactNode, createContext, useRef } from "react";
import { ChevronDown } from "lucide-react";

export const SectionScrollContext = createContext<React.RefObject<HTMLDivElement | null> | null>(null);

interface SectionWrapperProps {
  children: ReactNode;
  className?: string;
  id?: string;
  onNext?: () => void;
  showNextButton?: boolean;
}

export default function SectionWrapper({
  children,
  className = "",
  id,
  onNext,
  showNextButton = true,
}: SectionWrapperProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  return (
    <SectionScrollContext.Provider value={scrollRef}>
      {/* Outer Layer: Full-Width Background Canvas with Top Navbar Clearance Offset */}
      <motion.section
        id={id}
        className={`w-full relative flex flex-col items-center justify-center shrink-0 pt-28 sm:pt-32 md:pt-36 pb-10 sm:pb-14 px-4 sm:px-6 lg:px-10 scroll-mt-28 transition-colors duration-500 ${className}`}
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: false, amount: 0.12 }}
        transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
      >
        {/* Inner Layer: Centered Floating Elevated Content Frame with Uniform Generous Breathing Room */}
        <div
          ref={scrollRef}
          className="w-full max-w-[1280px] h-auto min-h-fit my-auto flex flex-col items-center justify-start overflow-hidden rounded-[32px] sm:rounded-[44px] md:rounded-[48px] bg-[#FAF7F2]/95 dark:bg-[#1C1B18]/95 border-2 border-[#E6DFD3] dark:border-[#2D2A26] shadow-[0_24px_70px_rgba(0,0,0,0.05)] backdrop-blur-xl relative pt-14 sm:pt-18 md:pt-20 pb-16 sm:pb-20 md:pb-24 px-6 sm:px-12 md:px-16 lg:px-20 transition-all duration-300"
        >
          {children}
        </div>

        {/* Scroll Next Indicator */}
        {showNextButton && onNext && (
          <motion.button
            onClick={onNext}
            aria-label="Scroll to next section"
            className="mt-8 sm:mt-10 flex h-11 w-11 items-center justify-center rounded-full border border-[#E6DFD3] dark:border-white/10 bg-white/80 dark:bg-zinc-900/80 text-ink transition-all duration-300 hover:scale-110 hover:bg-[#E0F2FE] dark:hover:bg-[#0F2338] hover:border-[#38BDF8] hover:text-[#0EA5E9] shadow-[0_4px_16px_rgba(0,0,0,0.06)] cursor-pointer group"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: [0, 5, 0] }}
            transition={{
              opacity: { duration: 0.5 },
              y: { repeat: Infinity, duration: 2.4, ease: "easeInOut" },
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <ChevronDown className="h-5 w-5 text-ink-muted transition-transform duration-300 group-hover:translate-y-0.5 group-hover:text-[#0EA5E9]" />
          </motion.button>
        )}
      </motion.section>
    </SectionScrollContext.Provider>
  );
}
