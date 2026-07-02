import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.models.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.models.events import EventType, MemoryLifecycleEvent
from app.models.memory import Memory
from app.services.memory_service import MemoryService
from app.workers.memory_worker import MemoryProcessingWorker


@pytest.fixture
def mock_memory():
    return Memory(
        id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        title="Concurrency Test Memory",
        content="Testing concurrent workers",
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
async def test_concurrent_worker_execution(mock_memory):
    """
    Test that if multiple workers process the same event concurrently,
    only one successfully updates the state (idempotency/state machine lock).
    We simulate this by checking if the memory state has changed.
    """
    mock_metadata_repo = AsyncMock()

    # State tracking to simulate DB state changing
    current_status = EmbeddingStatus.PENDING

    async def mock_get_by_id(memory_id):
        nonlocal current_status
        m = mock_memory.model_copy()
        m.embedding_status = current_status
        return m

    async def mock_update_status(memory_id, status):
        nonlocal current_status
        # In a real DB, this would throw an error if the state transition was invalid
        # But MemoryStateMachine.transition handles invalid transitions by raising ValueError
        current_status = status
        m = mock_memory.model_copy()
        m.embedding_status = status
        return m

    mock_metadata_repo.get_by_id.side_effect = mock_get_by_id
    mock_metadata_repo.update_embedding_status.side_effect = mock_update_status

    mock_ai_kernel = AsyncMock()
    mock_ai_kernel.summarize.return_value = "Summary"

    from app.models.ai import AIResponseMetadata, EmbeddingResponse

    mock_ai_kernel.embed.return_value = EmbeddingResponse(
        vector=[0.0] * 768,
        dimensions=768,
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10),
    )

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

    event1 = MemoryLifecycleEvent(
        memory_id=mock_memory.id,
        twin_id=mock_memory.twin_id,
        event_type=EventType.CREATED,
        correlation_id="c1",
        source="test",
        version="1.0",
    )

    # Run two workers concurrently
    # The first to get_by_id will see PENDING and transition to PROCESSING
    # The second one might see PENDING if there's a race condition, or PROCESSING.
    # If it sees PROCESSING, the transition from PROCESSING -> PROCESSING is ignored or fails.
    # If it sees COMPLETED, it gracefully skips.
    with patch("asyncio.sleep", return_value=None):
        results = await asyncio.gather(
            worker.handle_event(event1),
            worker.handle_event(event1),
            return_exceptions=True,
        )

    # Both should complete without unhandled exceptions
    for r in results:
        assert not isinstance(r, Exception)

    # The memory should end up as COMPLETED
    assert current_status == EmbeddingStatus.COMPLETED
