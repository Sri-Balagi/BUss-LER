import pytest
import uuid
from unittest.mock import Mock, AsyncMock

from fastapi import BackgroundTasks
from app.services.events.dispatcher import BackgroundTasksEventDispatcher
from app.models.events import MemoryLifecycleEvent, EventType


@pytest.fixture
def mock_background_tasks():
    return Mock(spec=BackgroundTasks)


@pytest.fixture
def dispatcher(mock_background_tasks):
    return BackgroundTasksEventDispatcher(mock_background_tasks)


def test_subscribe_and_dispatch(dispatcher, mock_background_tasks):
    handler = AsyncMock()
    event = MemoryLifecycleEvent(
        memory_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        event_type=EventType.CREATED,
        correlation_id="corr-123",
    )

    # Subscribe
    dispatcher.subscribe(MemoryLifecycleEvent, handler)

    # Dispatch
    dispatcher.dispatch(event)

    # Assert task was added
    mock_background_tasks.add_task.assert_called_once_with(handler, event)


def test_dispatch_without_tasks(dispatcher):
    dispatcher.set_background_tasks(None)
    handler = AsyncMock()

    event = MemoryLifecycleEvent(
        memory_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        event_type=EventType.CREATED,
        correlation_id="corr-123",
    )

    dispatcher.subscribe(MemoryLifecycleEvent, handler)

    # Should safely drop without failing
    dispatcher.dispatch(event)


def test_dispatch_unregistered_event(dispatcher, mock_background_tasks):
    event = MemoryLifecycleEvent(
        memory_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        event_type=EventType.CREATED,
        correlation_id="corr-123",
    )

    # Dispatch without subscription
    dispatcher.dispatch(event)

    # Assert no task was added
    mock_background_tasks.add_task.assert_not_called()
