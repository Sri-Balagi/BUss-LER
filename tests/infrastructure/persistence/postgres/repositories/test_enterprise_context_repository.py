import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.intelligence.intake.situation.enterprise_context import (
    ContextLifecycleCreate,
    ContextLifecycleUpdate,
    ContextLifecycleMetadata,
)
from app.shared.enums import ContextStatus
from app.shared.exceptions.errors import NotFoundError, RepositoryError
from app.infrastructure.persistence.postgres.repositories.enterprise_context_repository import EnterpriseContextRepository


@pytest.fixture
def mock_supabase_client():
    # Use MagicMock so synchronous method chaining works (table().select().eq())
    # Only execute() needs to be awaited.
    client = MagicMock()
    return client


@pytest.fixture
def repository(mock_supabase_client):
    return EnterpriseContextRepository(mock_supabase_client)


@pytest.mark.asyncio
async def test_create_success(repository, mock_supabase_client):
    context_id = uuid.uuid4()
    twin_id = uuid.uuid4()

    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "context_id": str(context_id),
                "twin_id": str(twin_id),
                "policy_id": "test_policy",
                "schema_version": "1.0",
                "status": ContextStatus.BUILDING.value,
                "is_partial": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    )
    mock_supabase_client.table().insert().execute = mock_execute

    data = ContextLifecycleCreate(
        context_id=context_id, twin_id=twin_id, policy_id="test_policy"
    )

    result = await repository.create(data)
    assert isinstance(result, ContextLifecycleMetadata)
    assert result.status == ContextStatus.BUILDING
    assert str(result.context_id) == str(context_id)
    assert str(result.twin_id) == str(twin_id)


@pytest.mark.asyncio
async def test_get_by_id_success(repository, mock_supabase_client):
    context_id = uuid.uuid4()
    twin_id = uuid.uuid4()

    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data={
            "context_id": str(context_id),
            "twin_id": str(twin_id),
            "policy_id": "test_policy",
            "schema_version": "1.0",
            "status": ContextStatus.ASSEMBLED.value,
            "is_partial": False,
        }
    )

    mock_supabase_client.table().select().eq().is_().single().execute = mock_execute

    result = await repository.get_by_id(context_id)
    assert isinstance(result, ContextLifecycleMetadata)
    assert result.status == ContextStatus.ASSEMBLED


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=None)

    mock_supabase_client.table().select().eq().is_().single().execute = mock_execute

    with pytest.raises(NotFoundError):
        await repository.get_by_id(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_status_success(repository, mock_supabase_client):
    context_id = uuid.uuid4()

    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "context_id": str(context_id),
                "twin_id": str(uuid.uuid4()),
                "policy_id": "test_policy",
                "schema_version": "1.0",
                "status": ContextStatus.ASSEMBLED.value,
                "is_partial": True,
            }
        ]
    )

    mock_supabase_client.table().update().eq().execute = mock_execute

    update_data = ContextLifecycleUpdate(
        status=ContextStatus.ASSEMBLED, is_partial=True
    )

    result = await repository.update_status(context_id, update_data)
    assert result.status == ContextStatus.ASSEMBLED
    assert result.is_partial is True


@pytest.mark.asyncio
async def test_create_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().insert().execute = mock_execute

    data = ContextLifecycleCreate(
        context_id=uuid.uuid4(),
        twin_id=uuid.uuid4(),
        policy_id="test",
        schema_version="1.0",
    )
    with pytest.raises(RepositoryError) as exc_info:
        await repository.create(data)
    assert "context.create" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_get_by_id_repository_error(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq().is_().single().execute = mock_execute

    with pytest.raises(RepositoryError) as exc_info:
        await repository.get_by_id(uuid.uuid4())
    assert "context.get_by_id" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_update_status_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().update().eq().execute = mock_execute

    with pytest.raises(RepositoryError) as exc_info:
        await repository.update_status(
            uuid.uuid4(), ContextLifecycleUpdate(status=ContextStatus.ASSEMBLED)
        )
    assert "context.update_status" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_update_status_full_fields(repository, mock_supabase_client):
    context_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "context_id": str(context_id),
                "twin_id": str(uuid.uuid4()),
                "policy_id": "test_policy",
                "schema_version": "1.0",
                "status": ContextStatus.ARCHIVED.value,
                "is_partial": True,
                "assembled_at": now.isoformat(),
                "expires_at": now.isoformat(),
                "consumed_at": now.isoformat(),
                "archived_at": now.isoformat(),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }
        ]
    )
    mock_supabase_client.table().update().eq().execute = mock_execute

    update = ContextLifecycleUpdate(
        status=ContextStatus.ARCHIVED,
        is_partial=True,
        assembled_at=now,
        expires_at=now,
        consumed_at=now,
        archived_at=now,
    )
    result = await repository.update_status(context_id, update)
    assert result.status == ContextStatus.ARCHIVED
    assert result.assembled_at == now
    assert result.archived_at == now


@pytest.mark.asyncio
async def test_list_by_twin_success(repository, mock_supabase_client):
    twin_id = uuid.uuid4()
    now = datetime.now(timezone.utc).isoformat()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[
            {
                "context_id": str(uuid.uuid4()),
                "twin_id": str(twin_id),
                "policy_id": "test",
                "schema_version": "1.0",
                "status": ContextStatus.ASSEMBLED.value,
                "is_partial": False,
                "created_at": now,
                "updated_at": now,
            }
        ],
        count=1,
    )

    mock_query = MagicMock()
    mock_query.execute = mock_execute
    mock_query.eq.return_value = mock_query
    mock_query.range.return_value = mock_query

    # We must patch the chain
    mock_supabase_client.table().select().eq().is_().order().range.return_value = (
        mock_query
    )

    result = await repository.list_by_twin(twin_id, status=ContextStatus.ASSEMBLED)
    assert result.total_count == 1
    assert len(result.items) == 1
    assert result.items[0].status == ContextStatus.ASSEMBLED


@pytest.mark.asyncio
async def test_list_by_twin_failure(repository, mock_supabase_client):
    mock_query = MagicMock()
    mock_query.execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq().is_().order().range.return_value = (
        mock_query
    )

    with pytest.raises(RepositoryError) as exc_info:
        await repository.list_by_twin(uuid.uuid4())
    assert "context.list_by_twin" in str(exc_info.value.operation)


@pytest.mark.asyncio
async def test_health_check_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_supabase_client.table().select().limit().execute = mock_execute

    health = await repository.health_check()
    assert health["enterprise_context_repository"] == "ok"


@pytest.mark.asyncio
async def test_health_check_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().limit().execute = mock_execute

    health = await repository.health_check()
    assert health["enterprise_context_repository"] == "error"
    assert "DB Error" in health["detail"]
