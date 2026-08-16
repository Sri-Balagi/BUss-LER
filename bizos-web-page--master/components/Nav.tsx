"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Cpu,
  Brain,
  Workflow,
  Database,
  Network,
  GitBranch,
  Zap,
  Layers,
  Settings,
  TrendingUp,
  MessageSquare,
  Users,
  DollarSign,
  Factory,
  Activity,
  Shield,
  Code2,
  Terminal,
  FileText,
  Webhook,
  FolderGit2,
  BookOpen,
  Newspaper,
  GraduationCap,
  Award,
  History,
  HelpCircle,
  MessageCircle,
  Lock,
  ShieldCheck,
  Scale,
  Server,
  Headphones,
  Mail,
  ChevronDown,
  Menu,
  X,
  ArrowRight,
} from "lucide-react";
import { MagneticButton } from "@/components/ui/MagneticButton";

// Navigation Structure Definitions
interface MenuItem {
  title: string;
  desc: string;
  icon: any;
  href: string;
}

interface NavCategory {
  id: string;
  label: string;
  hasDropdown: boolean;
  href?: string;
  columns?: { title?: string; items: MenuItem[] }[];
}

const NAV_CATEGORIES: NavCategory[] = [
  {
    id: "platform",
    label: "Platform",
    hasDropdown: true,
    columns: [
      {
        title: "Core Capabilities",
        items: [
          { title: "AI Operating System", desc: "Unified cognitive runtime environment", icon: Cpu, href: "#top" },
          { title: "Cognitive Engine", desc: "Real-time reasoning and intent synthesis", icon: Brain, href: "#section-2" },
          { title: "Agent Orchestration", desc: "Multi-agent team coordination & boundaries", icon: Workflow, href: "#features" },
          { title: "Memory System", desc: "Persistent long-term semantic galaxy", icon: Database, href: "#section-2" },
        ],
      },
      {
        title: "Intelligence & Workflows",
        items: [
          { title: "Knowledge Graph", desc: "Structured enterprise domain understanding", icon: Network, href: "#architecture" },
          { title: "Decision Engine", desc: "Automated scoring & policy safeguards", icon: GitBranch, href: "#section-3" },
          { title: "Workflow Automation", desc: "Autonomous end-to-end task execution", icon: Zap, href: "#section-3" },
          { title: "Integrations", desc: "Connect with 100+ enterprise software tools", icon: Layers, href: "#features" },
        ],
      },
    ],
  },
  {
    id: "solutions",
    label: "Solutions",
    hasDropdown: true,
    columns: [
      {
        title: "By Department",
        items: [
          { title: "Operations", desc: "Streamline business workflows autonomously", icon: Settings, href: "#features" },
          { title: "Sales", desc: "Intelligent pipeline automation & forecasting", icon: TrendingUp, href: "#features" },
          { title: "Customer Support", desc: "24/7 contextual case resolution", icon: MessageSquare, href: "#features" },
          { title: "HR", desc: "Automated employee onboarding & policy workflows", icon: Users, href: "#features" },
        ],
      },
      {
        title: "By Industry",
        items: [
          { title: "Finance", desc: "Automated audit logs, billing & reconciliations", icon: DollarSign, href: "#features" },
          { title: "Manufacturing", desc: "Supply chain planning & operational monitoring", icon: Factory, href: "#features" },
          { title: "Healthcare", desc: "Compliant clinical & administrative processing", icon: Activity, href: "#features" },
          { title: "Custom Enterprise", desc: "Tailored cognitive models for your enterprise", icon: Shield, href: "#section-6" },
        ],
      },
    ],
  },
  {
    id: "developers",
    label: "Developers",
    hasDropdown: true,
    columns: [
      {
        title: "Tools & Specs",
        items: [
          { title: "API", desc: "High-performance REST & WebSocket APIs", icon: Code2, href: "#architecture" },
          { title: "SDK", desc: "Client libraries for TypeScript, Python & Go", icon: Terminal, href: "#architecture" },
          { title: "Documentation", desc: "Complete guides, API specs & references", icon: FileText, href: "#section-3" },
          { title: "MCP Support", desc: "Model Context Protocol integration", icon: Cpu, href: "#architecture" },
        ],
      },
      {
        title: "Ecosystem",
        items: [
          { title: "Webhooks", desc: "Real-time event streams & system triggers", icon: Webhook, href: "#section-3" },
          { title: "GitHub", desc: "Open-source connectors, samples & community", icon: FolderGit2, href: "#top" },
          { title: "Examples", desc: "Reference architectures & starter projects", icon: BookOpen, href: "#architecture" },
        ],
      },
    ],
  },
  {
    id: "resources",
    label: "Resources",
    hasDropdown: true,
    columns: [
      {
        title: "Learn & Read",
        items: [
          { title: "Documentation", desc: "Guides, tutorials, and system specs", icon: FileText, href: "#section-3" },
          { title: "Blog", desc: "Deep dives into AI architecture & research", icon: Newspaper, href: "#top" },
          { title: "Tutorials", desc: "Step-by-step guides for building agents", icon: GraduationCap, href: "#section-3" },
          { title: "Case Studies", desc: "Real enterprise transformation outcomes", icon: Award, href: "#features" },
        ],
      },
      {
        title: "Support & Community",
        items: [
          { title: "Changelog", desc: "Latest updates, releases & improvements", icon: History, href: "#architecture" },
          { title: "FAQ", desc: "Common questions about security & deployment", icon: HelpCircle, href: "#section-6" },
          { title: "Community", desc: "Join Discord, discussions & events", icon: MessageCircle, href: "#section-footer" },
        ],
      },
    ],
  },
  {
    id: "enterprise",
    label: "Enterprise",
    hasDropdown: true,
    columns: [
      {
        title: "Trust & Governance",
        items: [
          { title: "Security", desc: "Bank-grade encryption & data isolation", icon: Lock, href: "#features" },
          { title: "Compliance", desc: "SOC2 Type II, ISO27001 & HIPAA ready", icon: ShieldCheck, href: "#features" },
          { title: "Governance", desc: "Audit streams, RBAC & human-in-loop", icon: Scale, href: "#architecture" },
        ],
      },
      {
        title: "Scale & Deployment",
        items: [
          { title: "Deployment", desc: "On-prem, private cloud, or VPC options", icon: Server, href: "#architecture" },
          { title: "Support", desc: "Dedicated 24/7 SLA & solutions engineers", icon: Headphones, href: "#section-6" },
          { title: "Contact Sales", desc: "Tailored enterprise pricing & proof-of-concept", icon: Mail, href: "#section-6" },
        ],
      },
    ],
  },
  {
    id: "pricing",
    label: "Pricing",
    hasDropdown: false,
    href: "#features",
  },
];

