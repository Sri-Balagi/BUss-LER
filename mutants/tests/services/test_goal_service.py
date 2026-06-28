import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from app.services.goal_service import GoalService
from app.models.commands import (
    CreateGoalCommand,
    UpdateGoalCommand,
    UpdateGoalProgressCommand,
    UpdateGoalStatusCommand,
    LinkIntentToGoalCommand,
    DeleteGoalCommand,
)
from app.models.enums import GoalStatus, GoalType
from app.models.goal import Goal, GoalUpdate, PaginatedGoals
from app.models.queries import GoalListQuery
from app.models.events import GoalCreatedEvent, GoalStatusChangedEvent
from app.core.context import OperationContext


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    return AsyncMock()


@pytest.fixture
def op_ctx():
    return OperationContext(correlation_id="test-corr-id")


@pytest.fixture
def service(mock_repo, mock_event_bus):
    return GoalService(repository=mock_repo, event_bus=mock_event_bus)


@pytest.fixture
def mock_goal():
    goal = MagicMock(spec=Goal)
    goal.id = uuid4()
    goal.twin_id = uuid4()
    goal.title = "Test Goal"
    goal.status = GoalStatus.DRAFT
    goal.progress = 0.0
    return goal


@pytest.mark.asyncio
async def test_create_goal_success(
    service, mock_repo, mock_event_bus, op_ctx, mock_goal
):
    mock_repo.create.return_value = mock_goal
    cmd = CreateGoalCommand(
        twin_id=mock_goal.twin_id,
        title="Test Goal",
        description="Goal desc",
        goal_type=GoalType.STRATEGIC,
    )

    result = await service.create_goal(op_ctx, cmd)

    assert result.goal == mock_goal
    assert result.dispatched_events == 1

    mock_repo.create.assert_called_once()
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, GoalCreatedEvent)
    assert event.goal_id == mock_goal.id


@pytest.mark.asyncio
async def test_get_goal(service, mock_repo, op_ctx, mock_goal):
    mock_repo.get_by_id.return_value = mock_goal

    result = await service.get_goal(op_ctx, mock_goal.id)

    assert result == mock_goal
    mock_repo.get_by_id.assert_called_once_with(mock_goal.id)


@pytest.mark.asyncio
async def test_list_goals(service, mock_repo, op_ctx):
    mock_repo.list_by_twin.return_value = PaginatedGoals(
        items=[], total_count=0, limit=10, offset=0
    )
    query = GoalListQuery(twin_id=uuid4(), limit=10, offset=0)

    result = await service.list_goals(op_ctx, query)

    assert result.total_count == 0
    mock_repo.list_by_twin.assert_called_once()


@pytest.mark.asyncio
async def test_update_goal(service, mock_repo, op_ctx, mock_goal):
    mock_repo.update.return_value = mock_goal
    cmd = UpdateGoalCommand(goal_id=mock_goal.id, title="New Title")

    result = await service.update_goal(op_ctx, cmd)

    assert result == mock_goal
    mock_repo.update.assert_called_once()
    args = mock_repo.update.call_args[0]
    assert args[0] == mock_goal.id
    assert isinstance(args[1], GoalUpdate)
    assert args[1].title == "New Title"


@pytest.mark.asyncio
async def test_update_progress_below_100(service, mock_repo, op_ctx, mock_goal):
    mock_goal.progress = 50.0
    mock_repo.update.return_value = mock_goal
    cmd = UpdateGoalProgressCommand(goal_id=mock_goal.id, progress=50.0)

    result = await service.update_progress(op_ctx, cmd)

    assert result == mock_goal
    mock_repo.update.assert_called_once()
    args = mock_repo.update.call_args[0]
    assert args[1].progress == 50.0


@pytest.mark.asyncio
async def test_update_progress_auto_complete(
    service, mock_repo, mock_event_bus, op_ctx, mock_goal
):
    # Setup initial mock return to simulate progress update
    in_progress_goal = MagicMock(spec=Goal)
    in_progress_goal.id = mock_goal.id
    in_progress_goal.twin_id = mock_goal.twin_id
    in_progress_goal.title = mock_goal.title
    in_progress_goal.status = GoalStatus.IN_PROGRESS

    completed_goal = MagicMock(spec=Goal)
    completed_goal.id = mock_goal.id
    completed_goal.twin_id = mock_goal.twin_id
    completed_goal.title = mock_goal.title
    completed_goal.status = GoalStatus.COMPLETED

    # First update sets progress to 100
    mock_repo.update.side_effect = [in_progress_goal, completed_goal]
    # For status check inside update_goal_status
    mock_repo.get_by_id.return_value = in_progress_goal

    cmd = UpdateGoalProgressCommand(goal_id=mock_goal.id, progress=100.0)
    result = await service.update_progress(op_ctx, cmd)

    assert result == completed_goal
    assert mock_repo.update.call_count == 2

    # Ensure completed events were published
    assert mock_event_bus.publish.call_count == 2


@pytest.mark.asyncio
async def test_update_goal_status(
    service, mock_repo, mock_event_bus, op_ctx, mock_goal
):
    mock_goal.status = GoalStatus.DRAFT
    mock_repo.get_by_id.return_value = mock_goal

    active_goal = MagicMock(spec=Goal)
    active_goal.id = mock_goal.id
    active_goal.twin_id = mock_goal.twin_id
    active_goal.title = mock_goal.title
    active_goal.status = GoalStatus.ACTIVE

    mock_repo.update.return_value = active_goal

    cmd = UpdateGoalStatusCommand(goal_id=mock_goal.id, target_status=GoalStatus.ACTIVE)
    result = await service.update_goal_status(op_ctx, cmd)

    assert result == active_goal
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, GoalStatusChangedEvent)


@pytest.mark.asyncio
async def test_link_intent_to_goal(service, mock_repo, op_ctx):
    from app.models.goal import GoalIntentLink

    cmd = LinkIntentToGoalCommand(intent_id=uuid4(), goal_id=uuid4())
    mock_link = GoalIntentLink(
        id=uuid4(),
        goal_id=cmd.goal_id,
        intent_id=cmd.intent_id,
        created_at=datetime.now(timezone.utc),
    )
    mock_repo.link_intent.return_value = mock_link

    result = await service.link_intent_to_goal(op_ctx, cmd)

    assert result is not None
    mock_repo.link_intent.assert_called_once_with(cmd.intent_id, cmd.goal_id)


@pytest.mark.asyncio
async def test_get_active_goals(service, mock_repo, op_ctx):
    mock_repo.get_active_goals.return_value = []
    twin_id = uuid4()

    result = await service.get_active_goals(op_ctx, twin_id)

    assert result == []
    mock_repo.get_active_goals.assert_called_once_with(twin_id)


@pytest.mark.asyncio
async def test_delete_goal(service, mock_repo, op_ctx):
    cmd = DeleteGoalCommand(goal_id=uuid4())

    await service.delete_goal(op_ctx, cmd)

    mock_repo.soft_delete.assert_called_once_with(cmd.goal_id)
