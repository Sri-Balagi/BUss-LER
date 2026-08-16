from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.infrastructure.persistence.postgres.repositories.snapshot_repository import (
    SnapshotRepository,
)
from app.interfaces.http.schemas.twin import TwinSnapshot
from app.shared.exceptions.errors import RepositoryError


@pytest.fixture
def mock_client():
    from unittest.mock import MagicMock
    client = MagicMock()
    client.table.return_value.insert.return_value.execute = AsyncMock()
    client.table.return_value.select.return_value.eq.return_value.execute = AsyncMock()
    client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute = AsyncMock()
    return client

@pytest.fixture
def repo(mock_client):
    return SnapshotRepository(mock_client)

@pytest.mark.asyncio
async def test_create_snapshot(repo, mock_client):
    twin_id = uuid4()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "twin_id": str(twin_id),
        "twin_version": 1,
        "snapshot_data": {"test": "data"},
        "change_reason": "test",
        "created_at": "2023-01-01T00:00:00Z"
    }]

    result = await repo.create(
        twin_id=twin_id,
        twin_version=1,
        snapshot_data={"test": "data"},
        change_reason="test"
    )

    assert isinstance(result, TwinSnapshot)
    mock_client.table.assert_called_with("twin_snapshots")
    mock_client.table.return_value.insert.assert_called_once()

@pytest.mark.asyncio
async def test_create_snapshot_error(repo, mock_client):
    mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB error")

    with pytest.raises(RepositoryError):
        await repo.create(uuid4(), 1, {})

@pytest.mark.asyncio
async def test_get_by_id(repo, mock_client):
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "twin_id": str(uuid4()),
        "twin_version": 1,
        "snapshot_data": {},
        "change_reason": "test",
        "created_at": "2023-01-01T00:00:00Z"
    }]

    result = await repo.get_by_id(uuid4())
    assert isinstance(result, TwinSnapshot)

@pytest.mark.asyncio
async def test_get_by_id_none(repo, mock_client):
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    result = await repo.get_by_id(uuid4())
    assert result is None

@pytest.mark.asyncio
async def test_get_by_id_error(repo, mock_client):
    mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("DB error")

    with pytest.raises(RepositoryError):
        await repo.get_by_id(uuid4())

@pytest.mark.asyncio
async def test_list_by_twin_id(repo, mock_client):
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "twin_id": str(uuid4()),
        "twin_version": 1,
        "snapshot_data": {},
        "change_reason": "test",
        "created_at": "2023-01-01T00:00:00Z"
    }]
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.count = 1

    results, count = await repo.list_by_twin_id(uuid4())
    assert count == 1
    assert len(results) == 1
    assert isinstance(results[0], TwinSnapshot)

@pytest.mark.asyncio
async def test_list_by_twin_id_error(repo, mock_client):
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = Exception("DB Error")

    with pytest.raises(RepositoryError):
        await repo.list_by_twin_id(uuid4())
