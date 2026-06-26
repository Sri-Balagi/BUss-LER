import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from decimal import Decimal

from app.models.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.models.exceptions import ServiceError, RepositoryError
from app.models.memory import Memory, PaginatedMemories
from app.services.memory_service import MemoryService
from app.core.context import OperationContext
from app.models.commands import CreateMemoryCommand, DeleteMemoryCommand, RestoreMemoryCommand
from app.models.queries import MemorySearchQuery
from app.models.results import CreateMemoryResult, SearchMemoryResult


@pytest.fixture
def mock_metadata_repo():
    return AsyncMock()

@pytest.fixture
def mock_vector_repo():
    return AsyncMock()

@pytest.fixture
def mock_ai_kernel():
    return AsyncMock()

@pytest.fixture
def mock_event_bus():
    return AsyncMock()

@pytest.fixture
def memory_service(mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus):
    return MemoryService(mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus)

@pytest.fixture
def ctx():
    return OperationContext()


@pytest.mark.asyncio
async def test_create_memory_success(memory_service, mock_metadata_repo, mock_event_bus, ctx):
    twin_id = uuid4()
    mem_id = uuid4()
    
    cmd = CreateMemoryCommand(
        twin_id=twin_id,
        content="Test content",
        memory_category=MemoryCategory.OBSERVATION,
        importance=0.5
    )

    mock_memory = Memory(
        id=mem_id,
        twin_id=twin_id,
        title="Test",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.USER_INPUT,
        content="Test content",
        importance=Decimal("0.5"),
        embedding_status=EmbeddingStatus.PENDING,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        metadata={}
    )
    mock_metadata_repo.create.return_value = mock_memory

    result = await memory_service.create_memory(ctx, cmd)
    assert result.memory.id == mem_id
    assert result.dispatched_events == 1
    mock_event_bus.publish.assert_called_once()
    mock_metadata_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_memory_repository_error(memory_service, mock_metadata_repo, ctx):
    mock_metadata_repo.create.side_effect = RepositoryError("db", "failure")
    
    cmd = CreateMemoryCommand(
        twin_id=uuid4(),
        content="test",
        memory_category=MemoryCategory.OBSERVATION
    )
    
    with pytest.raises(ServiceError):
        await memory_service.create_memory(ctx, cmd)


@pytest.mark.asyncio
async def test_delete_memory_orchestration(memory_service, mock_metadata_repo, mock_vector_repo, ctx):
    mem_id = uuid4()
    cmd = DeleteMemoryCommand(memory_id=mem_id)
    result = await memory_service.delete_memory(ctx, cmd)
    
    assert result.success is True
    mock_vector_repo.delete.assert_called_once_with(mem_id)
    mock_metadata_repo.soft_delete.assert_called_once_with(mem_id)


@pytest.mark.asyncio
async def test_search_memories_orchestration(memory_service, mock_metadata_repo, mock_vector_repo, mock_ai_kernel, ctx):
    twin_id = uuid4()
    mem_id = uuid4()
    
    query = MemorySearchQuery(
        twin_id=twin_id,
        query_text="search this",
        limit=10,
        threshold=0.7
    )

    # Mock AI Kernel
    mock_embed_response = MagicMock()
    mock_embed_response.vector = [0.1, 0.2, 0.3]
    mock_ai_kernel.embed.return_value = mock_embed_response

    # Mock Vector Repo Search
    mock_vector_result = MagicMock()
    mock_vector_result.id = mem_id
    mock_vector_result.score = 0.95
    mock_vector_repo.search.return_value = [mock_vector_result]

    # Mock Metadata Repo Get
    mock_memory = Memory(
        id=mem_id,
        twin_id=twin_id,
        title="Test",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.USER_INPUT,
        content="Test content",
        importance=Decimal("0.5"),
        embedding_status=EmbeddingStatus.COMPLETED,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        metadata={},
        is_deleted=False
    )
    mock_metadata_repo.get_by_id.return_value = mock_memory

    result = await memory_service.search_memories(ctx, query)
    
    assert isinstance(result, SearchMemoryResult)
    assert result.total_count == 1
    assert result.items[0].memory.id == mem_id
    assert result.items[0].similarity_score == 0.95
    
    mock_ai_kernel.embed.assert_called_once()
    mock_vector_repo.search.assert_called_once_with(
        query_vector=[0.1, 0.2, 0.3], limit=10, twin_id=twin_id
    )
    mock_metadata_repo.get_by_id.assert_called_once_with(mem_id)


