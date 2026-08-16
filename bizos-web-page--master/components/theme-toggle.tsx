"use client";

import { useState, useEffect } from "react";
import { Moon, Sun } from "lucide-react";
import { motion } from "framer-motion";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    if (document.documentElement.classList.contains("dark")) {
      setIsDark(true);
    }
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove("dark");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      setIsDark(true);
    }
  };

  return (
    <motion.button
      onClick={toggleTheme}
      className="fixed bottom-8 right-8 z-50 p-3.5 rounded-full flex items-center justify-center text-secondary hover:text-accent transition-all duration-300 backdrop-blur-2xl bg-white/75 dark:bg-[#1C1C1C]/75 border border-white/50 dark:border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.12)] hover:border-accent/40 hover:shadow-[0_12px_36px_rgba(232,123,42,0.18)]"
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      aria-label="Toggle Theme"
    >
      {isDark ? <Sun className="w-5 h-5 text-accent drop-shadow-[0_0_8px_rgba(232,123,42,0.5)]" /> : <Moon className="w-5 h-5 text-secondary hover:text-primary" />}
    </motion.button>
  );
}
