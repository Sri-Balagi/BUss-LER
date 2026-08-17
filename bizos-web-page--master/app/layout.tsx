import type { Metadata } from "next";
import { Geist_Mono, Poppins } from "next/font/google";
import "./globals.css";

const mono = Geist_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-mono",
});

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "BizOS — The Operating System for Artificial Intelligence",
  description:
    "BizOS orchestrates thinking, memory, knowledge, and decisions into one cognitive runtime. Watch intelligence move.",
};

import { AmbientBackground } from "@/components/ambient-background";
import Sidebar from "@/components/dashboard/Sidebar";
import { Navigator } from "@/components/navigator";
import { ThemeToggle } from "@/components/theme-toggle";
import { AuthProvider } from "@/lib/auth-context";
import { OnboardingProvider } from "@/lib/onboarding-context";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${mono.variable} ${poppins.variable}`}>
      <body className="font-body antialiased bg-deep-space text-primary min-h-screen">
        <AuthProvider>
          <OnboardingProvider>
            <AmbientBackground />
            <Sidebar />
            <Navigator />
            {children}
            <ThemeToggle />
          </OnboardingProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
