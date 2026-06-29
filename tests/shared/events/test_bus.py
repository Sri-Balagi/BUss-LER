import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import BackgroundTasks

from app.shared.events.bus import BackgroundTasksEventBus
from app.shared.events.models import DomainEvent
import uuid


class TestEvent(DomainEvent):
    """Dummy event for testing."""

    test_data: str


@pytest.fixture
def background_tasks():
    return MagicMock(spec=BackgroundTasks)


@pytest.fixture
def event_bus(background_tasks):
    return BackgroundTasksEventBus(background_tasks=background_tasks)


def test_subscribe_and_publish(event_bus, background_tasks):
    mock_handler = AsyncMock()
    event_bus.subscribe(TestEvent, mock_handler)

    event = TestEvent(
        event_id=uuid.uuid4(),
        correlation_id="corr-1",
        source="test",
        version="1.0",
        test_data="hello",
    )

    event_bus.publish(event)

    # Verify that the background task was added
    background_tasks.add_task.assert_called_once_with(mock_handler, event)


def test_subscribe_multiple_handlers(event_bus, background_tasks):
    handler1 = AsyncMock()
    handler2 = AsyncMock()

    event_bus.subscribe(TestEvent, handler1)
    event_bus.subscribe(TestEvent, handler2)

    event = TestEvent(
        event_id=uuid.uuid4(),
        correlation_id="corr-1",
        source="test",
        version="1.0",
        test_data="hello",
    )

    event_bus.publish(event)

    assert background_tasks.add_task.call_count == 2
    # Check that both handlers were added
    calls = background_tasks.add_task.call_args_list
    handlers_called = [call[0][0] for call in calls]
    assert handler1 in handlers_called
    assert handler2 in handlers_called


def test_unsubscribe(event_bus, background_tasks):
    handler = AsyncMock()
    event_bus.subscribe(TestEvent, handler)
    event_bus.unsubscribe(TestEvent, handler)

    event = TestEvent(
        event_id=uuid.uuid4(),
        correlation_id="corr-1",
        source="test",
        version="1.0",
        test_data="hello",
    )
    event_bus.publish(event)

    background_tasks.add_task.assert_not_called()


def test_publish_without_background_tasks():
    # Should not crash if background_tasks is None
    bus = BackgroundTasksEventBus()
    handler = AsyncMock()
    bus.subscribe(TestEvent, handler)

    event = TestEvent(
        event_id=uuid.uuid4(),
        correlation_id="corr-1",
        source="test",
        version="1.0",
        test_data="hello",
    )
    bus.publish(event)
    handler.assert_not_called()


def test_set_background_tasks(background_tasks):
    bus = BackgroundTasksEventBus()
    bus.set_background_tasks(background_tasks)

    handler = AsyncMock()
    bus.subscribe(TestEvent, handler)

    event = TestEvent(
        event_id=uuid.uuid4(),
        correlation_id="corr-1",
        source="test",
        version="1.0",
        test_data="hello",
    )
    bus.publish(event)
    background_tasks.add_task.assert_called_once_with(handler, event)


def test_publish_unregistered_event(event_bus, background_tasks):
    event = TestEvent(
        event_id=uuid.uuid4(),
        correlation_id="corr-1",
        source="test",
        version="1.0",
        test_data="hello",
    )
    event_bus.publish(event)
    background_tasks.add_task.assert_not_called()


def test_unsubscribe_unregistered_handler(event_bus):
    handler = AsyncMock()
    # Unsubscribing a handler that wasn't subscribed shouldn't crash
    event_bus.unsubscribe(TestEvent, handler)
