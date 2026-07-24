from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.models.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.models.exceptions import DuplicateMemoryError, MemoryNotFoundError
from app.models.memory import MemoryCreate, MemoryUpdate
from app.repositories.memory_repository import MemoryMetadataRepository


@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    # Mock the table builder chain
    client.table.return_value = client
    client.insert.return_value = client
    client.update.return_value = client
    client.select.return_value = client
    client.eq.return_value = client
    client.is_.return_value = client
    client.order.return_value = client
    client.range.return_value = client
    client.limit.return_value = client

    # We will overwrite execute() individually per test
    client.execute = AsyncMock()
    return client


@pytest.fixture
def repo(mock_supabase_client):
    return MemoryMetadataRepository(mock_supabase_client)


@pytest.mark.asyncio
async def test_create_memory(repo, mock_supabase_client):
    twin_id = uuid4()
    mem_id = uuid4()
    data = MemoryCreate(
        title="Test Memory",
        memory_category=MemoryCategory.EVENT,
        source=MemorySource.USER_INPUT,
        content="Test content",
        importance=Decimal("0.85"),
    )

    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(mem_id),
            "twin_id": str(twin_id),
            "title": "Test Memory",
            "memory_category": "event",
            "source": "user_input",
            "content": "Test content",
            "importance": 0.85,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response

    created = await repo.create(twin_id, data)
    assert created.id == mem_id
    assert created.title == "Test Memory"


@pytest.mark.asyncio
async def test_create_memory_with_metadata(repo, mock_supabase_client):
    twin_id = uuid4()
    mem_id = uuid4()
    data = MemoryCreate(
        title="Test Metadata",
        memory_category=MemoryCategory.EVENT,
        source=MemorySource.USER_INPUT,
        content="Test content",
        importance=Decimal("0.85"),
        metadata={"foo": "bar"},
    )

    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(mem_id),
            "twin_id": str(twin_id),
            "title": "Test Metadata",
            "memory_category": "event",
            "source": "user_input",
            "content": "Test content",
            "importance": 0.85,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {"foo": "bar"},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response

    created = await repo.create(twin_id, data)
    assert created.metadata == {"foo": "bar"}


@pytest.mark.asyncio
async def test_get_by_id(repo, mock_supabase_client):
    mem_id = uuid4()
    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(mem_id),
            "twin_id": str(uuid4()),
            "title": "Test",
            "memory_category": "event",
            "source": "user_input",
            "content": "Test content",
            "importance": 0.5,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response

    fetched = await repo.get_by_id(mem_id)
    assert fetched.id == mem_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase_client.execute.return_value = mock_response

    with pytest.raises(MemoryNotFoundError):
        await repo.get_by_id(uuid4())


@pytest.mark.asyncio
async def test_update_memory(repo, mock_supabase_client):
    mem_id = uuid4()
    update_data = MemoryUpdate(title="Updated Title", importance=Decimal("0.9"))

    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(mem_id),
            "twin_id": str(uuid4()),
            "title": "Updated Title",
            "memory_category": "event",
            "source": "user_input",
            "content": "Content",
            "importance": 0.9,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response

    updated = await repo.update(mem_id, update_data)
    assert updated.title == "Updated Title"
    assert updated.importance == Decimal("0.9")


@pytest.mark.asyncio
async def test_update_memory_enums(repo, mock_supabase_client):
    mem_id = uuid4()
    update_data = MemoryUpdate(
        memory_category=MemoryCategory.REFLECTION, source=MemorySource.DOCUMENT
    )

    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(mem_id),
            "twin_id": str(uuid4()),
            "title": "Title",
            "memory_category": "reflection",
            "source": "document",
            "content": "Content",
            "importance": 0.5,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response

    updated = await repo.update(mem_id, update_data)
    assert updated.memory_category == MemoryCategory.REFLECTION
    assert updated.source == MemorySource.DOCUMENT


@pytest.mark.asyncio
async def test_list_by_twin(repo, mock_supabase_client):
    twin_id = uuid4()
    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(uuid4()),
            "twin_id": str(twin_id),
            "title": "Test",
            "memory_category": "event",
            "source": "user_input",
            "content": "Test content",
            "importance": 0.5,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {},
        }
    ]
    mock_response.count = 1
    mock_supabase_client.execute.return_value = mock_response

    paginated = await repo.list_by_twin(twin_id)
    assert paginated.total_count == 1
    assert len(paginated.items) == 1


@pytest.mark.asyncio
async def test_soft_delete_and_restore(repo, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{"id": str(uuid4())}]
    mock_supabase_client.execute.return_value = mock_response

    await repo.soft_delete(uuid4())
    await repo.restore(uuid4())


@pytest.mark.asyncio
async def test_health_check(repo, mock_supabase_client):
    mock_supabase_client.execute.return_value = MagicMock()
    status = await repo.health_check()
    assert status["status"] == "healthy"


@pytest.mark.asyncio
async def test_update_summary(repo, mock_supabase_client):
    mem_id = uuid4()
    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(mem_id),
            "twin_id": str(uuid4()),
            "title": "Test",
            "memory_category": "event",
            "source": "user_input",
            "content": "Test content",
            "importance": 0.5,
            "embedding_status": "pending",
            "summary": "new summary",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response

    updated = await repo.update_summary(mem_id, "new summary")
    assert updated.summary == "new summary"


