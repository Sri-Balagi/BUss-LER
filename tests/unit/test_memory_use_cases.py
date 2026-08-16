import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.memory.create_memory import CreateMemoryUseCase
from app.application.memory.delete_memory import DeleteMemoryUseCase
from app.application.memory.update_memory import UpdateMemoryUseCase
from app.infrastructure.ai.models import AIResponseMetadata, EmbeddingResponse
from app.intelligence.learning.repository.memory import Memory, MemoryCreate, MemoryUpdate
from app.shared.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.shared.events.models import EventType


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
    return MagicMock()


@pytest.mark.asyncio
async def test_create_memory_use_case_orchestration(
    mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus
):
    use_case = CreateMemoryUseCase(
        metadata_repo=mock_metadata_repo,
        vector_repo=mock_vector_repo,
        ai_kernel=mock_ai_kernel,
        event_bus=mock_event_bus,
    )

    twin_id = uuid.uuid4()
    memory_id = uuid.uuid4()
    correlation_id = "test-corr-123"

    mock_memory = Memory(
        id=memory_id,
        twin_id=twin_id,
        title="Test Memory",
        content="Test content for memory that is short.",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )

    mock_metadata_repo.create.return_value = mock_memory

    mock_embed_res = EmbeddingResponse(
        vector=[0.1, 0.2, 0.3],
        metadata=AIResponseMetadata(model="test-embed-model", provider="test", latency_ms=10),
    )
    mock_ai_kernel.embed.return_value = mock_embed_res
    mock_metadata_repo.update_embedding_status.return_value = mock_memory

    data = MemoryCreate(
        title="Test Memory",
        content="Test content for memory that is short.",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
    )

    result = await use_case.execute(twin_id, data, correlation_id)

    assert result.id == memory_id
    mock_metadata_repo.create.assert_called_once_with(twin_id, data)
    mock_ai_kernel.embed.assert_called_once()
    mock_vector_repo.upsert.assert_called_once()
    mock_metadata_repo.update_embedding_status.assert_called_once_with(
        memory_id, EmbeddingStatus.COMPLETED
    )
    mock_event_bus.publish.assert_called_once()


@pytest.mark.asyncio
async def test_update_memory_use_case_no_content_change(
    mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus
):
    use_case = UpdateMemoryUseCase(mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus)
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Test",
        content="Same content",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_metadata_repo.get_by_id.return_value = mock_memory
    mock_metadata_repo.update.return_value = mock_memory

    data = MemoryUpdate(title="New Title", content="Same content")
    result = await use_case.execute(memory_id, data, "corr-123")

    assert result.id == memory_id
    mock_metadata_repo.update.assert_called_once_with(memory_id, data)
    mock_ai_kernel.embed.assert_not_called()
    mock_vector_repo.upsert.assert_not_called()


@pytest.mark.asyncio
async def test_update_memory_use_case_content_change(
    mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus
):
    use_case = UpdateMemoryUseCase(mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus)
    memory_id = uuid.uuid4()

    mock_original_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Test",
        content="Old content",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_updated_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Test",
        content="New content that is very long " * 10,
        summary=None,
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_metadata_repo.get_by_id.return_value = mock_original_memory
    mock_metadata_repo.update.return_value = mock_updated_memory
    mock_metadata_repo.update_summary.return_value = mock_updated_memory
    mock_metadata_repo.update_embedding_status.return_value = mock_updated_memory

    mock_ai_kernel.summarize.return_value = "Summary"
    mock_ai_kernel.embed.return_value = EmbeddingResponse(
        vector=[0.1], metadata=AIResponseMetadata(model="t", provider="t", latency_ms=10)
    )

    data = MemoryUpdate(title="Test", content="New content that is very long " * 10)
    await use_case.execute(memory_id, data, "corr-123")

    assert data.embedding_status == EmbeddingStatus.PENDING
    assert data.summary is None

    mock_metadata_repo.update.assert_called_once_with(memory_id, data)
    mock_ai_kernel.summarize.assert_called_once()
    mock_metadata_repo.update_summary.assert_called_once()
    mock_ai_kernel.embed.assert_called_once()
    mock_vector_repo.upsert.assert_called_once()
    mock_metadata_repo.update_embedding_status.assert_called_once_with(memory_id, EmbeddingStatus.COMPLETED)
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert event.event_type == EventType.UPDATED


@pytest.mark.asyncio
async def test_update_memory_use_case_embed_failure(
    mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus
):
    use_case = UpdateMemoryUseCase(mock_metadata_repo, mock_vector_repo, mock_ai_kernel, mock_event_bus)
    memory_id = uuid.uuid4()

    mock_original_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Test",
        content="Old content",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_updated_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Test",
        content="New content",
        summary="A summary",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_metadata_repo.get_by_id.return_value = mock_original_memory
    mock_metadata_repo.update.return_value = mock_updated_memory
    mock_metadata_repo.update_embedding_status.return_value = mock_updated_memory

    mock_ai_kernel.embed.side_effect = Exception("Embed Failed")

    data = MemoryUpdate(content="New content")
    await use_case.execute(memory_id, data, "corr-123")

    mock_metadata_repo.update_embedding_status.assert_called_once_with(memory_id, EmbeddingStatus.FAILED)


@pytest.mark.asyncio
async def test_delete_memory_use_case(
    mock_metadata_repo, mock_vector_repo, mock_event_bus
):
    use_case = DeleteMemoryUseCase(mock_metadata_repo, mock_vector_repo, mock_event_bus)
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Test",
        content="Content",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_metadata_repo.get_by_id.return_value = mock_memory

    await use_case.execute(memory_id, "corr-123")

    mock_metadata_repo.soft_delete.assert_called_once_with(memory_id)
    mock_vector_repo.delete.assert_called_once_with(memory_id)
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert event.event_type == EventType.DELETED


@pytest.mark.asyncio
async def test_delete_memory_use_case_vector_failure(
    mock_metadata_repo, mock_vector_repo, mock_event_bus
):
    use_case = DeleteMemoryUseCase(mock_metadata_repo, mock_vector_repo, mock_event_bus)
    memory_id = uuid.uuid4()

    mock_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Test",
        content="Content",
        memory_category=MemoryCategory.OBSERVATION,
        source=MemorySource.CONVERSATION,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_metadata_repo.get_by_id.return_value = mock_memory
    mock_vector_repo.delete.side_effect = Exception("Vector DB Error")

    await use_case.execute(memory_id, "corr-123")

    mock_metadata_repo.soft_delete.assert_called_once_with(memory_id)
    mock_metadata_repo.update_embedding_status.assert_called_once_with(memory_id, EmbeddingStatus.FAILED)
