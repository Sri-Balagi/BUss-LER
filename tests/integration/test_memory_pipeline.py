import asyncio
import uuid
from unittest.mock import AsyncMock

import pytest

from app.core.context import OperationContext
from app.models.ai import EmbeddingResponse
from app.models.enums import EmbeddingStatus, MemoryCategory, MemorySource
from app.models.events import MemoryLifecycleEvent, EventType
from app.models.memory import Memory
from app.services.memory_service import MemoryService
from app.workers.memory_worker import MemoryProcessingWorker


@pytest.mark.asyncio
async def test_memory_pipeline_integration():
    """
    Test the full memory processing pipeline integration:
    Worker -> MemoryService -> AIKernel -> Metadata/Vector Repositories.
    """
    # 1. Setup Mocks
    mock_metadata_repo = AsyncMock()
    mock_vector_repo = AsyncMock()
    mock_ai_kernel = AsyncMock()
    
    # 2. Setup Real Service and Worker
    memory_service = MemoryService(
        metadata_repo=mock_metadata_repo,
        vector_repo=mock_vector_repo,
        ai_kernel=mock_ai_kernel,
        event_bus=None  # We will trigger worker directly for this test
    )
    
    worker = MemoryProcessingWorker(
        memory_service=memory_service,
        ai_kernel=mock_ai_kernel,
        metadata_repo=mock_metadata_repo,
        vector_repo=mock_vector_repo
    )
    
    # 3. Create test data
    twin_id = uuid.uuid4()
    memory_id = uuid.uuid4()
    correlation_id = str(uuid.uuid4())
    
    mock_memory = Memory(
        id=memory_id,
        twin_id=twin_id,
        title="Integration Test",
        content="This is the original content that needs summarizing and embedding.",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.PENDING,
        summary=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )
    
    # Configure mock returns
    mock_metadata_repo.get_by_id.return_value = mock_memory
    
    # update_embedding_status and update_summary need to return the updated memory
    # We can just return the mock_memory modified or as-is since the worker just uses it for assertions or logs
    mock_metadata_repo.update_embedding_status.return_value = mock_memory
    mock_metadata_repo.update_summary.return_value = mock_memory
    
    # AI Kernel mocks
    mock_ai_kernel.summarize.return_value = "This is a summary."
    from app.models.ai import AIResponseMetadata
    mock_ai_kernel.embed.return_value = EmbeddingResponse(
        vector=[0.1, 0.2, 0.3], 
        dimensions=3, 
        metadata=AIResponseMetadata(provider="mock", model="mock", latency_ms=10)
    )
    
    # 4. Create and dispatch event
    event = MemoryLifecycleEvent(
        memory_id=memory_id,
        twin_id=twin_id,
        event_type=EventType.CREATED,
        correlation_id=correlation_id,
        source="integration_test",
        version="1.0"
    )
    
    # 5. Execute Pipeline
    await worker.handle_event(event)
    
    # 6. Assertions
    # Did it fetch the memory?
    mock_metadata_repo.get_by_id.assert_called_with(memory_id)
    
    # Did it mark as processing?
    mock_metadata_repo.update_embedding_status.assert_any_call(memory_id, EmbeddingStatus.PROCESSING)
    
    # Did it summarize?
    mock_ai_kernel.summarize.assert_called_once_with(mock_memory.content)
    mock_metadata_repo.update_summary.assert_called_once_with(memory_id, "This is a summary.")
    
    # Did it embed the summary?
    mock_ai_kernel.embed.assert_called_once()
    # Pydantic models might be compared differently, but we can check the call args
    embed_call_args = mock_ai_kernel.embed.call_args[0][0]
    assert embed_call_args.text == "This is a summary."
    
    # Did it store the vector?
    mock_vector_repo.upsert.assert_called_once()
    upsert_arg = mock_vector_repo.upsert.call_args[0][0]
    assert upsert_arg.id == memory_id
    assert upsert_arg.vector == [0.1, 0.2, 0.3]
    assert upsert_arg.payload.twin_id == twin_id
    
    # Did it mark as completed?
    mock_metadata_repo.update_embedding_status.assert_any_call(memory_id, EmbeddingStatus.COMPLETED)

@pytest.mark.asyncio
async def test_memory_pipeline_skip_completed():
    """Test that the worker gracefully skips memories already processed."""
    mock_metadata_repo = AsyncMock()
    memory_service = MemoryService(
        metadata_repo=mock_metadata_repo,
        vector_repo=AsyncMock(),
        ai_kernel=AsyncMock()
    )
    worker = MemoryProcessingWorker(
        memory_service=memory_service,
        ai_kernel=AsyncMock(),
        metadata_repo=mock_metadata_repo,
        vector_repo=AsyncMock()
    )
    
    memory_id = uuid.uuid4()
    mock_memory = Memory(
        id=memory_id,
        twin_id=uuid.uuid4(),
        title="Completed",
        content="Already done.",
        source=MemorySource.USER_INPUT,
        memory_category=MemoryCategory.EVENT,
        metadata={},
        importance=0.5,
        embedding_status=EmbeddingStatus.COMPLETED,
        summary="Done",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )
    mock_metadata_repo.get_by_id.return_value = mock_memory
    
    event = MemoryLifecycleEvent(
        memory_id=memory_id,
        twin_id=mock_memory.twin_id,
        event_type=EventType.CREATED,
        correlation_id="123",
        source="integration_test",
        version="1.0"
    )
    
    await worker.handle_event(event)
    
    # It should fetch, then see it's completed and stop
    mock_metadata_repo.get_by_id.assert_called_once()
    mock_metadata_repo.update_embedding_status.assert_not_called()
