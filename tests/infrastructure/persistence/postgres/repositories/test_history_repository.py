from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.infrastructure.persistence.postgres.repositories.history_repository import (
    HistoryRepository,
)
from app.interfaces.http.schemas.twin import ChangeType, TwinHistory
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
    return HistoryRepository(mock_client)

@pytest.mark.asyncio
async def test_create_history(repo, mock_client):
    twin_id = uuid4()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "twin_id": str(twin_id),
        "twin_version": 1,
        "change_type": "create",
        "changed_fields": [],
        "change_summary": "test",
        "changed_by": "tester",
        "old_values": {"a": 1},
        "new_values": {"a": 2},
        "created_at": "2023-01-01T00:00:00Z"
    }]

    result = await repo.create(
        twin_id=twin_id,
        twin_version=1,
        change_type=ChangeType.CREATE,
        change_summary="test",
        changed_by="tester",
        old_values={"a": 1},
        new_values={"a": 2}
    )

    assert isinstance(result, TwinHistory)
    mock_client.table.assert_called_with("twin_history")
    mock_client.table.return_value.insert.assert_called_once()

    # check kwargs
    insert_args = mock_client.table.return_value.insert.call_args[0][0]
    assert insert_args["change_summary"] == "test"
    assert insert_args["changed_by"] == "tester"
    assert insert_args["old_values"] == {"a": 1}
    assert insert_args["new_values"] == {"a": 2}

@pytest.mark.asyncio
async def test_create_history_error(repo, mock_client):
    mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")

    with pytest.raises(RepositoryError):
        await repo.create(
            twin_id=uuid4(),
            twin_version=1,
            change_type=ChangeType.CREATE
        )

@pytest.mark.asyncio
async def test_list_by_twin_id(repo, mock_client):
    twin_id = uuid4()

    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "twin_id": str(twin_id),
        "twin_version": 1,
        "change_type": "create",
        "changed_fields": [],
        "change_summary": "test",
        "changed_by": "tester",
        "old_values": {"a": 1},
        "new_values": {"a": 2},
        "created_at": "2023-01-01T00:00:00Z"
    }]
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.count = 1

    results, count = await repo.list_by_twin_id(twin_id)

    assert count == 1
    assert len(results) == 1
    assert isinstance(results[0], TwinHistory)

@pytest.mark.asyncio
async def test_list_by_twin_id_error(repo, mock_client):
    mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = Exception("DB error")

    with pytest.raises(RepositoryError):
        await repo.list_by_twin_id(uuid4())
