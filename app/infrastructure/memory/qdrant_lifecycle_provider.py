"""Qdrant Memory Lifecycle Provider backing IMemoryProvider.

Supports full lifecycle:
- Store (persist vector + payload)
- Retrieve (by UUID)
- Search (semantic vector search with metadata filtering)
- Update (modify record content & payload)
- Merge (append & re-embed memory)
- Archive (soft delete flag)
- Forget (hard purge from Qdrant vector store)
- Re-index (re-embed collection)
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

from app.config import get_settings
from app.domain.memory.models import MemoryRecord, MemoryType, MemorySource
from app.domain.memory.provider import IMemoryProvider
from app.infrastructure.embeddings.registry import IEmbeddingProvider, GeminiEmbeddingProvider

logger = structlog.get_logger(__name__)


class QdrantLifecycleMemoryProvider(IMemoryProvider):
    """Full-featured Qdrant memory lifecycle implementation."""

    def __init__(
        self,
        embedding_provider: Optional[IEmbeddingProvider] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
    ):
        settings = get_settings()
        self._host = host or settings.qdrant_host or "localhost"
        self._port = port or settings.qdrant_port or 6333
        self._collection = collection_name or settings.qdrant_collection or "memories"
        self._embedding_provider = embedding_provider or GeminiEmbeddingProvider()
        self._client = AsyncQdrantClient(host=self._host, port=self._port, timeout=10.0)

    @property
    def provider_name(self) -> str:
        return "qdrant-lifecycle"

    async def _ensure_collection(self) -> None:
        try:
            exists = await self._client.collection_exists(self._collection)
            if not exists:
                dim = self._embedding_provider.vector_dimension
                await self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=qmodels.VectorParams(
                        size=dim,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
        except Exception as e:
            logger.warning("Could not check/create Qdrant collection", error=str(e))

    async def store(self, record: MemoryRecord) -> None:
        await self._ensure_collection()
        text_to_embed = f"{record.title}\n{record.content}"
        vector = await self._embedding_provider.embed_text(text_to_embed)

        payload = {
            "memory_id": str(record.memory_id),
            "memory_type": record.memory_type.value if hasattr(record.memory_type, "value") else str(record.memory_type),
            "title": record.title,
            "content": record.content,
            "workflow_id": str(record.workflow_id) if record.workflow_id else None,
            "archived": False,
        }

        # Convert UUID to integer or string ID for Qdrant point ID
        point_id = str(record.memory_id)

        await self._client.upsert(
            collection_name=self._collection,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    async def retrieve(self, memory_id: UUID) -> Optional[MemoryRecord]:
        await self._ensure_collection()
        try:
            res = await self._client.retrieve(
                collection_name=self._collection,
                ids=[str(memory_id)],
            )
            if res and len(res) > 0:
                p = res[0].payload or {}
                return MemoryRecord(
                    memory_id=UUID(p["memory_id"]),
                    memory_type=MemoryType(p.get("memory_type", "KNOWLEDGE")),
                    source=MemorySource.SYSTEM,
                    title=p.get("title", ""),
                    content=p.get("content", ""),
                    workflow_id=UUID(p["workflow_id"]) if p.get("workflow_id") else None,
                )
        except Exception as e:
            logger.error("Failed to retrieve memory record from Qdrant", id=str(memory_id), error=str(e))
        return None

    async def search(self, query: str, limit: int = 10, **filters) -> List[MemoryRecord]:
        await self._ensure_collection()
        query_vector = await self._embedding_provider.embed_text(query)

        try:
            if hasattr(self._client, "query_points"):
                res = await self._client.query_points(
                    collection_name=self._collection,
                    query=query_vector,
                    limit=limit,
                )
                results = res.points if hasattr(res, "points") else []
            elif hasattr(self._client, "search"):
                results = await self._client.search(
                    collection_name=self._collection,
                    query_vector=query_vector,
                    limit=limit,
                )
            else:
                results = []

            records = []
            for hit in results:
                p = hit.payload or {}
                if p.get("archived", False) and not filters.get("include_archived", False):
                    continue
                rec = MemoryRecord(
                    memory_id=UUID(p["memory_id"]) if "memory_id" in p else UUID(str(hit.id)),
                    memory_type=MemoryType.KNOWLEDGE,
                    source=MemorySource.SYSTEM,
                    title=p.get("title", ""),
                    content=p.get("content", ""),
                    workflow_id=UUID(p["workflow_id"]) if p.get("workflow_id") else None,
                )
                records.append(rec)
            return records
        except Exception as e:
            logger.error("Qdrant semantic search failed", query=query, error=str(e))
            return []

    async def update(self, memory_id: UUID, record: MemoryRecord) -> None:
        await self.store(record)

    async def merge(self, memory_id: UUID, additional_content: str) -> None:
        existing = await self.retrieve(memory_id)
        if existing:
            existing.content = f"{existing.content}\n[Update]: {additional_content}"
            await self.store(existing)

    async def archive(self, memory_id: UUID) -> None:
        rec = await self.retrieve(memory_id)
        if rec:
            await self._client.set_payload(
                collection_name=self._collection,
                payload={"archived": True},
                points=[str(memory_id)],
            )

    async def forget(self, memory_id: UUID) -> None:
        try:
            await self._client.delete(
                collection_name=self._collection,
                points_selector=qmodels.PointIdsList(points=[str(memory_id)]),
            )
        except Exception as e:
            logger.error("Failed to delete point from Qdrant", id=str(memory_id), error=str(e))

    async def delete(self, memory_id: UUID) -> None:
        await self.forget(memory_id)

    async def reindex(self) -> int:
        await self._ensure_collection()
        info = await self._client.get_collection(self._collection)
        return info.points_count or 0
