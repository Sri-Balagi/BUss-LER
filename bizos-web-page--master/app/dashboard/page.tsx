import RuntimeOverview from "@/components/dashboard/RuntimeOverview";
import InfrastructureHealth from "@/components/dashboard/InfrastructureHealth";
import MemoryActivity from "@/components/dashboard/MemoryActivity";
import AgentFleet from "@/components/dashboard/AgentFleet";
import KnowledgeGraphWidget from "@/components/dashboard/KnowledgeGraphWidget";
import DecisionCenter from "@/components/dashboard/DecisionCenter";
import GoalManager from "@/components/dashboard/GoalManager";
import AuditLog from "@/components/dashboard/AuditLog";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-7 pb-16">
      <RuntimeOverview />
      <InfrastructureHealth />
      <MemoryActivity />

      <AgentFleet />
      <KnowledgeGraphWidget />
      <DecisionCenter />

      <GoalManager />
      <AuditLog />
    </div>
  );
}
