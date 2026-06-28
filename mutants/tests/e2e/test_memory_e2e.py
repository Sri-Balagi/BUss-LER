import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.memory import Memory, MemoryCategory, MemorySource, PaginatedMemories
from app.models.enums import EmbeddingStatus


@pytest.mark.asyncio
async def test_memory_e2e_flow(client):
    from app.main import app
    from app.api.v1.dependencies import get_memory_service

    mock_memory_service = AsyncMock()
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service

    """
    Simulates an End-to-End user flow:
    1. Create a Memory
    2. List Memories (verifying creation)
    3. Get Memory Status
    4. Search Memories
    5. Delete Memory
    """
    twin_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    # Setup standard mock memory
    mock_memory = Memory(
        id=memory_id,
        twin_id=twin_id,
        title="E2E Test Memory",
        content="This is an E2E test content.",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={"source": "test"},
        importance=0.8,
        embedding_status=EmbeddingStatus.COMPLETED,
        summary="E2E Summary",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )

    # 1. Create a Memory
    from app.models.results import CreateMemoryResult

    mock_memory_service.create_memory.return_value = CreateMemoryResult(
        memory=mock_memory, dispatched_events=1
    )

    create_payload = {
        "title": "E2E Test Memory",
        "content": "This is an E2E test content.",
        "category": "event",
        "importance": 0.8,
        "metadata": {"source": "test"},
    }

    response = client.post(f"/api/v1/twins/{twin_id}/memories", json=create_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(memory_id)
    assert data["title"] == "E2E Test Memory"

    # 2. List Memories
    mock_memory_service.list_memories.return_value = PaginatedMemories(
        items=[mock_memory], total_count=1, limit=50, offset=0
    )

    response = client.get(f"/api/v1/twins/{twin_id}/memories")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(memory_id)

    # 3. Get Memory Status
    mock_memory_service.get_memory.return_value = mock_memory
    response = client.get(f"/api/v1/memories/{memory_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["embedding_status"] == "completed"

    # 4. Search Memories
    from app.models.results import SearchMemoryResult, MemorySearchResultItem

    mock_memory_service.search_memories.return_value = SearchMemoryResult(
        items=[MemorySearchResultItem(memory=mock_memory, similarity_score=0.95)],
        total_count=1,
    )

    search_payload = {"query_text": "E2E search", "limit": 10, "threshold": 0.7}
    response = client.post(f"/api/v1/twins/{twin_id}/memory/query", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["items"][0]["similarity_score"] == 0.95
    assert data["items"][0]["memory"]["id"] == str(memory_id)

    # 5. Delete Memory
    from app.models.results import DeleteMemoryResult

    mock_memory_service.delete_memory.return_value = DeleteMemoryResult(
        success=True, memory_id=str(memory_id)
    )

    response = client.delete(f"/api/v1/memories/{memory_id}")
    assert response.status_code == 204

    app.dependency_overrides.clear()
