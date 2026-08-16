
from pydantic import Field

from app.domain.retrieval.models import RetrievalMetrics, RetrievalSource
from app.shared.events.models import DomainEvent


class RetrievalExecuted(DomainEvent):
    """Event emitted whenever the Retrieval Engine completes a query."""
    query_hash: str = Field(..., description="A one-way hash of the query text for privacy-preserving observability.")
    sources_used: list[RetrievalSource] = Field(..., description="The sources that were actually queried.")
    ranking_strategy: str = Field(..., description="The name of the ranking strategy applied (e.g. 'RRF').")
    metrics: RetrievalMetrics = Field(..., description="Execution diagnostics and timing.")
    tenant_id: str | None = Field(default=None, description="Tenant ID.")
