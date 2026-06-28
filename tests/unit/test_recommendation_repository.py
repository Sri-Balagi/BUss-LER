import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.models.recommendation import RecommendationCreate
from app.models.enums import RecommendationStatus, RecommendationConfidence
from app.models.exceptions import RecommendationNotFoundError, RepositoryError
from app.repositories.recommendation_repository import RecommendationRepository


@pytest.fixture
def mock_supabase(mocker):
    mock = mocker.MagicMock()
    return mock


@pytest.fixture
def repo(mock_supabase):
    return RecommendationRepository(client=mock_supabase)


@pytest.fixture
def sample_rec_data():
    return {
        "id": str(uuid4()),
        "twin_id": str(uuid4()),
        "title": "Rec Title",
        "body": "Rec Body",
        "rationale": "Rec Rationale",
        "confidence": "high",
        "trigger_context": {"event": "test"},
        "explainability_metadata": {},
        "metadata": {},
        "supporting_memory_ids": [str(uuid4())],
        "supporting_goal_ids": [str(uuid4())],
        "status": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.mark.asyncio
async def test_create_success(repo, mock_supabase, mocker, sample_rec_data):
    twin_id = uuid4()

    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_rec_data]
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    create_data = RecommendationCreate(
        title="Rec Title",
        body="Rec Body",
        rationale="Rec Rationale",
        confidence=RecommendationConfidence.HIGH,
        trigger_context={"event": "test"},
        explainability_metadata={},
        metadata={},
        supporting_memory_ids=[],
        supporting_goal_ids=[],
    )

    result = await repo.create(twin_id=twin_id, data=create_data)
    assert result.id == UUID(sample_rec_data["id"])
    assert result.title == "Rec Title"


@pytest.mark.asyncio
async def test_create_exception(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    create_data = RecommendationCreate(
        title="Rec Title",
        body="Rec Body",
        rationale="Rec Rationale",
        confidence=RecommendationConfidence.HIGH,
        trigger_context={"event": "test"},
        explainability_metadata={},
        metadata={},
        supporting_memory_ids=[],
        supporting_goal_ids=[],
    )

    with pytest.raises(RepositoryError):
        await repo.create(twin_id=uuid4(), data=create_data)


@pytest.mark.asyncio
async def test_get_by_id_success(repo, mock_supabase, mocker, sample_rec_data):
    rec_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_rec_data]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = (
        mock_execute
    )

    result = await repo.get_by_id(rec_id)
    assert result.id == UUID(sample_rec_data["id"])


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_supabase, mocker):
    rec_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = (
        mock_execute
    )

    with pytest.raises(RecommendationNotFoundError):
        await repo.get_by_id(rec_id)


@pytest.mark.asyncio
async def test_get_by_id_exception(repo, mock_supabase, mocker):
    rec_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = (
        mock_execute
    )

    with pytest.raises(RepositoryError):
        await repo.get_by_id(rec_id)


@pytest.mark.asyncio
async def test_list_by_twin_success(repo, mock_supabase, mocker, sample_rec_data):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_rec_data]
    mock_execute.return_value.count = 1
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_twin(twin_id=twin_id)
    assert result.total_count == 1
    assert len(result.items) == 1


@pytest.mark.asyncio
async def test_list_by_twin_with_status(repo, mock_supabase, mocker, sample_rec_data):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_rec_data]
    mock_execute.return_value.count = 1
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_twin(twin_id=twin_id, status=RecommendationStatus.NEW)
    assert result.total_count == 1


@pytest.mark.asyncio
async def test_list_by_twin_exception(repo, mock_supabase, mocker):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.list_by_twin(twin_id=twin_id)


@pytest.mark.asyncio
async def test_update_status_success(repo, mock_supabase, mocker, sample_rec_data):
    rec_id = uuid4()
    sample_rec_data["status"] = "acknowledged"
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [sample_rec_data]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = (
        mock_execute
    )

    result = await repo.update_status(rec_id, RecommendationStatus.ACKNOWLEDGED)
    assert result.status == RecommendationStatus.ACKNOWLEDGED


@pytest.mark.asyncio
async def test_update_status_not_found(repo, mock_supabase, mocker):
    rec_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = (
        mock_execute
    )

    with pytest.raises(RecommendationNotFoundError):
        await repo.update_status(rec_id, RecommendationStatus.ACKNOWLEDGED)


@pytest.mark.asyncio
async def test_update_status_exception(repo, mock_supabase, mocker):
    rec_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = (
        mock_execute
    )

    with pytest.raises(RepositoryError):
        await repo.update_status(rec_id, RecommendationStatus.ACKNOWLEDGED)


@pytest.mark.asyncio
async def test_health_check_healthy(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(return_value=True)
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute = (
        mock_execute
    )
    result = await repo.health_check()
    assert result["status"] == "healthy"
    assert result["database"] is True


@pytest.mark.asyncio
async def test_health_check_unhealthy(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute = (
        mock_execute
    )
    result = await repo.health_check()
    assert result["status"] == "unhealthy"
    assert result["database"] is False
    assert result["detail"] == "DB Error"
