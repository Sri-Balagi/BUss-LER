from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.models.cognitive_trace import CognitiveTraceCreate, CognitiveTraceTokenUsage
from app.models.exceptions import CognitiveTraceNotFoundError, RepositoryError
from app.repositories.cognitive_trace_repository import CognitiveTraceRepository


@pytest.fixture
def mock_supabase(mocker):
    mock = mocker.MagicMock()
    return mock


@pytest.fixture
def repo(mock_supabase):
    return CognitiveTraceRepository(client=mock_supabase)


@pytest.mark.asyncio
async def test_create_success(repo, mock_supabase, mocker):
    trace_id = uuid4()
    twin_id = uuid4()

    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [
        {
            "id": str(trace_id),
            "twin_id": str(twin_id),
            "operation_type": "test_op",
            "provider": "test",
            "model": "model",
            "prompt_version": "1.0",
            "operation_context_id": "ctx-1",
            "reasoning_summary": "sum",
            "latency_ms": 100,
            "token_usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
            "memory_ids_used": [],
            "goal_ids_used": [],
            "metadata": {},
            "created_at": datetime.now(UTC).isoformat(),
        }
    ]
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    create_data = CognitiveTraceCreate(
        twin_id=twin_id,
        operation_type="test_op",
        provider="test",
        model="model",
        prompt_version="1.0",
        operation_context_id="ctx-1",
        reasoning_summary="sum",
        latency_ms=100,
        token_usage=CognitiveTraceTokenUsage(
            prompt_tokens=10, completion_tokens=5, total_tokens=15
        ),
        memory_ids_used=[],
        goal_ids_used=[],
        metadata={},
        intent_id=uuid4(),
        confidence=0.9,
    )

    result = await repo.create(create_data)
    assert result.id == trace_id
    assert result.operation_type == "test_op"
    assert result.token_usage.total_tokens == 15


@pytest.mark.asyncio
async def test_create_exception(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    create_data = CognitiveTraceCreate(
        twin_id=uuid4(),
        operation_type="test_op",
        provider="test",
        model="model",
        prompt_version="1.0",
        operation_context_id="ctx-1",
        reasoning_summary="sum",
        latency_ms=100,
        token_usage=CognitiveTraceTokenUsage(
            prompt_tokens=10, completion_tokens=5, total_tokens=15
        ),
        memory_ids_used=[],
        goal_ids_used=[],
    )

    with pytest.raises(RepositoryError):
        await repo.create(create_data)


@pytest.mark.asyncio
async def test_get_by_id_success(repo, mock_supabase, mocker):
    trace_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = [
        {
            "id": str(trace_id),
            "twin_id": str(uuid4()),
            "operation_type": "test_op",
            "provider": "test",
            "model": "model",
            "prompt_version": "1.0",
            "operation_context_id": "ctx-1",
            "reasoning_summary": "sum",
            "latency_ms": 100,
            "token_usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
            "memory_ids_used": [str(uuid4())],
            "goal_ids_used": [str(uuid4())],
            "metadata": {},
            "created_at": datetime.now(UTC).isoformat(),
        }
    ]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    result = await repo.get_by_id(trace_id)
    assert result.id == trace_id
    assert len(result.memory_ids_used) == 1
    assert len(result.goal_ids_used) == 1


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_supabase, mocker):
    trace_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(CognitiveTraceNotFoundError):
        await repo.get_by_id(trace_id)


@pytest.mark.asyncio
async def test_get_by_id_exception(repo, mock_supabase, mocker):
    trace_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.get_by_id(trace_id)


@pytest.mark.asyncio
async def test_list_by_twin_success(repo, mock_supabase, mocker):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_execute.return_value.count = 0
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_twin(twin_id=twin_id)
    assert result.total_count == 0
    assert len(result.items) == 0


@pytest.mark.asyncio
async def test_list_by_twin_with_op(repo, mock_supabase, mocker):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_execute.return_value.count = 0
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_twin(twin_id=twin_id, operation_type="test")
    assert result.total_count == 0


@pytest.mark.asyncio
async def test_list_by_twin_exception(repo, mock_supabase, mocker):
    twin_id = uuid4()
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.list_by_twin(twin_id=twin_id)


@pytest.mark.asyncio
async def test_list_by_operation_success(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_execute.return_value.count = 0
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_operation(operation_type="test")
    assert result.total_count == 0


@pytest.mark.asyncio
async def test_list_by_operation_exception(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.list_by_operation(operation_type="test")


@pytest.mark.asyncio
async def test_list_by_context_success(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock()
    mock_execute.return_value.data = []
    mock_execute.return_value.count = 0
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    result = await repo.list_by_context(operation_context_id="ctx-1")
    assert result.total_count == 0


@pytest.mark.asyncio
async def test_list_by_context_exception(repo, mock_supabase, mocker):
    mock_execute = mocker.AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    with pytest.raises(RepositoryError):
        await repo.list_by_context(operation_context_id="ctx-1")


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
