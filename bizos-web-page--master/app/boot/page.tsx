"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";

const BOOT_SEQUENCE = [
  "Initializing Kernel...",
  "Loading Cognitive Layer...",
  "Memory Platform Online.",
  "Knowledge Repository Ready.",
  "Decision Engine Online.",
  "Workflow Runtime Active.",
  "Enterprise Infrastructure Secured.",
  "Welcome to BizOS."
];

export default function BootPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const router = useRouter();

  useEffect(() => {
    if (currentStep < BOOT_SEQUENCE.length) {
      const delay = currentStep === BOOT_SEQUENCE.length - 1 ? 600 : Math.random() * 150 + 50;
      const timeout = setTimeout(() => {
        setCurrentStep((prev) => prev + 1);
      }, delay);
      return () => clearTimeout(timeout);
    } else {
      // Transition to dashboard after sequence finishes
      setTimeout(() => {
        router.push("/app/core");
      }, 200);
    }
  }, [currentStep, router]);

  return (
    <div className="fixed inset-0 bg-deep-space z-50 flex items-center justify-center font-mono">
      <div className="max-w-2xl w-full p-8 flex flex-col gap-2 relative">
        <AnimatePresence>
          {BOOT_SEQUENCE.slice(0, currentStep + 1).map((text, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`text-sm md:text-base ${
                index === BOOT_SEQUENCE.length - 1
                  ? "text-accent font-bold text-lg mt-8"
                  : "text-primary"
              }`}
            >
              {`> ${text}`}
            </motion.div>
          ))}
        </AnimatePresence>
        
        {currentStep < BOOT_SEQUENCE.length && (
          <motion.div
            animate={{ opacity: [1, 0] }}
            transition={{ repeat: Infinity, duration: 0.8 }}
            className="w-3 h-5 bg-accent inline-block mt-2"
          />
        )}
      </div>

      <motion.div 
        className="absolute inset-0 pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: currentStep === BOOT_SEQUENCE.length ? 1 : 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="absolute inset-0 bg-primary" />
      </motion.div>
    </div>
  );
}
