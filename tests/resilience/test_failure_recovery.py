import pytest
import uuid
from unittest.mock import AsyncMock

from app.models.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.models.events import MemoryLifecycleEvent, EventType
from app.models.memory import Memory
from app.services.memory_service import MemoryService
from app.workers.memory_worker import MemoryProcessingWorker


@pytest.fixture
def mock_memory():
    return Memory(
        id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        title="Recovery Test Memory",
        content="Testing recovery from failure",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.FAILED,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )


@pytest.mark.asyncio
async def test_worker_recovers_failed_memory(mock_memory):
    """
    Test that a worker can re-process a FAILED memory if a new CREATED event is received,
    acting as a recovery mechanism.
    """
    mock_metadata_repo = AsyncMock()
    mock_metadata_repo.get_by_id.return_value = mock_memory
    
    mock_ai_kernel = AsyncMock()
    mock_ai_kernel.summarize.return_value = "Recovered Summary"
    
    from app.models.ai import EmbeddingResponse, AIResponseMetadata
    mock_ai_kernel.embed.return_value = EmbeddingResponse(
        vector=[0.1] * 768, 
        dimensions=768,
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10)
    )
    
    service = MemoryService(
        metadata_repo=mock_metadata_repo,
        vector_repo=AsyncMock(),
        ai_kernel=mock_ai_kernel
    )
    
    worker = MemoryProcessingWorker(
        memory_service=service,
        ai_kernel=mock_ai_kernel,
        metadata_repo=mock_metadata_repo,
        vector_repo=AsyncMock()
    )
    
    # Event representing a retry/recovery manual trigger
    event = MemoryLifecycleEvent(
        memory_id=mock_memory.id,
        twin_id=mock_memory.twin_id,
        event_type=EventType.CREATED,
        correlation_id="recovery_123",
        source="recovery",
        version="1.0"
    )
    
    # To recover, the status must first be explicitly transitioned to PENDING
    # as FAILED -> PROCESSING is invalid.
    mock_memory.embedding_status = EmbeddingStatus.PENDING
    
    await worker.handle_event(event)
    
    # Should transition from PENDING -> PROCESSING
    mock_metadata_repo.update_embedding_status.assert_any_call(mock_memory.id, EmbeddingStatus.PROCESSING)
    # Then to COMPLETED
    mock_metadata_repo.update_embedding_status.assert_any_call(mock_memory.id, EmbeddingStatus.COMPLETED)
