"""Vector Repository Module.

Defines the abstract interface for all vector repositories and
implements the specific MemoryVectorRepository for Qdrant persistence.
"""

from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.config import Settings
from app.domain.memory.vector_repository import AbstractVectorRepository
from app.infrastructure.vectorstore.models import MemoryVectorPayload, MemoryVectorPoint
from app.shared.exceptions.errors import VectorDatabaseError


class MemoryVectorRepository(AbstractVectorRepository):
    """Qdrant implementation of the vector repository for Memories."""

    def __init__(self, client: AsyncQdrantClient, settings: Settings):
        self._client = client
        self._collection = settings.qdrant_collection

    async def upsert(self, point: MemoryVectorPoint) -> None:
        """Upsert a single memory vector into Qdrant."""
        try:
            qdrant_point = models.PointStruct(
                id=str(point.id),
                vector=point.vector,
                payload=point.payload.model_dump(mode="json"),
            )
            await self._client.upsert(
                collection_name=self._collection,
                points=[qdrant_point],
            )
        except Exception as e:
            raise VectorDatabaseError(operation="upsert", detail=str(e))

    async def get_by_id(self, point_id: UUID) -> MemoryVectorPoint | None:
        """Retrieve a memory vector by its ID."""
        try:
            result = await self._client.retrieve(
                collection_name=self._collection,
                ids=[str(point_id)],
                with_vectors=True,
                with_payload=True,
            )
            if not result:
                return None

            record = result[0]
            rec_id = UUID(str(record.id)) if record.id else UUID(int=0)
            rec_vec: list[float] = [float(x) for x in record.vector if isinstance(x, (int, float))] if isinstance(record.vector, list) else []
            rec_payload = MemoryVectorPayload.model_validate(record.payload or {})
            return MemoryVectorPoint(
                id=rec_id,
                vector=rec_vec,
                payload=rec_payload,
            )
        except Exception as e:
            raise VectorDatabaseError(operation="get_by_id", detail=str(e))

    async def delete(self, point_id: UUID) -> None:
        """Delete a memory vector from Qdrant."""
        try:
            await self._client.delete(
                collection_name=self._collection,
                points_selector=models.PointIdsList(points=[str(point_id)]),
            )
        except Exception as e:
            raise VectorDatabaseError(operation="delete", detail=str(e))

    async def search(
        self,
        query_vector: list[float],
        twin_id: UUID,
        limit: int = 5,
    ) -> list[MemoryVectorPoint]:
        """Search vectors strictly filtered by twin_id."""
        try:
            results = await self._client.query_points(
                collection_name=self._collection,
                query=query_vector,
                limit=limit,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="twin_id",
                            match=models.MatchValue(value=str(twin_id)),
                        )
                    ]
                ),
                with_payload=True,
                with_vectors=True,
            )

            points = []
            for hit in results.points:
                hit_id = UUID(str(hit.id)) if hit.id else UUID(int=0)
                hit_vec: list[float] = [float(x) for x in hit.vector if isinstance(x, (int, float))] if isinstance(hit.vector, list) else []
                hit_payload = MemoryVectorPayload.model_validate(hit.payload or {})
                points.append(
                    MemoryVectorPoint(
                        id=hit_id,
                        vector=hit_vec,
                        payload=hit_payload,
                        score=hit.score,
                    )
                )
            return points

        except Exception as e:
            raise VectorDatabaseError(operation="search", detail=str(e))
