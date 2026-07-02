import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.persistence.postgres.repositories.goal_repository import GoalRepository
from app.intelligence.strategy.goals.goal import GoalCreate, GoalUpdate
from app.shared.enums import GoalStatus, GoalType
from app.shared.exceptions.errors import GoalNotFoundError, RepositoryError


@pytest.fixture
def mock_supabase_client():
    return MagicMock()


@pytest.fixture
def repository(mock_supabase_client):
    return GoalRepository(mock_supabase_client)


@pytest.mark.asyncio
async def test_create_success(repository, mock_supabase_client):
    goal_id = uuid.uuid4()
    twin_id = uuid.uuid4()

    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(goal_id),
                "twin_id": str(twin_id),
                "title": "Test Goal",
                "description": "A description",
                "goal_type": GoalType.STRATEGIC.value,
                "priority": 5,
                "success_criteria": ["Do it well"],
                "status": GoalStatus.DRAFT.value,
                "target_date": datetime.now(UTC).isoformat(),
                "parent_goal_id": str(uuid.uuid4()),
                "metadata": {"key": "value"},
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().insert().execute = mock_execute

    data = GoalCreate(
        title="Test Goal",
        description="A description",
        goal_type=GoalType.STRATEGIC,
        priority=5,
        success_criteria=["Do it well"],
        target_date=datetime.now(UTC),
        parent_goal_id=uuid.uuid4(),
        metadata={"key": "value"},
    )
    result = await repository.create(twin_id, data)
    assert result.id == goal_id


@pytest.mark.asyncio
async def test_create_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().insert().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.create(
            uuid.uuid4(),
            GoalCreate(
                title="Test",
                goal_type=GoalType.STRATEGIC,
                priority=5,
                success_criteria=[],
            ),
        )


@pytest.mark.asyncio
async def test_get_by_id_success(repository, mock_supabase_client):
    goal_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(goal_id),
                "twin_id": str(uuid.uuid4()),
                "title": "Test Goal",
                "goal_type": GoalType.STRATEGIC.value,
                "priority": 5,
                "success_criteria": [],
                "status": GoalStatus.DRAFT.value,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().select().eq().execute = mock_execute

    result = await repository.get_by_id(goal_id)
    assert result.id == goal_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[])
    mock_supabase_client.table().select().eq().execute = mock_execute
    with pytest.raises(GoalNotFoundError):
        await repository.get_by_id(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_by_id_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.get_by_id(uuid.uuid4())


@pytest.mark.asyncio
async def test_list_by_twin_success(repository, mock_supabase_client):
    twin_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(uuid.uuid4()),
                "twin_id": str(twin_id),
                "title": "Test Goal",
                "goal_type": GoalType.STRATEGIC.value,
                "priority": 5,
                "success_criteria": [],
                "status": GoalStatus.ACTIVE.value,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ],
        count=1,
    )

    mock_query = MagicMock()
    mock_query.execute = mock_execute
    mock_query.eq.return_value = mock_query
    mock_query.is_.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.range.return_value = mock_query

    mock_supabase_client.table().select().eq.return_value = mock_query

    result = await repository.list_by_twin(
        twin_id,
        status=GoalStatus.ACTIVE,
        goal_type=GoalType.STRATEGIC,
        include_deleted=False,
    )
    assert result.total_count == 1
    assert len(result.items) == 1


@pytest.mark.asyncio
async def test_list_by_twin_failure(repository, mock_supabase_client):
    mock_query = MagicMock()
    mock_query.execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq.return_value = mock_query

    with pytest.raises(RepositoryError):
        await repository.list_by_twin(uuid.uuid4(), include_deleted=True)


@pytest.mark.asyncio
async def test_get_active_goals_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(uuid.uuid4()),
                "twin_id": str(uuid.uuid4()),
                "title": "Test Goal",
                "goal_type": GoalType.STRATEGIC.value,
                "priority": 5,
                "success_criteria": [],
                "status": GoalStatus.ACTIVE.value,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    )

    mock_query = MagicMock()
    mock_query.execute = mock_execute
    mock_query.eq.return_value = mock_query
    mock_query.in_.return_value = mock_query
    mock_query.is_.return_value = mock_query
    mock_query.order.return_value = mock_query

    mock_supabase_client.table().select().eq.return_value = mock_query

    result = await repository.get_active_goals(uuid.uuid4())
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_active_goals_failure(repository, mock_supabase_client):
    mock_query = MagicMock()
    mock_query.execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq.return_value = mock_query

    with pytest.raises(RepositoryError):
        await repository.get_active_goals(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_success(repository, mock_supabase_client):
    goal_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(goal_id),
                "twin_id": str(uuid.uuid4()),
                "title": "Updated",
                "goal_type": GoalType.STRATEGIC.value,
                "priority": 5,
                "success_criteria": [],
                "status": GoalStatus.ACTIVE.value,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().update().eq().execute = mock_execute

    result = await repository.update(
        goal_id, GoalUpdate(status=GoalStatus.ACTIVE, goal_type=GoalType.STRATEGIC)
    )
    assert result.status == GoalStatus.ACTIVE


@pytest.mark.asyncio
async def test_update_empty(repository, mock_supabase_client):
    goal_id = uuid.uuid4()
    mock_get = AsyncMock()
    mock_get.return_value = MagicMock(
        data=[
            {
                "id": str(goal_id),
                "twin_id": str(uuid.uuid4()),
                "title": "Test Goal",
                "goal_type": GoalType.STRATEGIC.value,
                "priority": 5,
                "success_criteria": [],
                "status": GoalStatus.DRAFT.value,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().select().eq().execute = mock_get

    result = await repository.update(goal_id, GoalUpdate())
    assert str(result.id) == str(goal_id)


@pytest.mark.asyncio
async def test_update_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[])
    mock_supabase_client.table().update().eq().execute = mock_execute
    with pytest.raises(GoalNotFoundError):
        await repository.update(uuid.uuid4(), GoalUpdate(title="foo"))


@pytest.mark.asyncio
async def test_update_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().update().eq().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.update(uuid.uuid4(), GoalUpdate(title="foo"))


@pytest.mark.asyncio
async def test_soft_delete_success(repository, mock_supabase_client):
    goal_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[{"id": str(goal_id)}])
    mock_supabase_client.table().update().eq().is_().execute = mock_execute

    await repository.soft_delete(goal_id)


@pytest.mark.asyncio
async def test_soft_delete_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[])
    mock_supabase_client.table().update().eq().is_().execute = mock_execute
    with pytest.raises(GoalNotFoundError):
        await repository.soft_delete(uuid.uuid4())


@pytest.mark.asyncio
async def test_soft_delete_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().update().eq().is_().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.soft_delete(uuid.uuid4())


@pytest.mark.asyncio
async def test_link_intent_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    intent_id = uuid.uuid4()
    goal_id = uuid.uuid4()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "id": str(uuid.uuid4()),
                "intent_id": str(intent_id),
                "goal_id": str(goal_id),
                "created_at": datetime.now(UTC).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().insert().execute = mock_execute

    result = await repository.link_intent(intent_id, goal_id)
    assert str(result.intent_id) == str(intent_id)
    assert str(result.goal_id) == str(goal_id)


@pytest.mark.asyncio
async def test_link_intent_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().insert().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.link_intent(uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_health_check_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_supabase_client.table().select().limit().execute = mock_execute

    health = await repository.health_check()
    assert health["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().limit().execute = mock_execute

    health = await repository.health_check()
    assert health["status"] == "unhealthy"
    assert "DB Error" in health["detail"]
