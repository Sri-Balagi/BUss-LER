import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.conversation.conversation_service import ConversationService
from app.core.context import OperationContext
from app.interfaces.http.schemas.conversation import (
    ConversationThread,
    ConversationTurn,
)
from app.shared.enums import ConversationRole, ConversationStatus


@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def mock_event_bus():
    return MagicMock()

@pytest.fixture
def service(mock_repository, mock_event_bus):
    return ConversationService(mock_repository, mock_event_bus)

@pytest.fixture
def ctx():
    return OperationContext()

@pytest.mark.asyncio
async def test_create_thread(service, mock_repository, ctx):
    twin_id = uuid.uuid4()
    thread = ConversationThread(
        id=uuid.uuid4(),
        twin_id=twin_id,
        title="test",
        status=ConversationStatus.ACTIVE,
        metadata={},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    mock_repository.create_thread.return_value = thread

    result = await service.create_thread(ctx, twin_id, title="test", metadata={})

    assert result == thread
    mock_repository.create_thread.assert_called_once()
    create_cmd = mock_repository.create_thread.call_args[0][0]
    assert create_cmd.twin_id == twin_id
    assert create_cmd.title == "test"

@pytest.mark.asyncio
async def test_get_thread(service, mock_repository, ctx):
    thread_id = uuid.uuid4()
    thread = ConversationThread(
        id=thread_id,
        twin_id=uuid.uuid4(),
        status=ConversationStatus.ACTIVE,
        metadata={},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    mock_repository.get_thread.return_value = thread

    result = await service.get_thread(ctx, thread_id)

    assert result == thread
    mock_repository.get_thread.assert_called_once_with(thread_id)

@pytest.mark.asyncio
async def test_add_turn(service, mock_repository, mock_event_bus, ctx):
    thread_id = uuid.uuid4()
    thread = ConversationThread(
        id=thread_id,
        twin_id=uuid.uuid4(),
        status=ConversationStatus.ACTIVE,
        metadata={},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    mock_repository.get_thread.return_value = thread

    turn = ConversationTurn(
        id=uuid.uuid4(),
        thread_id=thread_id,
        role=ConversationRole.USER,
        turn_index=0,
        content="test content",
        created_at=datetime.now(UTC)
    )
    mock_repository.add_turn.return_value = turn

    result = await service.add_turn(ctx, thread_id, ConversationRole.USER, "test content")

    assert result == turn
    mock_repository.get_thread.assert_called_once_with(thread_id)
    mock_repository.add_turn.assert_called_once()
    add_cmd = mock_repository.add_turn.call_args[0][0]
    assert add_cmd.thread_id == thread_id
    assert add_cmd.role == ConversationRole.USER
    assert add_cmd.content == "test content"

