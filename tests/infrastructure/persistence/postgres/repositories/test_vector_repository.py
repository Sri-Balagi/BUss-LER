from datetime import UTC, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.config import Settings
from app.infrastructure.persistence.postgres.repositories.vector_repository import (
    MemoryVectorRepository,
)
from app.infrastructure.vectorstore.models import MemoryVectorPayload, MemoryVectorPoint
from app.infrastructure.vectorstore.qdrant import QdrantService
from app.shared.enums import MemoryCategory, MemorySource

# Define settings that point to a test collection
test_settings = Settings(
    qdrant_collection="test_memories",
    qdrant_vector_size=4,
    qdrant_distance_metric="Cosine",
)


@pytest.fixture(scope="module")
async def vector_repo():
    """Fixture to provide a MemoryVectorRepository initialized against an in-memory collection."""
    from qdrant_client import AsyncQdrantClient

    client = AsyncQdrantClient(location=":memory:")

    # Overwrite the get_client to return our in-memory client
    original_get_client = QdrantService.get_client
    QdrantService.get_client = classmethod(lambda cls, s: client)

    await QdrantService.initialize_collections(test_settings)
    repo = MemoryVectorRepository(client=client, settings=test_settings)
    yield repo

    # Teardown
    QdrantService.get_client = original_get_client
    await client.close()


@pytest.mark.asyncio
async def test_upsert_and_retrieve(vector_repo):
    """Test upserting a vector and then retrieving it."""
    point_id = uuid4()
    twin_id = uuid4()

    payload = MemoryVectorPayload(
        memory_id=point_id,
        twin_id=twin_id,
        memory_category=MemoryCategory.EVENT,
        source=MemorySource.OBSERVATION,
        importance=Decimal("0.50"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    vector = [0.1, 0.2, 0.3, 0.4]

    point = MemoryVectorPoint(
        id=point_id,
        vector=vector,
        payload=payload,
    )

    # Upsert
    await vector_repo.upsert(point)

    # Retrieve
    retrieved = await vector_repo.get_by_id(point_id)
    assert retrieved is not None
    assert retrieved.id == point_id
    assert retrieved.payload.twin_id == twin_id
    assert len(retrieved.vector) == 4


@pytest.mark.asyncio
async def test_search_vectors(vector_repo):
    """Test searching vectors strictly filtered by twin_id."""
    twin_id_1 = uuid4()
    twin_id_2 = uuid4()

    # Create two points for twin 1
    for _ in range(2):
        point_id = uuid4()
        payload = MemoryVectorPayload(
            memory_id=point_id,
            twin_id=twin_id_1,
            memory_category=MemoryCategory.TASK,
            source=MemorySource.EXECUTION,
            importance=Decimal("0.80"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        point = MemoryVectorPoint(id=point_id, vector=[1.0, 0.0, 0.0, 0.0], payload=payload)
        await vector_repo.upsert(point)

    # Create one point for twin 2
    point_id_2 = uuid4()
    payload_2 = MemoryVectorPayload(
        memory_id=point_id_2,
        twin_id=twin_id_2,
        memory_category=MemoryCategory.TASK,
        source=MemorySource.EXECUTION,
        importance=Decimal("0.80"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    point_2 = MemoryVectorPoint(id=point_id_2, vector=[1.0, 0.0, 0.0, 0.0], payload=payload_2)
    await vector_repo.upsert(point_2)

    # Search for twin 1
    results = await vector_repo.search(
        query_vector=[1.0, 0.0, 0.0, 0.0], twin_id=twin_id_1, limit=5
    )

    # Must only return twin 1 results
    assert len(results) == 2
    for r in results:
        assert r.payload.twin_id == twin_id_1


@pytest.mark.asyncio
async def test_delete_vector(vector_repo):
    """Test vector deletion."""
    point_id = uuid4()
    payload = MemoryVectorPayload(
        memory_id=point_id,
        twin_id=uuid4(),
        memory_category=MemoryCategory.EVENT,
        source=MemorySource.OBSERVATION,
        importance=Decimal("0.50"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    point = MemoryVectorPoint(id=point_id, vector=[0.0, 1.0, 0.0, 0.0], payload=payload)

    await vector_repo.upsert(point)
    retrieved = await vector_repo.get_by_id(point_id)
    assert retrieved is not None

    await vector_repo.delete(point_id)
    retrieved_after_delete = await vector_repo.get_by_id(point_id)
    assert retrieved_after_delete is None


@pytest.mark.asyncio
async def test_health_check(vector_repo):
    """Test health check using QdrantService."""
    status = await QdrantService.health_check(test_settings)
    assert status["qdrant"] is True
    # The collection was created by the fixture, so it should exist and have the right vector size
    assert status["collection"] is True
    assert status["vector_size"] == 4
    assert status["status"] == "healthy"
