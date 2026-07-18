from typing import List
from pydantic import Field

from app.shared.events.models import DomainEvent
from app.domain.retrieval.models import RetrievalSource, RetrievalMetrics


class RetrievalExecuted(DomainEvent):
    """Event emitted whenever the Retrieval Engine completes a query."""
    query_hash: str = Field(..., description="A one-way hash of the query text for privacy-preserving observability.")
    sources_used: List[RetrievalSource] = Field(..., description="The sources that were actually queried.")
    ranking_strategy: str = Field(..., description="The name of the ranking strategy applied (e.g. 'RRF').")
    metrics: RetrievalMetrics = Field(..., description="Execution diagnostics and timing.")
