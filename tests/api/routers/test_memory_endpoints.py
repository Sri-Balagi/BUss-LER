import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.api.v1.dependencies import get_memory_service
from app.models.enums import MemoryCategory, EmbeddingStatus, MemorySource
from app.models.memory import Memory, PaginatedMemories
from app.models.results import CreateMemoryResult, SearchMemoryResult, DeleteMemoryResult, MemorySearchResultItem


@pytest.fixture
def mock_memory_service():
    service = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_create_memory(mock_memory_service):
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    twin_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=twin_id,
        content="Test memory",
        title="Untitled",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.OBSERVATION,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.PENDING,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_memory_service.create_memory.return_value = CreateMemoryResult(
        memory=mock_memory, dispatched_events=1
    )

    payload = {
        "content": "Test memory"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/twins/{twin_id}/memories", json=payload)
        
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(memory_id)
    assert data["content"] == "Test memory"
    assert "X-Request-ID" in response.headers

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_memory(mock_memory_service):
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        content="Test get",
        title="Untitled",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.OBSERVATION,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.COMPLETED,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_memory_service.get_memory.return_value = mock_memory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/memories/{memory_id}")
        
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(memory_id)
    assert data["embedding_status"] == "completed"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_semantic_query(mock_memory_service):
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    twin_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=twin_id,
        content="Result",
        title="Untitled",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.OBSERVATION,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.COMPLETED,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_item = MemorySearchResultItem(memory=mock_memory, similarity_score=0.95)
    mock_memory_service.search_memories.return_value = SearchMemoryResult(
        items=[mock_item],
        total_count=1
    )

    payload = {
        "query_text": "Find result"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/twins/{twin_id}/memory/query", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["items"][0]["similarity_score"] == 0.95
    assert data["items"][0]["memory"]["id"] == str(memory_id)

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_list_memories(mock_memory_service):
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    twin_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=twin_id,
        content="Test content",
        title="Untitled",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.PENDING,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_memory_service.list_memories.return_value = PaginatedMemories(
        items=[mock_memory],
        total_count=1,
        limit=10,
        offset=0
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/twins/{twin_id}/memories?limit=10&offset=0&category=event&include_deleted=false")
        
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["items"][0]["id"] == str(memory_id)

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_memory(mock_memory_service):
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    memory_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(f"/api/v1/memories/{memory_id}")
        
    assert response.status_code == 204

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_restore_memory(mock_memory_service):
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        content="Test content",
        title="Untitled",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.PENDING,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_memory_service.restore_memory.return_value = MagicMock(memory=mock_memory)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/v1/memories/{memory_id}/restore")
        
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(memory_id)

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_memory_status(mock_memory_service):
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        content="Test content",
        title="Untitled",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.PROCESSING,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_memory_service.get_memory.return_value = mock_memory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/memories/{memory_id}/status")
        
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(memory_id)
    assert data["embedding_status"] == "processing"

    app.dependency_overrides.clear()
