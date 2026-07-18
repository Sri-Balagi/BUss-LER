import abc
from typing import List

from app.domain.retrieval.models import RetrievalContext, RetrievalResultItem


class IVectorRepository(abc.ABC):
    """
    Abstraction for the Vector Database.
    Accepts a full RetrievalContext to support advanced filtering,
    namespacing, and hybrid search natively on the DB side if supported.
    """
    
    @abc.abstractmethod
    async def search(self, context: RetrievalContext) -> List[RetrievalResultItem]:
        """
        Execute a vector search using the provided context.
        Must return standard RetrievalResultItem objects.
        """
        pass
