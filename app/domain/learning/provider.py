from abc import ABC, abstractmethod

from app.domain.intelligence.provider import IIntelligenceProvider
from app.domain.learning.models import LearningContext, LearningResult


class ILearningProvider(IIntelligenceProvider, ABC):
    """
    Abstract interface for learning and knowledge consolidation providers.
    Responsible for extracting knowledge from reflection data and persisting
    it to long-term storage mechanisms (BKG, Memory Engine, Vector Store).
    """

    @abstractmethod
    async def consolidate_knowledge(self, context: LearningContext) -> LearningResult:
        """
        Extracts insights from the agent's reflection feedback and consolidates
        them into long-term persistence.

        Args:
            context: The context containing the agent's reflection feedback.

        Returns:
            LearningResult containing metrics and consolidated items.
        """
        pass
