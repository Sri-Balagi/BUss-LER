"""Unit tests for Snapshot and History repositories."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.models.exceptions import RepositoryError
from app.repositories.history_repository import HistoryRepository
from app.repositories.snapshot_repository import SnapshotRepository


@pytest.fixture
def snapshot_repo(mock_supabase_client):
    return SnapshotRepository(mock_supabase_client)


@pytest.fixture
def history_repo(mock_supabase_client):
    return HistoryRepository(mock_supabase_client)


# =====================================================================
# SnapshotRepository Tests
# =====================================================================


@pytest.mark.asyncio
async def test_snapshot_repository_create_success(snapshot_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_data = {
        "id": str(uuid4()),
        "twin_id": str(twin_id),
        "snapshot_data": {"state": {"key": "val"}},
        "change_reason": None,
        "twin_version": 1,
        "created_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])

    snapshot = await snapshot_repo.create(twin_id, {"key": "val"}, 1)
    assert snapshot.twin_id == twin_id
    assert snapshot.twin_version == 1


@pytest.mark.asyncio
async def test_snapshot_repository_create_error(snapshot_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.side_effect = Exception("DB Error")
    with pytest.raises(RepositoryError):
        await snapshot_repo.create(uuid4(), {}, 1)


@pytest.mark.asyncio
async def test_snapshot_repository_list_success(snapshot_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_data = [
        {
            "id": str(uuid4()),
            "twin_id": str(twin_id),
            "snapshot_data": {},
            "change_reason": None,
            "twin_version": i,
            "created_at": "2026-06-25T00:00:00Z",
        }
        for i in range(1, 4)
    ]
    mock_execute = AsyncMock(data=mock_data)
    mock_execute.count = 3
    mock_supabase_client.table.return_value.execute.return_value = mock_execute

    items, total = await snapshot_repo.list_by_twin_id(twin_id, limit=3, offset=0)
    assert len(items) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_snapshot_repository_list_error(snapshot_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.side_effect = Exception("DB Error")
    with pytest.raises(RepositoryError):
        await snapshot_repo.list_by_twin_id(uuid4(), limit=10, offset=0)


# =====================================================================
# HistoryRepository Tests
# =====================================================================

from app.models.twin import ChangeType


@pytest.mark.asyncio
async def test_history_repository_create_success(history_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_data = {
        "id": str(uuid4()),
        "twin_id": str(twin_id),
        "change_type": "update",
        "change_summary": None,
        "changed_fields": [],
        "changed_by": "system",
        "old_values": None,
        "new_values": {"k": "v"},
        "twin_version": 2,
        "created_at": "2026-06-25T00:00:00Z",
    }
    mock_supabase_client.table.return_value.execute.return_value = AsyncMock(data=[mock_data])

    history = await history_repo.create(
        twin_id, 2, ChangeType.UPDATE, changed_by="system", new_values={"k": "v"}
    )
    assert history.twin_id == twin_id
    assert history.twin_version == 2


@pytest.mark.asyncio
async def test_history_repository_create_error(history_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.side_effect = Exception("DB Error")
    with pytest.raises(RepositoryError):
        await history_repo.create(uuid4(), 1, ChangeType.UPDATE, changed_by="system", new_values={})


@pytest.mark.asyncio
async def test_history_repository_list_success(history_repo, mock_supabase_client):
    twin_id = uuid4()
    mock_data = [
        {
            "id": str(uuid4()),
            "twin_id": str(twin_id),
            "change_type": "update",
            "changed_by": "system",
            "change_summary": None,
            "changed_fields": [],
            "old_values": None,
            "new_values": None,
            "twin_version": i,
            "created_at": "2026-06-25T00:00:00Z",
        }
        for i in range(1, 4)
    ]
    mock_execute = AsyncMock(data=mock_data)
    mock_execute.count = 3
    mock_supabase_client.table.return_value.execute.return_value = mock_execute

    items, total = await history_repo.list_by_twin_id(twin_id, limit=3, offset=0)
    assert len(items) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_history_repository_list_error(history_repo, mock_supabase_client):
    mock_supabase_client.table.return_value.execute.side_effect = Exception("DB Error")
    with pytest.raises(RepositoryError):
        await history_repo.list_by_twin_id(uuid4(), limit=10, offset=0)
