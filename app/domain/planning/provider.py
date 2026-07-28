from abc import ABC, abstractmethod

from app.domain.intelligence.provider import IIntelligenceProvider
from app.domain.planning.models import Goal, Plan, PlanningContext
from app.domain.intelligence.trace import CognitiveTrace


class IPlanningProvider(IIntelligenceProvider, ABC):
    """
    Contract for Cognitive Planning Engines (e.g. OpenAI, Anthropic, or specialized MCTS engines).
    """

    @abstractmethod
    async def generate_plan(self, context: PlanningContext, goal: Goal, trace: CognitiveTrace) -> Plan:
        """
        Synthesizes a Goal and PlanningContext into a multi-step Plan graph.
        The plan returned will be in DRAFT status and subjected to validation.
        """
        pass