@pytest.mark.asyncio
async def test_update_embedding_status(repo, mock_supabase_client):
    mem_id = uuid4()
    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": str(mem_id),
            "twin_id": str(uuid4()),
            "title": "Test",
            "memory_category": "event",
            "source": "user_input",
            "content": "Test content",
            "importance": 0.5,
            "embedding_status": "completed",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response

    updated = await repo.update_embedding_status(mem_id, EmbeddingStatus.COMPLETED)
    assert updated.embedding_status == EmbeddingStatus.COMPLETED


from app.models.exceptions import RepositoryError  # noqa: E402


@pytest.mark.asyncio
async def test_repository_errors(repo, mock_supabase_client):
    mock_supabase_client.execute.side_effect = Exception("DB Error")

    with pytest.raises(RepositoryError):
        await repo.create(
            uuid4(),
            MemoryCreate(
                title="t",
                memory_category=MemoryCategory.EVENT,
                source=MemorySource.USER_INPUT,
                content="c",
                importance=0.5,
            ),
        )

    with pytest.raises(RepositoryError):
        await repo.get_by_id(uuid4())

    with pytest.raises(RepositoryError):
        await repo.update(uuid4(), MemoryUpdate())

    with pytest.raises(RepositoryError):
        await repo.list_by_twin(uuid4())

    with pytest.raises(RepositoryError):
        await repo.soft_delete(uuid4())

    with pytest.raises(RepositoryError):
        await repo.restore(uuid4())

    with pytest.raises(RepositoryError):
        await repo.update_summary(uuid4(), "summary")

    with pytest.raises(RepositoryError):
        await repo.update_embedding_status(uuid4(), EmbeddingStatus.FAILED)


@pytest.mark.asyncio
async def test_not_found_errors_on_updates(repo, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase_client.execute.return_value = mock_response

    with pytest.raises(MemoryNotFoundError):
        await repo.update(uuid4(), MemoryUpdate(title="a"))

    with pytest.raises(MemoryNotFoundError):
        await repo.soft_delete(uuid4())

    with pytest.raises(MemoryNotFoundError):
        await repo.restore(uuid4())

    with pytest.raises(MemoryNotFoundError):
        await repo.update_summary(uuid4(), "sum")

    with pytest.raises(MemoryNotFoundError):
        await repo.update_embedding_status(uuid4(), EmbeddingStatus.COMPLETED)


@pytest.mark.asyncio
async def test_create_memory_duplicate(repo, mock_supabase_client):
    mock_supabase_client.execute.side_effect = Exception(
        "duplicate key value violates unique constraint"
    )

    with pytest.raises(DuplicateMemoryError):
        await repo.create(
            uuid4(),
            MemoryCreate(
                title="t",
                memory_category=MemoryCategory.EVENT,
                source=MemorySource.USER_INPUT,
                content="c",
                importance=0.5,
            ),
        )


@pytest.mark.asyncio
async def test_update_memory_with_metadata(repo, mock_supabase_client):
    mem_id = uuid4()
    update_data = MemoryUpdate(metadata={"key": "value"})

    # Needs to first fetch the memory
    mock_response_fetch = MagicMock()
    mock_response_fetch.data = [
        {
            "id": str(mem_id),
            "twin_id": str(uuid4()),
            "title": "Old Title",
            "memory_category": "event",
            "source": "user_input",
            "content": "Content",
            "importance": 0.5,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {"old": "val"},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response_fetch

    updated = await repo.update(mem_id, update_data)
    assert updated.metadata == {"old": "val"}

    # Let's fix the mock so it returns updated data on the second call (the update call).
    mock_response_update = MagicMock()
    mock_response_update.data = [
        {
            "id": str(mem_id),
            "twin_id": str(uuid4()),
            "title": "Old Title",
            "memory_category": "event",
            "source": "user_input",
            "content": "Content",
            "importance": 0.5,
            "embedding_status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "deleted_at": None,
            "metadata": {"old": "val", "key": "value"},
        }
    ]
    mock_supabase_client.execute.return_value = mock_response_update
    updated2 = await repo.update(mem_id, update_data)
    assert updated2.metadata == {"old": "val", "key": "value"}


@pytest.mark.asyncio
async def test_update_memory_error(repo, mock_supabase_client):
    mock_supabase_client.execute.side_effect = Exception("DB Error")

    with pytest.raises(RepositoryError):
        await repo.update(uuid4(), MemoryUpdate(title="a"))


@pytest.mark.asyncio
async def test_exists(repo, mock_supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{"id": str(uuid4())}]
    mock_supabase_client.execute.return_value = mock_response

    assert await repo.exists(uuid4()) is True

    mock_response.data = []
    assert await repo.exists(uuid4()) is False


@pytest.mark.asyncio
async def test_exists_error(repo, mock_supabase_client):
    mock_supabase_client.execute.side_effect = Exception("DB Error")

    with pytest.raises(RepositoryError):
        await repo.exists(uuid4())


@pytest.mark.asyncio
async def test_list_by_twin_include_deleted(repo, mock_supabase_client):
    twin_id = uuid4()
    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    mock_supabase_client.execute.return_value = mock_response

    paginated = await repo.list_by_twin(twin_id, include_deleted=True)
    assert paginated.total_count == 0


@pytest.mark.asyncio
async def test_health_check_failure(repo, mock_supabase_client):
    mock_supabase_client.execute.side_effect = Exception("DB Error")
    status = await repo.health_check()
    assert status["status"] == "unhealthy"
