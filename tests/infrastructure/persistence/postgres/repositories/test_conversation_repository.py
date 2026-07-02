import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.persistence.postgres.repositories.conversation_repository import (
    ConversationRepository,
)
from app.interfaces.http.schemas.conversation import (
    ConversationThread,
    ConversationThreadCreate,
    ConversationTurn,
    ConversationTurnCreate,
)
from app.shared.enums import ConversationRole, ConversationStatus
from app.shared.exceptions.errors import ConversationNotFoundError, RepositoryError


@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    return client


@pytest.fixture
def repository(mock_supabase_client):
    return ConversationRepository(mock_supabase_client)


@pytest.mark.asyncio
async def test_create_thread_success(repository, mock_supabase_client):
    twin_id = uuid.uuid4()
    thread_id = uuid.uuid4()

    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(thread_id),
                "twin_id": str(twin_id),
                "title": "Test Thread",
                "status": ConversationStatus.ACTIVE.value,
                "turn_count": 0,
                "metadata": {},
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().insert().execute = mock_execute

    data = ConversationThreadCreate(twin_id=twin_id, title="Test Thread")

    result = await repository.create_thread(data)
    assert isinstance(result, ConversationThread)
    assert result.status == ConversationStatus.ACTIVE
    assert str(result.id) == str(thread_id)
    assert str(result.twin_id) == str(twin_id)


@pytest.mark.asyncio
async def test_get_thread_success(repository, mock_supabase_client):
    thread_id = uuid.uuid4()
    twin_id = uuid.uuid4()

    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data={
            "id": str(thread_id),
            "twin_id": str(twin_id),
            "title": "Test Thread",
            "status": ConversationStatus.ACTIVE.value,
            "turn_count": 5,
            "metadata": {},
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )

    mock_supabase_client.table().select().eq().is_().single().execute = mock_execute

    result = await repository.get_thread(thread_id)
    assert isinstance(result, ConversationThread)
    assert str(result.id) == str(thread_id)
    assert result.turn_count == 5


@pytest.mark.asyncio
async def test_get_thread_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=None)

    mock_supabase_client.table().select().eq().is_().single().execute = mock_execute

    with pytest.raises(ConversationNotFoundError):
        await repository.get_thread(uuid.uuid4())


@pytest.mark.asyncio
async def test_add_turn_success(repository, mock_supabase_client):
    thread_id = uuid.uuid4()
    turn_id = uuid.uuid4()

    # Mock for count check
    count_execute = AsyncMock()
    count_execute.return_value = MagicMock(count=2)

    # Mock for insert turn
    insert_execute = AsyncMock()
    insert_execute.return_value = MagicMock(
        data=[
            {
                "id": str(turn_id),
                "thread_id": str(thread_id),
                "role": ConversationRole.USER.value,
                "content": "Hello",
                "turn_index": 2,
                "created_at": datetime.now(UTC).isoformat(),
            }
        ]
    )

    # Mock for update thread
    update_execute = AsyncMock()
    update_execute.return_value = MagicMock()

    # We have to patch the mock differently since there are multiple executes on different table chains
    # but the simplest way with our mock is just assign execute side_effect or use AsyncMock directly
    # where needed. Let's simplify and just set the return_value for the table mock itself.

    # Mocking the table method to return different mocks based on table name
    def table_side_effect(table_name):
        table_mock = MagicMock()
        if table_name == "conversation_turns":
            # the count execute is called first, then insert execute
            table_mock.select().eq().execute = count_execute
            table_mock.insert().execute = insert_execute
        elif table_name == "conversation_threads":
            table_mock.update().eq().execute = update_execute
        return table_mock

    mock_supabase_client.table.side_effect = table_side_effect

    data = ConversationTurnCreate(thread_id=thread_id, role=ConversationRole.USER, content="Hello")

    result = await repository.add_turn(data)
    assert isinstance(result, ConversationTurn)
    assert str(result.id) == str(turn_id)
    assert result.turn_index == 2


