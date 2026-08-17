import type { Metadata } from "next";
import { CognitiveStateProvider } from "@/lib/dashboard/state";
import NeuralBackground from "@/components/NeuralBackground";
import Topbar from "@/components/dashboard/Topbar";
import WelcomeBanner from "@/components/dashboard/WelcomeBanner";

export const metadata: Metadata = {
  title: "Dashboard — BizOS",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <CognitiveStateProvider>
      <NeuralBackground />
      <div className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-all duration-200 ease-[0.16,1,0.3,1]">
        <div className="mx-auto max-w-[1440px] space-y-7">
          <Topbar />
          <WelcomeBanner />
          {children}
        </div>
      </div>
    </CognitiveStateProvider>
  );
}
