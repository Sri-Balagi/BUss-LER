import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        white: "var(--bg-surface)",
        black: "var(--text-primary)",
        "deep-space": "var(--bg-main)",
        "glass-panel": "var(--bg-surface)",
        primary: "var(--text-primary)",
        secondary: "var(--text-secondary)",
        tertiary: "var(--text-muted)",
        accent: "var(--accent-primary)",
        "accent-hover": "var(--accent-hover)",
        ink: "var(--text-primary)",
        "ink-muted": "var(--text-secondary)",
        "ink-faint": "var(--text-muted)",
        void: "var(--bg-main)",
        "section-alt": "var(--bg-section-alt)",
        "hover-beige": "var(--bg-hover-beige)",
        cognition: {
          thought: "var(--accent-primary)",
          memory: "var(--accent-primary)",
          knowledge: "var(--accent-primary)",
          decision: "var(--accent-primary)",
          warning: "#FF9900",
          critical: "#FF3366",
        },
      },
      fontFamily: {
        display: ["var(--font-poppins)", "sans-serif"],
        body: ["var(--font-poppins)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        "glow-thought": "none",
        "glow-memory": "none",
        "glow-knowledge": "none",
        "glow-decision": "none",
        "glow-warning": "none",
        "glow-critical": "none",
        panel: "0 2px 15px rgba(0, 0, 0, 0.05)",
      },
      backgroundImage: {
        "grid-fade":
          "linear-gradient(to bottom, rgba(236,226,210,0.02) 1px, transparent 1px), linear-gradient(to right, rgba(236,226,210,0.02) 1px, transparent 1px)",
      },
      animation: {
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        float: "float 6s ease-in-out infinite",
        breathe: "breathe 4s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        breathe: {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.8", transform: "scale(1.01)" },
        }
      },
    },
  },
  plugins: [],
};

export default config;
