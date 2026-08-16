"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

const LINES = [
  "BizOS — initializing",
  "loading cognitive layer",
  "memory platform online",
  "knowledge repository ready",
  "decision engine ready",
  "workflow runtime active",
];

export default function BootSequence() {
  const [visible, setVisible] = useState(false);
  const [lineIndex, setLineIndex] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const alreadyBooted = sessionStorage.getItem("bizos-booted");
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (alreadyBooted || prefersReduced) {
      setDone(true);
      return;
    }
    setVisible(true);
    sessionStorage.setItem("bizos-booted", "1");

    const stepMs = 280;
    const timers = LINES.map((_, i) =>
      setTimeout(() => setLineIndex(i + 1), stepMs * (i + 1))
    );
    const closeTimer = setTimeout(() => setVisible(false), stepMs * (LINES.length + 2));
    const doneTimer = setTimeout(() => setDone(true), stepMs * (LINES.length + 2) + 700);

    return () => {
      timers.forEach(clearTimeout);
      clearTimeout(closeTimer);
      clearTimeout(doneTimer);
    };
  }, []);

  if (done) return null;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-void"
        >
          <div className="w-[320px] font-mono text-[13px]">
            {LINES.map((line, i) => (
              <div
                key={line}
                className="flex items-center gap-2 py-1 transition-opacity duration-300"
                style={{ opacity: i < lineIndex ? 1 : 0 }}
              >
                <span className="text-core-cyan">{i < lineIndex ? "✓" : ""}</span>
                <span className="text-ink-muted">{line}</span>
              </div>
            ))}
            <div className="mt-3 h-px w-full overflow-hidden bg-white/[0.06]">
              <motion.div
                className="h-full bg-gradient-to-r from-core-blue via-core-cyan to-core-violet"
                initial={{ width: "0%" }}
                animate={{ width: `${(lineIndex / LINES.length) * 100}%` }}
                transition={{ duration: 0.25 }}
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
