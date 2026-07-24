import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.goal.goal_service import GoalService
from app.core.context import OperationContext
from app.intelligence.strategy.goals.goal import Goal
from app.runtime.core.commands import CreateGoalCommand, DeleteGoalCommand, UpdateGoalCommand
from app.shared.enums import GoalStatus


@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def mock_event_bus():
    return MagicMock()

@pytest.fixture
def service(mock_repository, mock_event_bus):
    return GoalService(mock_repository, mock_event_bus)

@pytest.fixture
def ctx():
    return OperationContext()

@pytest.mark.asyncio
async def test_create_goal(service, mock_repository, ctx):
    twin_id = uuid.uuid4()
    goal = Goal(
        id=uuid.uuid4(),
        twin_id=twin_id,
        title="test",
        status=GoalStatus.DRAFT,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    mock_repository.create.return_value = goal
    cmd = CreateGoalCommand(twin_id=twin_id, title="test", description="test")

    result = await service.create_goal(ctx, cmd)

    assert result.goal == goal
    mock_repository.create.assert_called_once()

@pytest.mark.asyncio
async def test_get_goal(service, mock_repository, ctx):
    goal_id = uuid.uuid4()
    goal = Goal(
        id=goal_id,
        twin_id=uuid.uuid4(),
        title="test",
        status=GoalStatus.DRAFT,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    mock_repository.get_by_id.return_value = goal

    result = await service.get_goal(ctx, goal_id)

    assert result == goal
    mock_repository.get_by_id.assert_called_once_with(goal_id)

@pytest.mark.asyncio
async def test_update_goal(service, mock_repository, ctx):
    goal_id = uuid.uuid4()
    goal = Goal(
        id=goal_id,
        twin_id=uuid.uuid4(),
        title="test",
        status=GoalStatus.DRAFT,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    mock_repository.get_by_id.return_value = goal
    mock_repository.update.return_value = goal

    cmd = UpdateGoalCommand(goal_id=goal_id, title="new title")
    result = await service.update_goal(ctx, cmd)

    assert result == goal
    mock_repository.update.assert_called_once()

@pytest.mark.asyncio
async def test_delete_goal(service, mock_repository, ctx):
    goal_id = uuid.uuid4()
    goal = Goal(
        id=goal_id,
        twin_id=uuid.uuid4(),
        title="test",
        status=GoalStatus.DRAFT,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    mock_repository.get_by_id.return_value = goal

    cmd = DeleteGoalCommand(goal_id=goal_id)
    await service.delete_goal(ctx, cmd)

    mock_repository.soft_delete.assert_called_once_with(goal_id)

