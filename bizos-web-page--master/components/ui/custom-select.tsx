"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

export interface CustomSelectProps {
  value: string;
  onChange: (val: string) => void;
  options: readonly string[] | string[];
  placeholder?: string;
  hasIcon?: boolean;
  disabled?: boolean;
  className?: string;
}

export function CustomSelect({
  value,
  onChange,
  options,
  placeholder = "Select option...",
  hasIcon = false,
  disabled = false,
  className = "",
}: CustomSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className={`relative w-full ${className}`} ref={containerRef}>
      {/* Dropdown Trigger */}
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          backgroundColor: "var(--dropdown-trigger-bg)",
          borderColor: "var(--dropdown-trigger-border)",
          color: value ? "var(--dropdown-trigger-text)" : "var(--dropdown-placeholder)",
        }}
        className={`flex h-11 w-full items-center justify-between rounded-xl border transition-all duration-200 cursor-pointer ${
          hasIcon ? "pl-10" : "pl-4"
        } pr-4 text-sm hover:border-[color:var(--accent-primary)] focus:border-[color:var(--accent-primary)] focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        <span className={`truncate ${value ? "font-medium" : "font-light"}`}>
          {value || placeholder}
        </span>
        <ChevronDown
          style={{ color: "var(--dropdown-placeholder)" }}
          className={`h-4 w-4 shrink-0 transition-transform duration-200 ${
            isOpen ? "rotate-180 text-[color:var(--accent-primary)]" : ""
          }`}
        />
      </button>

      {/* Dropdown Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            style={{
              backgroundColor: "var(--dropdown-panel-bg)",
              borderColor: "var(--dropdown-panel-border)",
            }}
            className="absolute left-0 right-0 mt-1.5 max-h-60 overflow-y-auto rounded-xl border py-1.5 shadow-[0_4px_24px_rgba(0,0,0,0.12)] z-50 scrollbar-thin"
          >
            {options.map((opt) => {
              const isSelected = opt === value;
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => {
                    onChange(opt);
                    setIsOpen(false);
                  }}
                  style={{
                    backgroundColor: isSelected ? "var(--dropdown-option-selected-bg)" : undefined,
                    color: isSelected ? "var(--dropdown-option-selected-text)" : "var(--dropdown-option-text)",
                  }}
                  className={`flex w-full items-center px-4 py-2.5 text-sm text-left transition-colors duration-150 cursor-pointer ${
                    isSelected
                      ? "font-medium"
                      : "hover:bg-[color:var(--dropdown-option-hover)]"
                  }`}
                >
                  {opt}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default CustomSelect;
