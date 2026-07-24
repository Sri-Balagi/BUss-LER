from abc import abstractmethod

from app.domain.intelligence.provider import IIntelligenceProvider
from app.domain.planning.models import Goal, Plan, PlanningContext


class IPlanningProvider(IIntelligenceProvider):
    """
    Interface for planning capabilities.
    Extends the intelligence provider to ensure registration via CapabilityRegistry.
    Provider implementations must remain LLM/execution agnostic at the domain level.
    """

    @abstractmethod
    async def generate_plan(self, context: PlanningContext, goal: Goal) -> Plan:
        """
        Generates a plan for the given goal using the provided context.
        The plan returned will be in DRAFT status and subjected to validation.
        """
        pass
