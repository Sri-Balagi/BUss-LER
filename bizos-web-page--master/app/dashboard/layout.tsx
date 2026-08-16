"use client";

import { useBusiness } from "@/lib/business-context";
import { CognitiveStateProvider } from "@/lib/dashboard/state";
import NeuralBackground from "@/components/NeuralBackground";
import Topbar from "@/components/dashboard/Topbar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isPrimaryAccount } = useBusiness();

  // For normal users: Clean centered view containing ONLY the Contact Us Setup Card (No topbar, no sidebar padding, no navigator)
  if (!isPrimaryAccount) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 sm:p-6">
        {children}
      </div>
    );
  }

  // For rsribalagi@gmail.com ONLY: Full Hotel Balagi Bhavan AI OS Dashboard layout
  return (
    <CognitiveStateProvider>
      <NeuralBackground />
      <div className="min-h-screen pl-4 sm:pl-[92px] lg:pl-[104px] pr-4 sm:pr-8 lg:pr-12 pt-6 pb-16 transition-all duration-200 ease-[0.16,1,0.3,1]">
        <div className="mx-auto max-w-[1440px] space-y-7">
          <Topbar />
          {children}
        </div>
      </div>
    </CognitiveStateProvider>
  );
}
