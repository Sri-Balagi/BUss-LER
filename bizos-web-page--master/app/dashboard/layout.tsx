import type { Metadata } from "next";
import { CognitiveStateProvider } from "@/lib/dashboard/state";
import NeuralBackground from "@/components/NeuralBackground";
import Sidebar from "@/components/dashboard/Sidebar";
import Topbar from "@/components/dashboard/Topbar";

export const metadata: Metadata = {
  title: "Dashboard — BizOS",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <CognitiveStateProvider>
      <NeuralBackground />
      <Sidebar />
      <div className="min-h-screen pl-[104px] pr-6 pt-6 sm:pr-8">
        <div className="mx-auto max-w-[1400px]">
          <Topbar />
          {children}
        </div>
      </div>
    </CognitiveStateProvider>
  );
}