@pytest.mark.asyncio
async def test_list_memories(memory_service, mock_metadata_repo, ctx):
    twin_id = uuid4()
    mock_metadata_repo.list_by_twin.return_value = PaginatedMemories(
        items=[], total_count=0, limit=50, offset=0
    )
    
    res = await memory_service.list_memories(ctx, twin_id)
    assert res.total_count == 0
    mock_metadata_repo.list_by_twin.assert_called_once_with(twin_id, 50, 0, False)

@pytest.mark.asyncio
async def test_list_memories_with_category(memory_service, mock_metadata_repo, ctx):
    twin_id = uuid4()
    
    # Create two memories with different categories
    mem1 = Memory(id=uuid4(), twin_id=twin_id, memory_category=MemoryCategory.EVENT, title="M1", content="C1", importance=0.5, embedding_status=EmbeddingStatus.PENDING, created_at="2023-01-01T00:00:00Z", updated_at="2023-01-01T00:00:00Z", metadata={}, source=MemorySource.USER_INPUT)
    mem2 = Memory(id=uuid4(), twin_id=twin_id, memory_category=MemoryCategory.OBSERVATION, title="M2", content="C2", importance=0.5, embedding_status=EmbeddingStatus.PENDING, created_at="2023-01-01T00:00:00Z", updated_at="2023-01-01T00:00:00Z", metadata={}, source=MemorySource.USER_INPUT)
    
    mock_metadata_repo.list_by_twin.return_value = PaginatedMemories(
        items=[mem1, mem2], total_count=2, limit=50, offset=0
    )
    
    res = await memory_service.list_memories(ctx, twin_id, category=MemoryCategory.EVENT)
    assert res.total_count == 1
    assert res.items[0].id == mem1.id

@pytest.mark.asyncio
async def test_list_memories_error(memory_service, mock_metadata_repo, ctx):
    mock_metadata_repo.list_by_twin.side_effect = RepositoryError("db", "failure")
    with pytest.raises(ServiceError):
        await memory_service.list_memories(ctx, uuid4())

@pytest.mark.asyncio
async def test_delete_memory_error(memory_service, mock_metadata_repo, ctx):
    mock_metadata_repo.soft_delete.side_effect = RepositoryError("db", "failure")
    with pytest.raises(ServiceError):
        await memory_service.delete_memory(ctx, DeleteMemoryCommand(memory_id=uuid4()))

@pytest.mark.asyncio
async def test_restore_memory(memory_service, mock_metadata_repo, ctx):
    mem_id = uuid4()
    await memory_service.restore_memory(ctx, RestoreMemoryCommand(memory_id=mem_id))
    mock_metadata_repo.restore.assert_called_once_with(mem_id)

@pytest.mark.asyncio
async def test_restore_memory_error(memory_service, mock_metadata_repo, ctx):
    mock_metadata_repo.restore.side_effect = RepositoryError("db", "failure")
    with pytest.raises(ServiceError):
        await memory_service.restore_memory(ctx, RestoreMemoryCommand(memory_id=uuid4()))

@pytest.mark.asyncio
async def test_update_summary(memory_service, mock_metadata_repo, ctx):
    mem_id = uuid4()
    mock_mem = MagicMock()
    mock_metadata_repo.update_summary.return_value = mock_mem
    res = await memory_service.update_summary(ctx, mem_id, "new sum")
    assert res == mock_mem
    mock_metadata_repo.update_summary.assert_called_once_with(mem_id, "new sum")

@pytest.mark.asyncio
async def test_update_summary_error(memory_service, mock_metadata_repo, ctx):
    mock_metadata_repo.update_summary.side_effect = RepositoryError("db", "failure")
    with pytest.raises(ServiceError):
        await memory_service.update_summary(ctx, uuid4(), "sum")

@pytest.mark.asyncio
async def test_update_embedding_status(memory_service, mock_metadata_repo, ctx):
    mem_id = uuid4()
    mock_mem = MagicMock()
    mock_metadata_repo.update_embedding_status.return_value = mock_mem
    res = await memory_service.update_embedding_status(ctx, mem_id, EmbeddingStatus.COMPLETED)
    assert res == mock_mem

