"use client";

import { useBusiness } from "@/lib/business-context";
import { NewAccountPage } from "@/components/NewAccountPage";
import WelcomeBanner from "@/components/dashboard/WelcomeBanner";
import RuntimeOverview from "@/components/dashboard/RuntimeOverview";
import InfrastructureHealth from "@/components/dashboard/InfrastructureHealth";
import MemoryActivity from "@/components/dashboard/MemoryActivity";
import AgentFleet from "@/components/dashboard/AgentFleet";
import KnowledgeGraphWidget from "@/components/dashboard/KnowledgeGraphWidget";
import DecisionCenter from "@/components/dashboard/DecisionCenter";
import GoalManager from "@/components/dashboard/GoalManager";
import AuditLog from "@/components/dashboard/AuditLog";

export default function DashboardPage() {
  const { isPrimaryAccount } = useBusiness();

  // For Normal Users: Show ONLY the Contact Us Setup Card
  if (!isPrimaryAccount) {
    return <NewAccountPage />;
  }

  // For rsribalagi@gmail.com ONLY: Full Hotel Balagi Bhavan AI OS Active Workspace
  return (
    <div className="flex flex-col gap-6 pb-16">
      <WelcomeBanner />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-7">
        <RuntimeOverview />
        <InfrastructureHealth />
        <MemoryActivity />

        <AgentFleet />
        <KnowledgeGraphWidget />
        <DecisionCenter />

        <GoalManager />
        <AuditLog />
      </div>
    </div>
  );
}
