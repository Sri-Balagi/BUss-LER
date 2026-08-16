from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.infrastructure.persistence.postgres.repositories.twin_repository import TwinRepository
from app.interfaces.http.schemas.twin import DigitalTwinCreate, DigitalTwinUpdate, TwinMetadata
from app.shared.exceptions.errors import (
    DuplicateTwinError,
    RepositoryError,
    TwinNotFoundError,
    VersionConflictError,
)


@pytest.fixture
def mock_client():
    client = MagicMock()
    # Mocks for table chaining: table().select().eq().execute()
    return client

@pytest.fixture
def repo(mock_client):
    return TwinRepository(mock_client)

@pytest.mark.asyncio
async def test_create_success(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = [{"id": str(uuid4()), "entity_id": str(uuid4()), "state": {}, "metadata": {}, "twin_version": 1, "last_snapshot_at": "2026-07-23T00:00:00Z", "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_client.table.return_value.insert.return_value.execute = mock_execute

    data = DigitalTwinCreate(entity_id=uuid4(), state={}, metadata=TwinMetadata(schema_version="1.0"))
    result = await repo.create(data)
    assert result is not None
    assert mock_execute.called

@pytest.mark.asyncio
async def test_create_duplicate(repo, mock_client):
    mock_execute = AsyncMock(side_effect=Exception("duplicate key value violates unique constraint"))
    mock_client.table.return_value.insert.return_value.execute = mock_execute

    data = DigitalTwinCreate(entity_id=uuid4(), state={}, metadata=TwinMetadata(schema_version="1.0"))
    with pytest.raises(DuplicateTwinError):
        await repo.create(data)

@pytest.mark.asyncio
async def test_get_by_id_success(repo, mock_client):
    mock_execute = AsyncMock()
    twin_id = str(uuid4())
    mock_execute.return_value.data = [{"id": twin_id, "entity_id": str(uuid4()), "state": {}, "metadata": {}, "twin_version": 1, "last_snapshot_at": "2026-07-23T00:00:00Z", "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    result = await repo.get_by_id(uuid4())
    assert str(result.id) == twin_id

@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(TwinNotFoundError):
        await repo.get_by_id(uuid4())

@pytest.mark.asyncio
async def test_get_by_entity_id_success(repo, mock_client):
    mock_execute = AsyncMock()
    entity_id = str(uuid4())
    mock_execute.return_value.data = [{"id": str(uuid4()), "entity_id": entity_id, "state": {}, "metadata": {}, "twin_version": 1, "last_snapshot_at": "2026-07-23T00:00:00Z", "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    result = await repo.get_by_entity_id(uuid4())
    assert str(result.entity_id) == entity_id

@pytest.mark.asyncio
async def test_get_by_entity_id_not_found(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(TwinNotFoundError):
        await repo.get_by_entity_id(uuid4())

@pytest.mark.asyncio
async def test_list_success(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = [{"id": str(uuid4()), "entity_id": str(uuid4()), "state": {}, "metadata": {}, "twin_version": 1, "last_snapshot_at": "2026-07-23T00:00:00Z", "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_execute.return_value.count = 1
    mock_client.table.return_value.select.return_value.order.return_value.range.return_value.execute = mock_execute

    items, total = await repo.list()
    assert len(items) == 1
    assert total == 1

@pytest.mark.asyncio
async def test_update_with_snapshot_success(repo, mock_client):
    mock_execute = AsyncMock()
    twin_id = str(uuid4())
    mock_execute.return_value.data = [{"id": twin_id, "entity_id": str(uuid4()), "state": {}, "metadata": {}, "twin_version": 2, "last_snapshot_at": "2026-07-23T00:00:00Z", "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_client.rpc.return_value.execute = mock_execute

    update_data = DigitalTwinUpdate(expected_version=1, state={"status": "new"})
    result = await repo.update_with_snapshot(uuid4(), update_data)
    assert result is not None

@pytest.mark.asyncio
async def test_update_with_snapshot_not_found(repo, mock_client):
    mock_execute = AsyncMock(side_effect=Exception("TWIN_NOT_FOUND"))
    mock_execute.side_effect.message = "TWIN_NOT_FOUND:123"
    mock_client.rpc.return_value.execute = mock_execute

    update_data = DigitalTwinUpdate(expected_version=1)
    with pytest.raises(TwinNotFoundError):
        await repo.update_with_snapshot(uuid4(), update_data)

@pytest.mark.asyncio
async def test_update_with_snapshot_version_conflict(repo, mock_client):
    mock_execute = AsyncMock(side_effect=Exception("VERSION_CONFLICT:expected=1, actual=2"))
    mock_execute.side_effect.message = "VERSION_CONFLICT:expected=1, actual=2"
    mock_client.rpc.return_value.execute = mock_execute

    update_data = DigitalTwinUpdate(expected_version=1)
    with pytest.raises(VersionConflictError):
        await repo.update_with_snapshot(uuid4(), update_data)

@pytest.mark.asyncio
async def test_delete_success(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = [{"id": str(uuid4())}]
    mock_client.table.return_value.delete.return_value.eq.return_value.execute = mock_execute

    await repo.delete(uuid4())
    assert mock_execute.called

@pytest.mark.asyncio
async def test_delete_not_found(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = []
    mock_client.table.return_value.delete.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(TwinNotFoundError):
        await repo.delete(uuid4())
