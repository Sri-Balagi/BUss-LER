import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch, ANY

from app.workers.memory_worker import MemoryProcessingWorker
from app.models.events import MemoryLifecycleEvent, EventType
from app.models.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.models.ai import EmbeddingResponse, AIResponseMetadata
from app.services.memory_service import AbstractMemoryService
from app.services.ai.kernel import AbstractAIKernel
from app.repositories.memory_repository import AbstractMemoryRepository
from app.repositories.vector_repository import AbstractVectorRepository
from app.core.context import OperationContext

@pytest.fixture
def memory_service():
    return AsyncMock(spec=AbstractMemoryService)

@pytest.fixture
def ai_kernel():
    return AsyncMock(spec=AbstractAIKernel)

@pytest.fixture
def metadata_repo():
    return AsyncMock(spec=AbstractMemoryRepository)

@pytest.fixture
def vector_repo():
    return AsyncMock(spec=AbstractVectorRepository)

@pytest.fixture
def worker(memory_service, ai_kernel, metadata_repo, vector_repo):
    return MemoryProcessingWorker(memory_service, ai_kernel, metadata_repo, vector_repo)

@pytest.mark.asyncio
async def test_worker_skips_unhandled_events(worker):
    event = MemoryLifecycleEvent(
        memory_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        event_type=EventType.COMPLETED,
        correlation_id="corr",
        source="test",
        version="1.0"
    )
    await worker.handle_event(event)
    worker._memory_service.get_memory.assert_not_called()

@pytest.mark.asyncio
async def test_worker_pipeline_success_no_summary(worker, memory_service, ai_kernel, vector_repo):
    memory_id = uuid.uuid4()
    twin_id = uuid.uuid4()
    
    event = MemoryLifecycleEvent(
        memory_id=memory_id,
        twin_id=twin_id,
        event_type=EventType.CREATED,
        correlation_id="corr",
        source="test",
        version="1.0"
    )

    # Mock memory retrieval
    mock_memory = Mock()
    mock_memory.id = memory_id
    mock_memory.twin_id = twin_id
    mock_memory.embedding_status = EmbeddingStatus.PENDING
    mock_memory.summary = None
    mock_memory.content = "Some memory content"
    mock_memory.memory_category = MemoryCategory.OBSERVATION
    mock_memory.source = MemorySource.USER_INPUT
    mock_memory.importance = 0.5
    mock_memory.created_at = datetime.utcnow()
    mock_memory.updated_at = datetime.utcnow()
    mock_memory.metadata = {}
    memory_service.get_memory.return_value = mock_memory

    # Mock AI Kernel
    ai_kernel.summarize.return_value = "Generated summary"
    ai_kernel.embed.return_value = EmbeddingResponse(
        vector=[0.1, 0.2, 0.3],
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10)
    )

    await worker.handle_event(event)

    # Assert state transitions
    memory_service.update_embedding_status.assert_any_call(ANY, memory_id, EmbeddingStatus.PROCESSING)
    memory_service.update_embedding_status.assert_any_call(ANY, memory_id, EmbeddingStatus.COMPLETED)
    
    # Assert summarization
    ai_kernel.summarize.assert_called_once_with("Some memory content")
    memory_service.update_summary.assert_called_once_with(ANY, memory_id, "Generated summary")

    # Assert embedding storage
    vector_repo.upsert.assert_called_once()
    point = vector_repo.upsert.call_args[0][0]
    assert point.id == memory_id
    assert point.vector == [0.1, 0.2, 0.3]
    assert point.payload.memory_category == MemoryCategory.OBSERVATION

@pytest.mark.asyncio
async def test_worker_idempotency_skip(worker, memory_service):
    memory_id = uuid.uuid4()
    event = MemoryLifecycleEvent(
        memory_id=memory_id,
        twin_id=uuid.uuid4(),
        event_type=EventType.CREATED,
        correlation_id="corr",
        source="test",
        version="1.0"
    )

    mock_memory = Mock()
    mock_memory.embedding_status = EmbeddingStatus.COMPLETED
    memory_service.get_memory.return_value = mock_memory

    await worker.handle_event(event)

    # Should not process further
    memory_service.update_embedding_status.assert_not_called()

@pytest.mark.asyncio
async def test_worker_retries_and_fails(worker, memory_service, ai_kernel):
    memory_id = uuid.uuid4()
    event = MemoryLifecycleEvent(
        memory_id=memory_id,
        twin_id=uuid.uuid4(),
        event_type=EventType.CREATED,
        correlation_id="corr",
        source="test",
        version="1.0"
    )

    mock_memory = Mock()
    mock_memory.embedding_status = EmbeddingStatus.PENDING
    memory_service.get_memory.return_value = mock_memory

    # Make summarize always fail
    ai_kernel.summarize.side_effect = Exception("AI Error")

    with patch.object(worker, '_process_memory_pipeline', side_effect=Exception("Hard fail")):
        await worker.handle_event(event)
        
    memory_service.update_embedding_status.assert_called_once_with(ANY, memory_id, EmbeddingStatus.FAILED)
