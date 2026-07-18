import abc
from app.domain.retrieval.models import RetrievalContext, RetrievalResult


class IRetrievalPipeline(abc.ABC):
    """
    Abstraction for the end-to-end Retrieval Pipeline.
    Separates source selection, retrieval, normalization, ranking (RRF),
    result assembly, and event publication from the service orchestrator.
    """
    
    @abc.abstractmethod
    async def execute(self, context: RetrievalContext) -> RetrievalResult:
        """Execute the full retrieval pipeline and return the final result."""
        pass