@pytest.mark.asyncio
async def test_create_thread_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().insert().execute = mock_execute
    with pytest.raises(RepositoryError) as exc_info:
        await repository.create_thread(ConversationThreadCreate(twin_id=uuid.uuid4(), title="fail"))
    assert "conversation.create_thread" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_get_thread_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq().is_().single().execute = mock_execute
    with pytest.raises(RepositoryError) as exc_info:
        await repository.get_thread(uuid.uuid4())
    assert "conversation.get_thread" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_add_turn_count_failure(repository, mock_supabase_client):
    thread_id = uuid.uuid4()
    turn_id = uuid.uuid4()

    count_execute = AsyncMock(side_effect=Exception("Count Error"))
    insert_execute = AsyncMock()
    insert_execute.return_value = MagicMock(
        data=[
            {
                "id": str(turn_id),
                "thread_id": str(thread_id),
                "role": ConversationRole.USER.value,
                "content": "Hello",
                "turn_index": 0,
                "created_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    update_execute = AsyncMock()

    def table_side_effect(table_name):
        table_mock = MagicMock()
        if table_name == "conversation_turns":
            table_mock.select().eq().execute = count_execute
            table_mock.insert().execute = insert_execute
        elif table_name == "conversation_threads":
            table_mock.update().eq().execute = update_execute
        return table_mock

    mock_supabase_client.table.side_effect = table_side_effect

    data = ConversationTurnCreate(thread_id=thread_id, role=ConversationRole.USER, content="Hello")
    result = await repository.add_turn(data)
    assert result.turn_index == 0


@pytest.mark.asyncio
async def test_add_turn_insert_failure(repository, mock_supabase_client):
    count_execute = AsyncMock()
    count_execute.return_value = MagicMock(count=1)
    insert_execute = AsyncMock(side_effect=Exception("Insert Error"))

    def table_side_effect(table_name):
        table_mock = MagicMock()
        if table_name == "conversation_turns":
            table_mock.select().eq().execute = count_execute
            table_mock.insert().execute = insert_execute
        return table_mock

    mock_supabase_client.table.side_effect = table_side_effect

    with pytest.raises(RepositoryError) as exc_info:
        await repository.add_turn(
            ConversationTurnCreate(
                thread_id=uuid.uuid4(), role=ConversationRole.USER, content="Hello"
            )
        )
    assert "conversation.add_turn" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_get_recent_turns_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(uuid.uuid4()),
                "thread_id": str(uuid.uuid4()),
                "role": ConversationRole.USER.value,
                "content": "Hi",
                "turn_index": 0,
                "created_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().select().eq().order().limit().execute = mock_execute

    result = await repository.get_recent_turns(uuid.uuid4())
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_recent_turns_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq().order().limit().execute = mock_execute

    with pytest.raises(RepositoryError) as exc_info:
        await repository.get_recent_turns(uuid.uuid4())
    assert "conversation.get_recent_turns" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_list_threads_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(uuid.uuid4()),
                "twin_id": str(uuid.uuid4()),
                "title": "Thread",
                "status": ConversationStatus.ACTIVE.value,
                "turn_count": 1,
                "metadata": {},
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ],
        count=1,
    )

    mock_query = MagicMock()
    mock_query.execute = mock_execute
    mock_query.eq.return_value = mock_query

    mock_supabase_client.table().select().eq().is_().order().range.return_value = mock_query

    result = await repository.list_threads(uuid.uuid4(), status=ConversationStatus.ACTIVE)
    assert result.total_count == 1
    assert len(result.items) == 1


@pytest.mark.asyncio
async def test_list_threads_failure(repository, mock_supabase_client):
    mock_query = MagicMock()
    mock_query.execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq().is_().order().range.return_value = mock_query

    with pytest.raises(RepositoryError):
        await repository.list_threads(uuid.uuid4())


@pytest.mark.asyncio
async def test_archive_thread_success(repository, mock_supabase_client):
    thread_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(thread_id),
                "twin_id": str(uuid.uuid4()),
                "title": "Thread",
                "status": ConversationStatus.ARCHIVED.value,
                "turn_count": 1,
                "metadata": {},
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().update().eq().execute = mock_execute

    result = await repository.archive_thread(thread_id)
    assert result.status == ConversationStatus.ARCHIVED


@pytest.mark.asyncio
async def test_archive_thread_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=None)
    mock_supabase_client.table().update().eq().execute = mock_execute

    with pytest.raises(ConversationNotFoundError):
        await repository.archive_thread(uuid.uuid4())


@pytest.mark.asyncio
async def test_archive_thread_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().update().eq().execute = mock_execute

    with pytest.raises(RepositoryError):
        await repository.archive_thread(uuid.uuid4())


@pytest.mark.asyncio
async def test_health_check_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_supabase_client.table().select().limit().execute = mock_execute

    health = await repository.health_check()
    assert health["conversation_repository"] == "ok"


@pytest.mark.asyncio
async def test_health_check_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().limit().execute = mock_execute

    health = await repository.health_check()
    assert health["conversation_repository"] == "error"
