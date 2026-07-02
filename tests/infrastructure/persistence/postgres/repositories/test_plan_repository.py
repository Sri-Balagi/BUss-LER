from datetime import UTC, datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.infrastructure.persistence.postgres.repositories.plan_repository import PlanRepository
from app.intelligence.decision.planning.plan import PlanCreate, PlanStep
from app.shared.enums import PlanStatus
from app.shared.exceptions.errors import PlanNotFoundError, RepositoryError


@pytest.fixture
def mock_supabase(mocker):
    mock = mocker.MagicMock()
    return mock


@pytest.fixture
def repo(mock_supabase):
    return PlanRepository(client=mock_supabase)


@pytest.fixture
def sample_plan_data():
    return {
        "id": str(uuid4()),
        "twin_id": str(uuid4()),
        "goal_id": str(uuid4()),
        "intent_id": str(uuid4()),
        "rationale": "Test rationale",
        "steps": [
            {
                "id": str(uuid4()),
                "step_number": 1,
                "action": "API_CALL",
                "expected_outcome": "success",
                "depends_on": [],
            }
        ],
        "status": "draft",
        "assumptions": ["assumption1"],
        "risks": [{"risk": "risk1", "likelihood": "high", "mitigation": "none"}],
        "dependencies": ["dep1"],
        "confidence": 0.9,
        "estimated_effort": "low",
        "metadata": {},
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }


@pytest.mark.asyncio
async def test_create_success(repo, mock_supabase, mocker, sample_plan_data):
    twin_id = uuid4()
    goal_id = uuid4()
    intent_id = uuid4()

    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_plan_data]
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    create_data = PlanCreate(
        rationale="Test rationale",
        steps=[PlanStep(step_number=1, action="API_CALL", expected_outcome="success")],
        assumptions=["assumption1"],
        risks=[{"risk": "risk1", "likelihood": "high", "mitigation": "none"}],
        dependencies=["dep1"],
        confidence=0.9,
        estimated_effort="low",
        metadata={},
    )

    result = await repo.create(
        twin_id=twin_id, goal_id=goal_id, intent_id=intent_id, data=create_data
    )
    assert result.id == UUID(sample_plan_data["id"])
    assert result.rationale == "Test rationale"
    assert len(result.steps) == 1


@pytest.mark.asyncio
async def test_create_exception(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    create_data = PlanCreate(
        rationale="Test rationale",
        steps=[PlanStep(step_number=1, action="API_CALL", expected_outcome="fail")],
    )

    with pytest.raises(RepositoryError):
        await repo.create(twin_id=uuid4(), goal_id=None, intent_id=None, data=create_data)


@pytest.mark.asyncio
async def test_get_by_id_success(repo, mock_supabase, mocker, sample_plan_data):
    plan_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_plan_data]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    result = await repo.get_by_id(plan_id)
    assert result.id == UUID(sample_plan_data["id"])


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_supabase, mocker):
    plan_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(PlanNotFoundError):
        await repo.get_by_id(plan_id)


@pytest.mark.asyncio
async def test_get_by_id_exception(repo, mock_supabase, mocker):
    plan_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.get_by_id(plan_id)


@pytest.mark.asyncio
async def test_list_by_twin_success(repo, mock_supabase, mocker, sample_plan_data):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_plan_data]
    mock_execute.return_value.count = 1
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_twin(twin_id=twin_id)
    assert result.total_count == 1
    assert len(result.items) == 1


@pytest.mark.asyncio
async def test_list_by_twin_with_goal_and_intent(repo, mock_supabase, mocker):
    twin_id = uuid4()
    goal_id = uuid4()
    intent_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_execute.return_value.count = 0
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_twin(twin_id=twin_id, goal_id=goal_id, intent_id=intent_id)
    assert result.total_count == 0


@pytest.mark.asyncio
async def test_list_by_twin_exception(repo, mock_supabase, mocker):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.list_by_twin(twin_id=twin_id)


@pytest.mark.asyncio
async def test_update_status_success(repo, mock_supabase, mocker, sample_plan_data):
    plan_id = uuid4()
    sample_plan_data["status"] = "executing"
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_plan_data]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    result = await repo.update_status(plan_id, PlanStatus.EXECUTING)
    assert result.status == PlanStatus.EXECUTING


@pytest.mark.asyncio
async def test_update_status_not_found(repo, mock_supabase, mocker):
    plan_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(PlanNotFoundError):
        await repo.update_status(plan_id, PlanStatus.EXECUTING)


@pytest.mark.asyncio
async def test_update_status_exception(repo, mock_supabase, mocker):
    plan_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.update_status(plan_id, PlanStatus.EXECUTING)


@pytest.mark.asyncio
async def test_health_check_healthy(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(return_value=True)
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute = mock_execute
    result = await repo.health_check()
    assert result["status"] == "healthy"
    assert result["database"] is True


@pytest.mark.asyncio
async def test_health_check_unhealthy(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute = mock_execute
    result = await repo.health_check()
    assert result["status"] == "unhealthy"
    assert result["database"] is False
    assert result["detail"] == "DB Error"