@pytest.mark.asyncio
async def test_update_embedding_status_error(memory_service, mock_metadata_repo, ctx):
    mock_metadata_repo.update_embedding_status.side_effect = RepositoryError("db", "failure")
    with pytest.raises(ServiceError):
        await memory_service.update_embedding_status(ctx, uuid4(), EmbeddingStatus.FAILED)

@pytest.mark.asyncio
async def test_get_memory(memory_service, mock_metadata_repo, ctx):
    mem_id = uuid4()
    mock_metadata_repo.get_by_id.return_value = "mem"
    assert await memory_service.get_memory(ctx, mem_id) == "mem"

@pytest.mark.asyncio
async def test_get_memory_error(memory_service, mock_metadata_repo, ctx):
    mock_metadata_repo.get_by_id.side_effect = RepositoryError("db", "failure")
    with pytest.raises(ServiceError):
        await memory_service.get_memory(ctx, uuid4())

@pytest.mark.asyncio
async def test_search_memories_no_ai_kernel(mock_metadata_repo, mock_vector_repo, mock_event_bus, ctx):
    service = MemoryService(mock_metadata_repo, mock_vector_repo, None, mock_event_bus)
    with pytest.raises(ServiceError):
        await service.search_memories(ctx, MemorySearchQuery(twin_id=uuid4(), query_text=""))

@pytest.mark.asyncio
async def test_search_memories_empty_vector_results(memory_service, mock_ai_kernel, mock_vector_repo, ctx):
    mock_ai_kernel.embed.return_value = MagicMock(vector=[1, 2])
    mock_vector_repo.search.return_value = []
    
    res = await memory_service.search_memories(ctx, MemorySearchQuery(twin_id=uuid4(), query_text=""))
    assert res.total_count == 0
    assert len(res.items) == 0

@pytest.mark.asyncio
async def test_search_memories_filters(memory_service, mock_ai_kernel, mock_vector_repo, mock_metadata_repo, ctx):
    twin_id = uuid4()
    mock_ai_kernel.embed.return_value = MagicMock(vector=[1, 2])
    
    res1 = MagicMock(id=uuid4(), score=0.9)
    res2 = MagicMock(id=uuid4(), score=0.6) # Fails threshold 0.8
    res3 = MagicMock(id=uuid4(), score=0.9) # Fails category
    res4 = MagicMock(id=uuid4(), score=0.9) # Fails importance
    res5 = MagicMock(id=uuid4(), score=0.9) # Fails include_deleted
    res6 = MagicMock(id=uuid4(), score=0.9) # RepositoryError fetching metadata

    mock_vector_repo.search.return_value = [res1, res2, res3, res4, res5, res6]
    
    base_attrs = {
        "twin_id": twin_id,
        "title": "Title",
        "content": "Content",
        "source": MemorySource.USER_INPUT,
        "embedding_status": EmbeddingStatus.PENDING,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "metadata": {}
    }
    
    mem1 = Memory(id=res1.id, memory_category=MemoryCategory.EVENT, importance=0.5, **base_attrs)
    mem3 = Memory(id=res3.id, memory_category=MemoryCategory.OBSERVATION, importance=0.5, **base_attrs)
    mem4 = Memory(id=res4.id, memory_category=MemoryCategory.EVENT, importance=0.1, **base_attrs)
    mem5 = Memory(id=res5.id, memory_category=MemoryCategory.EVENT, importance=0.5, deleted_at="2023-01-01T00:00:00Z", **base_attrs)
    
    async def mock_get_by_id(mem_id):
        if mem_id == res1.id: return mem1
        if mem_id == res3.id: return mem3
        if mem_id == res4.id: return mem4
        if mem_id == res5.id: return mem5
        if mem_id == res6.id: raise RepositoryError("db", "fail")
        return None
        
    mock_metadata_repo.get_by_id.side_effect = mock_get_by_id
    
    query = MemorySearchQuery(
        twin_id=twin_id, 
        query_text="", 
        threshold=0.8,
        category=MemoryCategory.EVENT,
        min_importance=0.4,
        include_deleted=False
    )
    
    res = await memory_service.search_memories(ctx, query)
    assert res.total_count == 1
    assert res.items[0].memory.id == mem1.id

@pytest.mark.asyncio
async def test_search_memories_general_exception(memory_service, mock_ai_kernel, ctx):
    mock_ai_kernel.embed.side_effect = Exception("General error")
    with pytest.raises(ServiceError):
        await memory_service.search_memories(ctx, MemorySearchQuery(twin_id=uuid4(), query_text=""))
