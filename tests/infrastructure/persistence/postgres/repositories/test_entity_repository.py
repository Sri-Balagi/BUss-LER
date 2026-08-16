from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.infrastructure.persistence.postgres.repositories.entity_repository import EntityRepository
from app.interfaces.http.schemas.base import EntityCreate
from app.interfaces.http.schemas.entity import EntityUpdate
from app.shared.enums import EntityType
from app.shared.exceptions.errors import EntityNotFoundError, RepositoryError


@pytest.fixture
def mock_client():
    client = MagicMock()
    return client

@pytest.fixture
def repo(mock_client):
    return EntityRepository(mock_client)

@pytest.mark.asyncio
async def test_create_success(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = [{"id": str(uuid4()), "user_id": str(uuid4()), "name": "Test", "entity_type": "organization", "description": "", "metadata": {}, "is_active": True, "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_client.table.return_value.insert.return_value.execute = mock_execute

    data = EntityCreate(name="Test", entity_type=EntityType.ORGANIZATION)
    result = await repo.create(uuid4(), data)
    assert result is not None
    assert mock_execute.called

@pytest.mark.asyncio
async def test_create_error(repo, mock_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_client.table.return_value.insert.return_value.execute = mock_execute

    data = EntityCreate(name="Test", entity_type=EntityType.ORGANIZATION)
    with pytest.raises(RepositoryError):
        await repo.create(uuid4(), data)

@pytest.mark.asyncio
async def test_get_by_id_success(repo, mock_client):
    mock_execute = AsyncMock()
    entity_id = str(uuid4())
    mock_execute.return_value.data = [{"id": entity_id, "user_id": str(uuid4()), "name": "Test", "entity_type": "organization", "description": "", "metadata": {}, "is_active": True, "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    result = await repo.get_by_id(uuid4())
    assert str(result.id) == entity_id

@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = []
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(EntityNotFoundError):
        await repo.get_by_id(uuid4())

@pytest.mark.asyncio
async def test_list_success(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = [{"id": str(uuid4()), "user_id": str(uuid4()), "name": "Test", "entity_type": "organization", "description": "", "metadata": {}, "is_active": True, "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_execute.return_value.count = 1
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute = mock_execute

    items, total = await repo.list(user_id=uuid4(), is_active=True)
    assert len(items) == 1
    assert total == 1

@pytest.mark.asyncio
async def test_update_success(repo, mock_client):
    mock_execute = AsyncMock()
    entity_id = str(uuid4())
    mock_execute.return_value.data = [{"id": entity_id, "user_id": str(uuid4()), "name": "Test Updated", "entity_type": "organization", "description": "", "metadata": {}, "is_active": True, "created_at": "2026-07-23T00:00:00Z", "updated_at": "2026-07-23T00:00:00Z"}]
    mock_client.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    update_data = EntityUpdate(name="Test Updated")
    result = await repo.update(uuid4(), update_data)
    assert result.name == "Test Updated"

@pytest.mark.asyncio
async def test_update_not_found(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = []
    mock_client.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    update_data = EntityUpdate(name="Test Updated")
    with pytest.raises(EntityNotFoundError):
        await repo.update(uuid4(), update_data)

@pytest.mark.asyncio
async def test_soft_delete_success(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = [{"id": str(uuid4())}]
    mock_client.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    await repo.soft_delete(uuid4())
    assert mock_execute.called

@pytest.mark.asyncio
async def test_soft_delete_not_found(repo, mock_client):
    mock_execute = AsyncMock()
    mock_execute.return_value.data = []
    mock_client.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    with pytest.raises(EntityNotFoundError):
        await repo.soft_delete(uuid4())
