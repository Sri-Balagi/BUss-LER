import enum
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.intelligence.context import IntelligenceContext


class RetrievalSource(enum.StrEnum):
    GRAPH = "GRAPH"
    MEMORY = "MEMORY"
    VECTOR = "VECTOR"


class RetrievalQuery(BaseModel):
    """Stable query object containing what to search for."""
    query_text: str = Field(..., description="The natural language text to search for.")
    query_vector: list[float] | None = Field(default=None, description="Pre-computed embeddings for vector search.")

    class Config:
        frozen = True


class RetrievalContext(IntelligenceContext):
    """Encapsulates the query alongside execution metadata for safe tracing and tracking."""
    query: RetrievalQuery = Field(..., description="The query to execute.")

    filters: dict[str, Any] = Field(default_factory=dict, description="Metadata filters (e.g. types, scopes).")
    sources: list[RetrievalSource] = Field(
        default_factory=lambda: [RetrievalSource.GRAPH, RetrievalSource.MEMORY, RetrievalSource.VECTOR],
        description="Which sources to query."
    )
    limit: int = Field(default=10, description="Max results to return.")
    offset: int = Field(default=0, description="Pagination offset.")

    class Config:
        frozen = True


class RetrievalResultItem(BaseModel):
    """A single matched item returned by the Retrieval Engine."""
    source: RetrievalSource = Field(..., description="Which storage layer produced this result.")
    entity_id: UUID = Field(..., description="The canonical UUID of the retrieved object.")
    content: Any = Field(..., description="The retrieved payload (e.g. memory content or node properties).")

    relevance_score: float = Field(default=0.0, description="Raw normalized score (0.0 to 1.0) indicating search rank relevance.")
    confidence: float = Field(default=1.0, description="Source-level confidence (e.g. factual confidence from SemanticMemory).")

    provenance_chain: list[str] = Field(default_factory=list, description="Traceability showing where this data originated.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary metadata.")


class RetrievalMetrics(BaseModel):
    """Immutable model capturing execution timing and diagnostics."""
    graph_search_time_ms: float = Field(default=0.0)
    memory_search_time_ms: float = Field(default=0.0)
    vector_search_time_ms: float = Field(default=0.0)
    ranking_time_ms: float = Field(default=0.0)
    total_execution_time_ms: float = Field(default=0.0)
    total_candidates: int = Field(default=0)
    final_result_count: int = Field(default=0)

    class Config:
        frozen = True


class RetrievalResult(BaseModel):
    """The complete response from the Retrieval Engine."""
    context: RetrievalContext = Field(..., description="The original context used for retrieval.")
    items: list[RetrievalResultItem] = Field(default_factory=list, description="The ranked result items.")
    metrics: RetrievalMetrics = Field(default_factory=RetrievalMetrics, description="Execution diagnostics.")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat(), description="ISO-8601 timestamp.")
