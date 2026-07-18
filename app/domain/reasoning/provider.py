import abc
from app.domain.intelligence.provider import IIntelligenceProvider
from app.domain.reasoning.models import ReasoningContext, ReasoningQuery, ReasoningResponse


class IReasoningProvider(IIntelligenceProvider):
    """
    Abstracts a generic reasoning capability (e.g. LLM, rules engine, symbolic).
    """
    
    @abc.abstractmethod
    async def reason(self, context: ReasoningContext, query: ReasoningQuery) -> ReasoningResponse:
        """Executes a reasoning operation and returns a canonical response."""
        pass
