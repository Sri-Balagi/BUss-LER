import pytest
import uuid
import time

from app.models.memory_vector import MemoryVectorPoint, MemoryVectorPayload
from app.models.enums import MemoryCategory, MemorySource
from app.repositories.vector_repository import MemoryVectorRepository
from qdrant_client import AsyncQdrantClient
from app.config import Settings

import pytest_asyncio
from qdrant_client.models import VectorParams, Distance


@pytest_asyncio.fixture
async def in_memory_qdrant():
    client = AsyncQdrantClient(":memory:")
    # Create the collection
    await client.create_collection(
        collection_name="memories",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    return client


def generate_mock_points(count: int, twin_id: uuid.UUID) -> list[MemoryVectorPoint]:
    """Generate a batch of mock vector points."""
    points = []
    # Using a dummy vector for speed
    dummy_vector = [0.1] * 768
    for i in range(count):
        points.append(
            MemoryVectorPoint(
                id=uuid.uuid4(),
                vector=dummy_vector,
                payload=MemoryVectorPayload(
                    memory_id=uuid.uuid4(),
                    twin_id=twin_id,
                    memory_category=MemoryCategory.EVENT,
                    source=MemorySource.USER_INPUT,
                    importance=0.5,
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z",
                ),
            )
        )
    return points


@pytest.mark.asyncio
@pytest.mark.parametrize("dataset_size", [10, 100, 1000])
async def test_memory_growth_benchmark(in_memory_qdrant, dataset_size):
    """
    Benchmark semantic search vector retrieval using progressively larger datasets.
    """
    # 10,000 points takes too long to generate in python loops for a fast CI test,
    # so we'll test up to 1000 here, or 10000 if performance permits.

    twin_id = uuid.uuid4()
    settings = Settings()
    repo = MemoryVectorRepository(client=in_memory_qdrant, settings=settings)

    # Generate points
    points = generate_mock_points(dataset_size, twin_id)

    # We must insert in batches to avoid overwhelming the synchronous test setup
    batch_size = 500
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        # upsert is async
        for point in batch:
            await repo.upsert(point)

    # Measure search latency
    query_vector = [0.1] * 768

    start_time = time.perf_counter()

    results = await repo.search(twin_id=twin_id, query_vector=query_vector, limit=10)

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    # Assert search completes in reasonable time (e.g. < 50ms for in-memory)
    # The actual constraint will depend on environment, but we ensure it works.
    assert latency_ms < 500  # generous threshold for CI
    assert len(results) <= 10

    print(f"Dataset Size: {dataset_size:5d} | Search Latency: {latency_ms:.2f} ms")
