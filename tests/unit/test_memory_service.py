import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.memory.service import MemoryEngineService
from app.domain.memory.events import (
    MemoryCreated,
    MemoryRemoved,
    MemoryRetrieved,
    MemoryUpdated,
)
from app.domain.memory.models import MemoryRecord


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    return MagicMock()


@pytest.fixture
def service(mock_repository, mock_event_bus):
    return MemoryEngineService(mock_repository, mock_event_bus)


@pytest.mark.asyncio
async def test_save_memory(service, mock_repository, mock_event_bus):
    record = MemoryRecord(
        memory_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        memory_type="EPISODIC",
        source="SYSTEM",
        title="test title",
        content="test content"
    )
    await service.save_memory(record)

    mock_repository.save.assert_called_once_with(record)
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, MemoryCreated)
    assert event.memory_id == record.memory_id


@pytest.mark.asyncio
async def test_get_memory_found(service, mock_repository, mock_event_bus):
    record = MemoryRecord(
        memory_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        memory_type="EPISODIC",
        source="SYSTEM",
        title="test title",
        content="test content"
    )
    mock_repository.get.return_value = record

    result = await service.get_memory(record.memory_id, query_context="test")

    assert result == record
    mock_repository.get.assert_called_once_with(record.memory_id)
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, MemoryRetrieved)
    assert event.memory_id == record.memory_id


@pytest.mark.asyncio
async def test_get_memory_not_found(service, mock_repository, mock_event_bus):
    memory_id = uuid.uuid4()
    mock_repository.get.return_value = None

    result = await service.get_memory(memory_id)

    assert result is None
    mock_repository.get.assert_called_once_with(memory_id)
    mock_event_bus.publish.assert_not_called()


@pytest.mark.asyncio
async def test_update_memory(service, mock_repository, mock_event_bus):
    record = MemoryRecord(
        memory_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        memory_type="EPISODIC",
        source="SYSTEM",
        title="test title",
        content="test content"
    )
    await service.update_memory(record)

    mock_repository.save.assert_called_once_with(record)
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, MemoryUpdated)
    assert event.memory_id == record.memory_id


@pytest.mark.asyncio
async def test_remove_memory_found(service, mock_repository, mock_event_bus):
    memory_id = uuid.uuid4()
    record = MemoryRecord(
        memory_id=memory_id,
        twin_id=uuid.uuid4(),
        memory_type="EPISODIC",
        source="SYSTEM",
        title="test title",
        content="test content"
    )
    mock_repository.get.return_value = record

    await service.remove_memory(memory_id)

    mock_repository.get.assert_called_once_with(memory_id)
    mock_repository.remove.assert_called_once_with(memory_id)
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, MemoryRemoved)
    assert event.memory_id == memory_id


@pytest.mark.asyncio
async def test_remove_memory_not_found(service, mock_repository, mock_event_bus):
    memory_id = uuid.uuid4()
    mock_repository.get.return_value = None

    await service.remove_memory(memory_id)

    mock_repository.get.assert_called_once_with(memory_id)
    mock_repository.remove.assert_not_called()
    mock_event_bus.publish.assert_not_called()


@pytest.mark.asyncio
async def test_search(service, mock_repository):
    mock_repository.search.return_value = []

    result = await service.search("query", 5)

    assert result == []
    mock_repository.search.assert_called_once_with("query", 5)


@pytest.mark.asyncio
async def test_batch_save(service, mock_repository):
    records = []

    await service.batch_save(records)

    mock_repository.batch_save.assert_called_once_with(records)


@pytest.mark.asyncio
async def test_batch_remove(service, mock_repository):
    memory_ids = []

    await service.batch_remove(memory_ids)

    mock_repository.batch_remove.assert_called_once_with(memory_ids)
