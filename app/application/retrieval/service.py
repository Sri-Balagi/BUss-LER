import asyncio
import hashlib
import time

from app.domain.knowledge.repository import IKnowledgeRepository
from app.domain.memory.repository import IMemoryRepository
from app.domain.retrieval.events import RetrievalExecuted
from app.domain.retrieval.models import (
    RetrievalContext,
    RetrievalMetrics,
    RetrievalResult,
    RetrievalResultItem,
    RetrievalSource,
)
from app.domain.retrieval.pipeline import IRetrievalPipeline
from app.domain.retrieval.ranking import IRankingStrategy
from app.domain.retrieval.vector_store import IVectorRepository
from app.shared.events.bus import EventBus


class DefaultRetrievalPipeline(IRetrievalPipeline):
    """
    Standard retrieval pipeline that queries Graph, Memory, and Vector sources
    concurrently, ranks them via IRankingStrategy, and publishes the event.
    """

    def __init__(
        self,
        knowledge_repo: IKnowledgeRepository,
        memory_repo: IMemoryRepository,
        vector_repo: IVectorRepository,
        ranking_strategy: IRankingStrategy,
        event_bus: EventBus
    ):
        self._knowledge_repo = knowledge_repo
        self._memory_repo = memory_repo
        self._vector_repo = vector_repo
        self._ranking_strategy = ranking_strategy
        self._event_bus = event_bus

    async def execute(self, context: RetrievalContext) -> RetrievalResult:
        t_start = time.perf_counter()

        # Prepare concurrent tasks based on sources
        tasks = []
        source_mapping = []

        if RetrievalSource.GRAPH in context.sources:
            tasks.append(self._search_graph(context))
            source_mapping.append(RetrievalSource.GRAPH)

        if RetrievalSource.MEMORY in context.sources:
            tasks.append(self._search_memory(context))
            source_mapping.append(RetrievalSource.MEMORY)

        if RetrievalSource.VECTOR in context.sources:
            tasks.append(self._search_vector(context))
            source_mapping.append(RetrievalSource.VECTOR)

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect timing and items
        all_items = []
        metrics = {
            "graph_search_time_ms": 0.0,
            "memory_search_time_ms": 0.0,
            "vector_search_time_ms": 0.0
        }

        for idx, (source, result) in enumerate(zip(source_mapping, results)):
            if isinstance(result, BaseException):
                # In production, log the error. For now, skip failed source.
                continue

            items, duration_ms = result
            all_items.extend(items)

            if source == RetrievalSource.GRAPH:
                metrics["graph_search_time_ms"] = duration_ms
            elif source == RetrievalSource.MEMORY:
                metrics["memory_search_time_ms"] = duration_ms
            elif source == RetrievalSource.VECTOR:
                metrics["vector_search_time_ms"] = duration_ms

        total_candidates = len(all_items)

        # Rank
        t_rank_start = time.perf_counter()
        ranked_items = self._ranking_strategy.rank(context, all_items)
        ranking_time_ms = (time.perf_counter() - t_rank_start) * 1000

        total_time_ms = (time.perf_counter() - t_start) * 1000

        retrieval_metrics = RetrievalMetrics(
            graph_search_time_ms=metrics["graph_search_time_ms"],
            memory_search_time_ms=metrics["memory_search_time_ms"],
            vector_search_time_ms=metrics["vector_search_time_ms"],
            ranking_time_ms=ranking_time_ms,
            total_execution_time_ms=total_time_ms,
            total_candidates=total_candidates,
            final_result_count=len(ranked_items)
        )

        # Hash query text for privacy
        query_hash = hashlib.sha256(context.query.query_text.encode('utf-8')).hexdigest()

        # Publish event
        event = RetrievalExecuted(
            correlation_id=context.correlation_id,
            tenant_id=str(context.tenant_id) if context.tenant_id else None,
            query_hash=query_hash,
            sources_used=context.sources,
            ranking_strategy=self._ranking_strategy.__class__.__name__,
            metrics=retrieval_metrics
        )
        self._event_bus.publish(event)

        return RetrievalResult(
            context=context,
            items=ranked_items,
            metrics=retrieval_metrics
        )

    # Internal adapters to standardize repository responses to RetrievalResultItem

    async def _search_graph(self, context: RetrievalContext):
        t0 = time.perf_counter()
        # IKnowledgeRepository currently has `search(query: str, limit: int)`
        # In a full implementation, we'd add tenant_id to the repo layer.
        nodes = await self._knowledge_repo.search(context.query.query_text, limit=context.limit)

        items = []
        for node in nodes:
            items.append(RetrievalResultItem(
                source=RetrievalSource.GRAPH,
                entity_id=node.id,
                content=node.description or node.name,
                relevance_score=0.7, # Mock baseline
                confidence=1.0,
                provenance_chain=["BusinessKnowledgeGraph"],
                metadata={"node_type": node.entity_type}
            ))
        t1 = time.perf_counter()
        return items, (t1 - t0) * 1000

    async def _search_memory(self, context: RetrievalContext):
        t0 = time.perf_counter()
        # IMemoryRepository has `search(query_text: str, limit: int)`
        memories = await self._memory_repo.search(context.query.query_text, limit=context.limit)

        items = []
        for memory in memories:
            if context.tenant_id and memory.tenant_id != context.tenant_id:
                continue
            items.append(RetrievalResultItem(
                source=RetrievalSource.MEMORY,
                entity_id=memory.id,
                content=memory.content,
                relevance_score=0.8, # Mock baseline
                confidence=getattr(memory, "fact_confidence", 1.0),
                provenance_chain=["MemoryEngine", memory.provenance] if memory.provenance else ["MemoryEngine"],
                metadata={"memory_type": memory.memory_type}
            ))
        t1 = time.perf_counter()
        return items, (t1 - t0) * 1000

    async def _search_vector(self, context: RetrievalContext):
        t0 = time.perf_counter()
        items = await self._vector_repo.search(context)
        t1 = time.perf_counter()
        return items, (t1 - t0) * 1000


class RetrievalEngineService:
    """
    Thin orchestrator for the Retrieval Engine.
    Delegates to the configured pipeline.
    """

    def __init__(self, pipeline: IRetrievalPipeline):
        self._pipeline = pipeline

    async def retrieve(self, context: RetrievalContext) -> RetrievalResult:
        """Execute a retrieval operation."""
        return await self._pipeline.execute(context)
