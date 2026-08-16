"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Brain, Zap, Globe2 } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="relative w-full h-full min-h-screen overflow-hidden flex flex-col items-center justify-center pt-24 pb-32">
      {/* Hero Section */}
      <section className="relative z-10 flex flex-col items-center text-center max-w-5xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="mb-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-cognition-thought/30 bg-cognition-thought/5 backdrop-blur-md mb-6">
            <span className="w-2 h-2 rounded-full bg-cognition-thought animate-pulse-slow " />
            <span className="text-sm font-mono tracking-widest text-cognition-thought uppercase">
              System Online
            </span>
          </div>

          <h1 className="font-display text-5xl md:text-7xl lg:text-[100px] font-medium leading-[1.1] tracking-tight mb-6">
            The Operating System <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[color:var(--text-primary)] to-[color:var(--text-secondary)]">
              for Intelligence
            </span>
          </h1>

          <p className="font-body text-xl md:text-2xl text-secondary max-w-3xl mx-auto mb-12 font-light">
            Not another dashboard. A living, breathing cognitive space where memory,
            knowledge, and reasoning converge into a single unified runtime.
          </p>

          <Link href="/boot">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative inline-flex items-center gap-3 px-8 py-4 rounded-full bg-primary text-deep-space font-medium text-lg overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-cognition-thought via-cognition-knowledge to-cognition-memory opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <span className="relative z-10 group-hover:text-deep-space transition-colors duration-300">
                Initialize Sequence
              </span>
              <ArrowRight className="relative z-10 w-5 h-5 group-hover:text-deep-space transition-colors duration-300" />
            </motion.button>
          </Link>
        </motion.div>
      </section>

      {/* Feature Glimpse */}
      <section className="relative z-10 mt-32 w-full max-w-6xl px-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <FeatureCard
          delay={0.2}
          icon={Brain}
          title="Cognitive Runtime"
          description="Watch intelligence move as tasks flow through planner, reasoning, and decision engines in real-time."
          glowColor="thought"
        />
        <FeatureCard
          delay={0.4}
          icon={Globe2}
          title="Memory Galaxy"
          description="Navigate semantic neighborhoods in a fully 3D celestial representation of long-term storage."
          glowColor="memory"
        />
        <FeatureCard
          delay={0.6}
          icon={Zap}
          title="Workflow Playback"
          description="Replay the exact path of reasoning and decision-making for any historical execution."
          glowColor="decision"
        />
      </section>

      <div className="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-deep-space to-transparent pointer-events-none" />
    </main>
  );
}

function FeatureCard({ delay, icon: Icon, title, description, glowColor }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: delay * 0.5, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -5 }}
      className="glass-panel p-8 group relative overflow-hidden"
    >
      <div
        className="absolute -inset-px opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl"
        style={{
          boxShadow: `inset 0 0 20px -10px var(--glow-${glowColor}, #fff)`,
        }}
      />
      <Icon className={`w-8 h-8 mb-6 text-cognition-${glowColor}`} />
      <h3 className="font-display text-2xl mb-3">{title}</h3>
      <p className="text-secondary leading-relaxed">{description}</p>
    </motion.div>
  );
}