export default function Nav() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseEnter = (id: string) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    const cat = NAV_CATEGORIES.find((c) => c.id === id);
    if (cat && cat.hasDropdown) {
      setActiveTab(id);
    } else {
      setActiveTab(null);
    }
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setActiveTab(null);
    }, 180);
  };

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (href.startsWith("#")) {
      e.preventDefault();
      setActiveTab(null);
      setMobileOpen(false);
      const targetId = href.replace("#", "");
      const el = document.getElementById(targetId);
      if (el) {
        const navOffset = 110;
        const elementPosition = el.getBoundingClientRect().top + window.scrollY;
        const offsetPosition = elementPosition - navOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth",
        });
      }
    }
  };

  const currentCategory = NAV_CATEGORIES.find((c) => c.id === activeTab);

  return (
    <>
      {/* Full-Page Backdrop Blur Overlay when dropdown menu or mobile drawer is open */}
      <AnimatePresence>
        {(activeTab !== null || mobileOpen) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            onClick={() => {
              setActiveTab(null);
              setMobileOpen(false);
            }}
            className="fixed inset-0 top-[82px] z-40 bg-black/40 dark:bg-black/60 backdrop-blur-md cursor-pointer transition-all duration-300"
          />
        )}
      </AnimatePresence>

      <motion.header
        initial={{ y: -28, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
        className="fixed inset-x-0 top-0 z-50 w-full border-b-2 border-[#E2DAD0] dark:border-[#2D2A26] backdrop-blur-2xl bg-[#F5F1E8]/98 dark:bg-[#1C1B18]/98 shadow-[0_4px_28px_rgba(0,0,0,0.06)] transition-all duration-300"
      >
        <div
          className="relative w-full"
          onMouseLeave={handleMouseLeave}
        >
          {/* Full-Width 100% Span Top Bar from Left to Right */}
          <nav className="w-full max-w-[1536px] mx-auto flex items-center justify-between px-6 sm:px-12 lg:px-16 py-5 sm:py-5.5">
            
            {/* Logo & Brand (Enlarged) */}
            <a
              href="#top"
              onClick={(e) => handleNavClick(e, "#top")}
              className="flex items-center gap-4 group"
            >
              <div className="flex h-10 sm:h-11 w-10 sm:w-11 items-center justify-center rounded-2xl bg-accent text-white shadow-[0_4px_14px_rgba(232,123,42,0.35)] transition-transform duration-300 group-hover:scale-105">
                <Cpu className="h-5.5 sm:h-6 w-5.5 sm:w-6" strokeWidth={1.5} />
              </div>
              <span className="font-display text-[22px] sm:text-[25px] font-bold tracking-tight text-ink">
                Biz<span className="text-accent font-mono font-normal">OS</span>
              </span>
            </a>

            {/* Desktop Navigation Category Links (Enlarged Text) */}
            <div className="hidden lg:flex items-center gap-3 sm:gap-4">
              {NAV_CATEGORIES.map((cat) => {
                const isActive = activeTab === cat.id;

                if (!cat.hasDropdown) {
                  return (
                    <a
                      key={cat.id}
                      href={cat.href || "#features"}
                      onClick={(e) => handleNavClick(e, cat.href || "#features")}
                      onMouseEnter={() => handleMouseEnter(cat.id)}
                      className="px-5 py-2.5 text-[16px] sm:text-[17px] font-semibold text-ink-muted transition-colors duration-200 hover:text-ink rounded-full hover:bg-black/[0.04] dark:hover:bg-white/[0.05]"
                    >
                      {cat.label}
                    </a>
                  );
                }

                return (
                  <div
                    key={cat.id}
                    onMouseEnter={() => handleMouseEnter(cat.id)}
                    className="relative"
                  >
                    <button
                      className={`flex items-center gap-2 px-5 py-2.5 text-[16px] sm:text-[17px] font-semibold transition-all duration-200 rounded-full cursor-pointer ${
                        isActive
                          ? "text-[#0EA5E9] bg-[#E0F2FE] dark:bg-[#0F172A]"
                          : "text-ink-muted hover:text-ink hover:bg-black/[0.04] dark:hover:bg-white/[0.05]"
                      }`}
                    >
                      {cat.label}
                      <ChevronDown
                        className={`h-4 w-4 transition-transform duration-250 ${
                          isActive ? "rotate-180 text-[#0EA5E9]" : "text-ink-muted/70"
                        }`}
                      />
                    </button>
                  </div>
                );
              })}
            </div>

            {/* Action Buttons on Right (Enlarged) */}
            <div className="flex items-center gap-6 sm:gap-8">
              <Link
                href="/auth/signin"
                className="hidden sm:inline-block text-[16px] sm:text-[17px] font-semibold text-ink-muted transition-colors duration-200 hover:text-ink"
              >
                Log in
              </Link>
              <MagneticButton
                onClick={() => router.push("/login")}
                className="flex items-center gap-2.5 rounded-full bg-accent hover:bg-accent-hover px-8 py-3.5 text-[15.5px] font-bold text-white shadow-[0_6px_20px_rgba(232,123,42,0.3)] transition-all duration-300 hover:scale-[1.04] active:scale-[0.98] cursor-pointer"
              >
                Initialize Sequence
                <ArrowRight className="h-4.5 w-4.5" />
              </MagneticButton>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="lg:hidden flex h-11 w-11 items-center justify-center rounded-full border-2 border-[color:var(--border-color)] bg-white dark:bg-zinc-900 text-ink"
              >
                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </nav>

          {/* Mega Menu Dropdown Window (Solid Warm Beige Card with Zero Overlap Bleed-Through) */}
          <AnimatePresence>
            {activeTab && currentCategory && currentCategory.hasDropdown && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.98 }}
                transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
                onMouseEnter={() => {
                  if (timeoutRef.current) clearTimeout(timeoutRef.current);
                }}
                className="absolute left-0 right-0 top-[82px] z-50 pt-2 px-6 sm:px-12 lg:px-16 max-w-[1536px] mx-auto"
              >
                <div className="w-full rounded-[32px] bg-[#FAF7F2] dark:bg-[#1C1B18] border-2 border-[#E2DAD0] dark:border-[#2D2A26] shadow-[0_30px_90px_rgba(0,0,0,0.25)] p-8 md:p-10">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    {currentCategory.columns?.map((col, cIdx) => (
                      <div key={cIdx} className="space-y-4">
                        {col.title && (
                          <p className="font-mono text-[12px] uppercase tracking-widest text-ink-muted font-bold px-3 mb-2">
                            {col.title}
                          </p>
                        )}
                        <div className="space-y-1.5">
                          {col.items.map((item, iIdx) => {
                            const Icon = item.icon;
                            return (
                              <a
                                key={iIdx}
                                href={item.href}
                                onClick={(e) => handleNavClick(e, item.href)}
                                className="group flex items-start gap-4 p-3.5 rounded-2xl transition-all duration-200 hover:bg-[#F5F1E8] dark:hover:bg-zinc-800/60 border border-transparent hover:border-[#D6CCBF]/60 hover:shadow-[0_4px_12px_rgba(0,0,0,0.04)] cursor-pointer"
                              >
                                <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[color:var(--border-color)] bg-[#EBE4D8] dark:bg-zinc-800 text-ink-muted transition-all duration-200 group-hover:bg-[#FFF7ED] group-hover:border-accent group-hover:text-accent">
                                  <Icon className="h-5 w-5" strokeWidth={1.5} />
                                </div>
                                <div>
                                  <div className="text-[15.5px] font-semibold text-ink group-hover:text-accent transition-colors duration-200 flex items-center gap-1.5">
                                    {item.title}
                                  </div>
                                  <p className="text-[13px] leading-snug text-ink-muted font-light mt-0.5">
                                    {item.desc}
                                  </p>
                                </div>
                              </a>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Mobile Navigation Drawer */}
          <AnimatePresence>
            {mobileOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="lg:hidden absolute left-0 right-0 top-[82px] z-50 rounded-b-[32px] bg-[#FAF7F2] dark:bg-[#1C1B18] border-b-2 border-x-2 border-[#E2DAD0] dark:border-[#2D2A26] shadow-[0_24px_50px_rgba(0,0,0,0.2)] p-8 max-h-[80vh] overflow-y-auto"
              >
                <div className="space-y-6">
                  {NAV_CATEGORIES.map((cat) => (
                    <div key={cat.id} className="space-y-2">
                      <p className="font-display text-[16px] font-bold text-ink border-b border-[color:var(--border-color)] pb-2">
                        {cat.label}
                      </p>
                      {cat.columns?.map((col, cIdx) => (
                        <div key={cIdx} className="grid grid-cols-1 gap-2 pl-2">
                          {col.items.map((item, iIdx) => {
                            const Icon = item.icon;
                            return (
                              <a
                                key={iIdx}
                                href={item.href}
                                onClick={(e) => handleNavClick(e, item.href)}
                                className="flex items-center gap-3.5 p-2.5 rounded-xl text-[14.5px] font-medium text-ink-muted hover:text-ink hover:bg-black/[0.04]"
                              >
                                <Icon className="h-4.5 w-4.5 text-accent" />
                                <span>{item.title}</span>
                              </a>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  ))}
                  <div className="pt-5 border-t border-[color:var(--border-color)] flex flex-col gap-3.5">
                    <Link
                      href="/auth/signin"
                      onClick={() => setMobileOpen(false)}
                      className="text-center py-3 text-[15px] font-semibold text-ink border-2 border-[color:var(--border-color)] rounded-full"
                    >
                      Log in
                    </Link>
                    <Link
                      href="/login"
                      onClick={() => setMobileOpen(false)}
                      className="text-center py-3 text-[15px] font-bold text-white bg-accent rounded-full shadow-md"
                    >
                      Initialize Sequence
                    </Link>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </motion.header>
    </>
  );
}
