import type { Metadata } from "next";
import { Outfit, Plus_Jakarta_Sans, Space_Mono } from "next/font/google";
import "./globals.css";

const display = Outfit({
  subsets: ["latin"],
  variable: "--font-display",
});

const body = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-body",
});

const mono = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "BizOS — The Operating System for Artificial Intelligence",
  description:
    "BizOS orchestrates thinking, memory, knowledge, and decisions into one cognitive runtime. Watch intelligence move.",
};

import { AmbientBackground } from "@/components/ambient-background";
import { Navigator } from "@/components/navigator";
import { ThemeToggle } from "@/components/theme-toggle";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body className="font-body antialiased bg-deep-space text-primary min-h-screen">
        <AmbientBackground />
        <Navigator />
        {children}
        <ThemeToggle />
      </body>
    </html>
  );
}
