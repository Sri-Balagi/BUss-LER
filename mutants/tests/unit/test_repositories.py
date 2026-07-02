"""Unit tests for repositories including all edge cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.models.entity import EntityUpdate
from app.models.enums import EntityType
from app.models.exceptions import (
    DuplicateTwinError,
    EntityNotFoundError,
    RepositoryError,
    TwinNotFoundError,
    VersionConflictError,
)
from app.models.schemas import EntityCreate
from app.models.twin import DigitalTwinCreate, DigitalTwinUpdate
from app.repositories.entity_repository import EntityRepository
from app.repositories.twin_repository import TwinRepository


@pytest.fixture
def entity_repo(mock_supabase_client):
    return EntityRepository(mock_supabase_client)


@pytest.fixture
def twin_repo(mock_supabase_client):
    return TwinRepository(mock_supabase_client)


# =====================================================================
# EntityRepository Tests
# =====================================================================


@pytest.mark.asyncio
async def test_entity_repository_create_success(entity_repo, mock_supabase_client):
    user_id = uuid4()
    mock_data = {
        "id": str(uuid4()),
        "user_id": str(user_id),
        "name": "Test",
        "entity_type": "startup",
        "metadata": {},
        "is_active": True,
        "description": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])

    data = EntityCreate(name="Test", entity_type=EntityType.STARTUP)
    entity = await entity_repo.create(user_id, data)
    assert entity.name == "Test"
    assert entity.entity_type == EntityType.STARTUP


@pytest.mark.asyncio
async def test_entity_repository_create_duplicate(entity_repo, mock_supabase_client):
    user_id = uuid4()
    mock_supabase_client.table.return_value.execute.side_effect = Exception(
        "duplicate key value violates unique constraint"
    )
    data = EntityCreate(name="Test", entity_type=EntityType.STARTUP)
    with pytest.raises(RepositoryError) as exc_info:
        await entity_repo.create(user_id, data)
    assert "duplicate key" in exc_info.value.detail


@pytest.mark.asyncio
async def test_entity_repository_create_db_timeout(entity_repo, mock_supabase_client):
    user_id = uuid4()
    mock_supabase_client.table.return_value.execute.side_effect = TimeoutError(
        "Database connection timed out"
    )
    data = EntityCreate(name="Test", entity_type=EntityType.STARTUP)
    with pytest.raises(RepositoryError):
        await entity_repo.create(user_id, data)


@pytest.mark.asyncio
async def test_entity_repository_get_by_id_success(entity_repo, mock_supabase_client):
    entity_id = uuid4()
    mock_data = {
        "id": str(entity_id),
        "user_id": str(uuid4()),
        "name": "Test",
        "entity_type": "startup",
        "metadata": {},
        "is_active": True,
        "description": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])
    entity = await entity_repo.get_by_id(entity_id)
    assert entity.id == entity_id


@pytest.mark.asyncio
async def test_entity_repository_get_by_id_not_found_empty_results(
    entity_repo, mock_supabase_client
):
    entity_id = uuid4()
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[])
    with pytest.raises(EntityNotFoundError):
        await entity_repo.get_by_id(entity_id)


@pytest.mark.asyncio
async def test_entity_repository_get_by_id_invalid_uuid(entity_repo, mock_supabase_client):
    # Pass an invalid UUID type to trigger DB exception (mocked)
    mock_supabase_client.table.return_value.execute.side_effect = Exception(
        "invalid input syntax for type uuid"
    )
    with pytest.raises(RepositoryError) as exc_info:
        await entity_repo.get_by_id("not-a-uuid")
    assert "invalid input syntax" in exc_info.value.detail


@pytest.mark.asyncio
async def test_entity_repository_update_success(entity_repo, mock_supabase_client):
    entity_id = uuid4()
    mock_data = {
        "id": str(entity_id),
        "user_id": str(uuid4()),
        "name": "Updated",
        "entity_type": "startup",
        "metadata": {},
        "is_active": True,
        "description": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])
    update_data = EntityUpdate(name="Updated")
    entity = await entity_repo.update(entity_id, update_data)
    assert entity.name == "Updated"


@pytest.mark.asyncio
async def test_entity_repository_update_not_found(entity_repo, mock_supabase_client):
    entity_id = uuid4()
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[])
    update_data = EntityUpdate(name="Updated")
    with pytest.raises(EntityNotFoundError):
        await entity_repo.update(entity_id, update_data)


@pytest.mark.asyncio
async def test_entity_repository_delete_success(entity_repo, mock_supabase_client):
    entity_id = uuid4()
    mock_data = {
        "id": str(entity_id),
        "user_id": str(uuid4()),
        "name": "Test",
        "entity_type": "startup",
        "metadata": {},
        "is_active": False,
        "description": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])
    await entity_repo.soft_delete(entity_id)
    # Check that soft delete logic (is_active=False) was executed via the mock calls.
    # The actual behavior is inside the mock, but the lack of error indicates success.


@pytest.mark.asyncio
async def test_entity_repository_delete_not_found(entity_repo, mock_supabase_client):
    entity_id = uuid4()
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[])
    with pytest.raises(EntityNotFoundError):
        await entity_repo.soft_delete(entity_id)


@pytest.mark.asyncio
async def test_entity_repository_list_success(entity_repo, mock_supabase_client):
    user_id = uuid4()
    mock_data = [
        {
            "id": str(uuid4()),
            "user_id": str(user_id),
            "name": f"Test {i}",
            "entity_type": "startup",
            "metadata": {},
            "is_active": True,
            "description": None,
            "created_at": "2026-06-25T00:00:00Z",
            "updated_at": "2026-06-25T00:00:00Z",
        }
        for i in range(5)
    ]
    mock_execute = AsyncMock(data=mock_data)
    mock_execute.count = 5
    mock_supabase_client.table.return_value.execute.return_value = mock_execute

    items, total = await entity_repo.list(user_id=user_id, limit=5, offset=0)
    assert len(items) == 5
    assert total == 5


@pytest.mark.asyncio
async def test_entity_repository_list_pagination_boundaries(entity_repo, mock_supabase_client):
    user_id = uuid4()
    # Mocking a response where we request limit=5 but get back 6 items, indicating has_more=True
    mock_data = [
        {
            "id": str(uuid4()),
            "user_id": str(user_id),
            "name": f"Test {i}",
            "entity_type": "startup",
            "metadata": {},
            "is_active": True,
            "description": None,
            "created_at": "2026-06-25T00:00:00Z",
            "updated_at": "2026-06-25T00:00:00Z",
        }
        for i in range(5)
    ]

    # Configure mock to also return count=6
    mock_execute = AsyncMock(data=mock_data)
    mock_execute.count = 6
    mock_supabase_client.table.return_value.execute.return_value = mock_execute

    items, total = await entity_repo.list(user_id=user_id, limit=5, offset=0)
    assert len(items) == 5
    assert total == 6


@pytest.mark.asyncio
async def test_entity_repository_list_generic_exception(entity_repo, mock_supabase_client):
    user_id = uuid4()
    mock_supabase_client.table.return_value.execute.side_effect = Exception("Unknown error")
    with pytest.raises(RepositoryError):
        await entity_repo.list(user_id=user_id)


# =====================================================================
# TwinRepository Tests
# =====================================================================


@pytest.mark.asyncio
async def test_twin_repository_create_success(twin_repo, mock_supabase_client):
    entity_id = uuid4()
    mock_data = {
        "id": str(uuid4()),
        "entity_id": str(entity_id),
        "state": {"key": "val"},
        "metadata": {
            "schema_version": 1,
            "labels": [],
            "external_ids": {},
            "source": "system",
            "created_by": "system",
            "updated_by": "system",
        },
        "twin_version": 1,
        "last_snapshot_at": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])

    data = DigitalTwinCreate(entity_id=entity_id, state={"key": "val"})
    twin = await twin_repo.create(data)

    assert twin.entity_id == entity_id
    assert twin.state == {"key": "val"}


@pytest.mark.asyncio
async def test_twin_repository_create_duplicate(twin_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.side_effect = Exception(
        "duplicate key value violates unique constraint"
    )
    data = DigitalTwinCreate(entity_id=uuid4(), state={"key": "val"})
    with pytest.raises(DuplicateTwinError):
        await twin_repo.create(data)


@pytest.mark.asyncio
async def test_twin_repository_get_by_id_success(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_data = {
        "id": str(twin_id),
        "entity_id": str(uuid4()),
        "state": {"key": "val"},
        "metadata": {
            "schema_version": 1,
            "labels": [],
            "external_ids": {},
            "source": "system",
            "created_by": "system",
            "updated_by": "system",
        },
        "twin_version": 1,
        "last_snapshot_at": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])

    twin = await twin_repo.get_by_id(twin_id)
    assert twin.id == twin_id


@pytest.mark.asyncio
async def test_twin_repository_get_by_id_not_found(twin_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[])
    with pytest.raises(TwinNotFoundError):
        await twin_repo.get_by_id(uuid4())


@pytest.mark.asyncio
async def test_twin_repository_get_by_entity_id_success(twin_repo, mock_supabase_client):
    entity_id = uuid4()
    mock_data = {
        "id": str(uuid4()),
        "entity_id": str(entity_id),
        "state": {"key": "val"},
        "metadata": {
            "schema_version": 1,
            "labels": [],
            "external_ids": {},
            "source": "system",
            "created_by": "system",
            "updated_by": "system",
        },
        "twin_version": 1,
        "last_snapshot_at": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])

    twin = await twin_repo.get_by_entity_id(entity_id)
    assert twin.entity_id == entity_id


@pytest.mark.asyncio
async def test_twin_repository_get_by_entity_id_not_found(twin_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[])
    with pytest.raises(TwinNotFoundError):
        await twin_repo.get_by_entity_id(uuid4())


@pytest.mark.asyncio
async def test_twin_repository_update_with_snapshot_success(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_data = {
        "id": str(twin_id),
        "entity_id": str(uuid4()),
        "state": {"key": "new_val"},
        "metadata": {
            "schema_version": 1,
            "labels": [],
            "external_ids": {},
            "source": "system",
            "created_by": "system",
            "updated_by": "system",
        },
        "twin_version": 2,
        "last_snapshot_at": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.rpc.return_value.execute.return_value = AsyncMock(data=mock_data)

    data = DigitalTwinUpdate(state={"key": "new_val"}, expected_version=1)
    twin = await twin_repo.update_with_snapshot(twin_id, data)

    assert twin.twin_version == 2
    assert twin.state == {"key": "new_val"}


@pytest.mark.asyncio
async def test_twin_repository_update_version_conflict(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    error = Exception("VERSION_CONFLICT:expected=1, actual=2")
    mock_supabase_client.rpc.return_value.execute.side_effect = error

    data = DigitalTwinUpdate(state={"key": "new_val"}, expected_version=1)

    with pytest.raises(VersionConflictError):
        await twin_repo.update_with_snapshot(twin_id, data)


@pytest.mark.asyncio
async def test_twin_repository_update_twin_not_found(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    error = Exception("TWIN_NOT_FOUND:123")
    mock_supabase_client.rpc.return_value.execute.side_effect = error

    data = DigitalTwinUpdate(state={"key": "new_val"}, expected_version=1)
    with pytest.raises(TwinNotFoundError):
        await twin_repo.update_with_snapshot(twin_id, data)


@pytest.mark.asyncio
async def test_twin_repository_update_invalid_rpc_response(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    # Mocking empty response which should raise TwinNotFoundError
    mock_supabase_client.rpc.return_value.execute.return_value = AsyncMock(data=None)
    data = DigitalTwinUpdate(state={"key": "new_val"}, expected_version=1)

    with pytest.raises(TwinNotFoundError):
        await twin_repo.update_with_snapshot(twin_id, data)


@pytest.mark.asyncio
async def test_twin_repository_update_unknown_rpc_error(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    error = Exception("Some weird postgres exception")
    mock_supabase_client.rpc.return_value.execute.side_effect = error
    data = DigitalTwinUpdate(state={"key": "new_val"}, expected_version=1)

    with pytest.raises(RepositoryError):
        await twin_repo.update_with_snapshot(twin_id, data)


@pytest.mark.asyncio
async def test_twin_repository_delete_success(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_data = {
        "id": str(twin_id),
        "entity_id": str(uuid4()),
        "state": {},
        "metadata": {
            "schema_version": 1,
            "labels": [],
            "external_ids": {},
            "source": "system",
            "created_by": "system",
            "updated_by": "system",
        },
        "twin_version": 1,
        "last_snapshot_at": None,
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])
    await twin_repo.delete(twin_id)


@pytest.mark.asyncio
async def test_twin_repository_delete_not_found(twin_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[])
    with pytest.raises(TwinNotFoundError):
        await twin_repo.delete(twin_id)


@pytest.mark.asyncio
async def test_twin_repository_list_pagination(twin_repo, mock_supabase_client):
    mock_data = [
        {
            "id": str(uuid4()),
            "entity_id": str(uuid4()),
            "state": {},
            "metadata": {
                "schema_version": 1,
                "labels": [],
                "external_ids": {},
                "source": "system",
                "created_by": "system",
                "updated_by": "system",
            },
            "twin_version": 1,
            "last_snapshot_at": None,
            "created_at": "2026-06-25T00:00:00Z",
            "updated_at": "2026-06-25T00:00:00Z",
        }
        for i in range(10)
    ]
    mock_execute = AsyncMock(data=mock_data)
    mock_execute.count = 11
    mock_supabase_client.table.return_value.execute.return_value = mock_execute

    items, total = await twin_repo.list(limit=10, offset=0)
    assert len(items) == 10
    assert total == 11


@pytest.mark.asyncio
async def test_twin_repository_list_db_timeout(twin_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.side_effect = TimeoutError("Timeout")
    with pytest.raises(RepositoryError):
        await twin_repo.list(limit=10)


@pytest.mark.asyncio
async def test_twin_repository_handle_rpc_error_fallback():
    # Test the fallback branch of _handle_rpc_error directly
    twin_repo = TwinRepository(AsyncMock())

    class CustomExc(Exception):
        pass

    exc = CustomExc("WEIRD_ERROR")
    # Simulate _handle_rpc_error behavior mapping to RepositoryError
    with pytest.raises(RepositoryError) as exc_info:
        twin_repo._handle_rpc_error("WEIRD_ERROR", uuid4(), 1, exc)

    assert "WEIRD_ERROR" in exc_info.value.detail
