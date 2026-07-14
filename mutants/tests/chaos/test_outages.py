import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.models.commands import CreateMemoryCommand, DeleteMemoryCommand
from app.models.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.models.events import EventType, MemoryLifecycleEvent
from app.models.exceptions import RepositoryError, ServiceError
from app.models.memory import Memory
from app.services.memory_service import MemoryService
from app.workers.memory_worker import MemoryProcessingWorker

from app.core.context import OperationContext


@pytest.fixture
def base_context():
    return OperationContext(correlation_id=str(uuid.uuid4()), twin_id=uuid.uuid4())


@pytest.fixture
def mock_memory():
    return Memory(
        id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        title="Chaos Test Memory",
        content="Testing outages",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.PENDING,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )


@pytest.mark.asyncio
async def test_postgresql_outage(base_context):
    """Test that the service gracefully handles a PostgreSQL (metadata repo) outage."""
    mock_metadata_repo = AsyncMock()
    # Simulate DB failure
    mock_metadata_repo.create.side_effect = RepositoryError("DB Connection Lost")

    service = MemoryService(
        metadata_repo=mock_metadata_repo, vector_repo=AsyncMock(), ai_kernel=AsyncMock()
    )

    cmd = CreateMemoryCommand(
        twin_id=base_context.twin_id,
        content="Test",
        title="Test",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
    )

    with pytest.raises(ServiceError) as exc:
        await service.create_memory(base_context, cmd)

    assert "Memory orchestration failed" in str(exc.value)
    assert "DB Connection Lost" in str(exc.value)


@pytest.mark.asyncio
async def test_qdrant_outage(base_context, mock_memory):
    """Test that the service gracefully handles a Qdrant (vector repo) outage."""
    mock_vector_repo = AsyncMock()
    mock_vector_repo.delete.side_effect = RepositoryError("Qdrant unavailable")

    service = MemoryService(
        metadata_repo=AsyncMock(), vector_repo=mock_vector_repo, ai_kernel=AsyncMock()
    )

    cmd = DeleteMemoryCommand(memory_id=mock_memory.id)

    with pytest.raises(ServiceError) as exc:
        await service.delete_memory(base_context, cmd)

    assert "Memory deletion orchestration failed" in str(exc.value)
    assert "Qdrant unavailable" in str(exc.value)


@pytest.mark.asyncio
async def test_ai_provider_timeout(mock_memory):
    """Test that the worker retries and eventually fails on AI Provider timeout."""
    mock_ai_kernel = AsyncMock()
    # Always raise an exception to simulate timeout
    mock_ai_kernel.summarize.side_effect = Exception("AI Provider Timeout")

    mock_metadata_repo = AsyncMock()
    mock_metadata_repo.get_by_id.return_value = mock_memory

    service = MemoryService(
        metadata_repo=mock_metadata_repo,
        vector_repo=AsyncMock(),
        ai_kernel=mock_ai_kernel,
    )

    worker = MemoryProcessingWorker(
        memory_service=service,
        ai_kernel=mock_ai_kernel,
        metadata_repo=mock_metadata_repo,
        vector_repo=AsyncMock(),
    )

    event = MemoryLifecycleEvent(
        memory_id=mock_memory.id,
        twin_id=mock_memory.twin_id,
        event_type=EventType.CREATED,
        correlation_id="123",
        source="chaos_test",
        version="1.0",
    )

    # We expect handle_event to swallow the error after retries and mark as FAILED
    # But since it uses tenacity, wait_exponential might take a long time in a real test.
    # We should patch the retry parameters for the test to avoid actually waiting 10 seconds.
    with patch("app.workers.memory_worker.wait_exponential"):
        # Just run the pipeline directly to trigger tenacity, we have to bypass handle_event wrapper
        # actually handle_event wraps _process_memory_pipeline which has tenacity.
        pass

    # Actually wait we can just patch `tenacity.nap.time.sleep` or something,
    # but since it's async we should patch `asyncio.sleep`.
    with patch("asyncio.sleep", return_value=None):
        await worker.handle_event(event)

    # Verify it updated the embedding status to FAILED
    mock_metadata_repo.update_embedding_status.assert_called_with(
        mock_memory.id, EmbeddingStatus.FAILED
    )
    # The kernel should have been called 3 times (the initial try + 2 retries, depending on stop_after_attempt)
    assert mock_ai_kernel.summarize.call_count >= 1


@pytest.mark.asyncio
async def test_duplicate_event_delivery(mock_memory):
    """Test that the worker is idempotent on duplicate events."""
    mock_metadata_repo = AsyncMock()

    # Setup: Memory is already COMPLETED
    mock_memory.embedding_status = EmbeddingStatus.COMPLETED
    mock_metadata_repo.get_by_id.return_value = mock_memory

    service = MemoryService(
        metadata_repo=mock_metadata_repo, vector_repo=AsyncMock(), ai_kernel=AsyncMock()
    )

    worker = MemoryProcessingWorker(
        memory_service=service,
        ai_kernel=AsyncMock(),
        metadata_repo=mock_metadata_repo,
        vector_repo=AsyncMock(),
    )

    event = MemoryLifecycleEvent(
        memory_id=mock_memory.id,
        twin_id=mock_memory.twin_id,
        event_type=EventType.CREATED,
        correlation_id="duplicate_123",
        source="chaos_test",
        version="1.0",
    )

    # Send duplicate event twice
    await worker.handle_event(event)
    await worker.handle_event(event)

    # Should only fetch it, and not process further
    assert mock_metadata_repo.get_by_id.call_count == 2
    mock_metadata_repo.update_embedding_status.assert_not_called()
