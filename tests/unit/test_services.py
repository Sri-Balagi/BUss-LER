"""Unit tests for services including all edge cases."""

from uuid import uuid4
import pytest
from unittest.mock import AsyncMock

from app.models.enums import EntityType
from app.models.exceptions import EntityNotFoundError, ServiceError, RepositoryError, TwinNotFoundError, VersionConflictError
from app.models.schemas import Entity, EntityCreate
from app.models.entity import EntityUpdate
from app.models.twin import DigitalTwin, DigitalTwinCreate, DigitalTwinUpdate, TwinMetadata
from app.services.entity_service import EntityService
from app.services.twin_service import TwinService


@pytest.fixture
def entity_service(mock_entity_repo):
    return EntityService(mock_entity_repo)


@pytest.fixture
def twin_service(mock_twin_repo, mock_snapshot_repo, mock_history_repo, mock_entity_repo):
    return TwinService(mock_twin_repo, mock_snapshot_repo, mock_history_repo, mock_entity_repo)


# =====================================================================
# EntityService Tests
# =====================================================================

@pytest.mark.asyncio
async def test_entity_service_create_success(entity_service, mock_entity_repo):
    user_id = uuid4()
    mock_entity = Entity(id=uuid4(), user_id=user_id, name="Test", entity_type=EntityType.STARTUP, metadata={}, is_active=True, created_at="2026-06-25T00:00:00Z", updated_at="2026-06-25T00:00:00Z", description=None)
    mock_entity_repo.create.return_value = mock_entity
    
    data = EntityCreate(name="Test", entity_type=EntityType.STARTUP)
    entity = await entity_service.create_entity(user_id, data)
    assert entity.id == mock_entity.id
    mock_entity_repo.create.assert_called_once_with(user_id, data)

@pytest.mark.asyncio
async def test_entity_service_create_repository_failure(entity_service, mock_entity_repo):
    user_id = uuid4()
    mock_entity_repo.create.side_effect = RepositoryError("entity.create", "DB Error")
    data = EntityCreate(name="Test", entity_type=EntityType.STARTUP)
    with pytest.raises(RepositoryError):
        await entity_service.create_entity(user_id, data)

@pytest.mark.asyncio
async def test_entity_service_get_by_id_active(entity_service, mock_entity_repo):
    entity_id = uuid4()
    mock_entity = Entity(id=entity_id, user_id=uuid4(), name="Test", entity_type=EntityType.STARTUP, metadata={}, is_active=True, created_at="2026-06-25T00:00:00Z", updated_at="2026-06-25T00:00:00Z", description=None)
    mock_entity_repo.get_by_id.return_value = mock_entity
    
    entity = await entity_service.get_by_id(entity_id)
    assert entity.id == entity_id

@pytest.mark.asyncio
async def test_entity_service_get_by_id_inactive_raises(entity_service, mock_entity_repo):
    entity_id = uuid4()
    mock_entity = Entity(id=entity_id, user_id=uuid4(), name="Test", entity_type=EntityType.STARTUP, metadata={}, is_active=False, created_at="2026-06-25T00:00:00Z", updated_at="2026-06-25T00:00:00Z", description=None)
    mock_entity_repo.get_by_id.return_value = mock_entity
    
    with pytest.raises(EntityNotFoundError):
        await entity_service.get_by_id(entity_id)

@pytest.mark.asyncio
async def test_entity_service_update_invalid(entity_service, mock_entity_repo):
    # Updating an entity that doesn't exist raises EntityNotFoundError
    entity_id = uuid4()
    mock_entity_repo.update.side_effect = EntityNotFoundError(str(entity_id))
    data = EntityUpdate(name="New Name")
    with pytest.raises(EntityNotFoundError):
        await entity_service.update(entity_id, data)

@pytest.mark.asyncio
async def test_entity_service_delete_nonexistent(entity_service, mock_entity_repo):
    entity_id = uuid4()
    mock_entity_repo.soft_delete.side_effect = EntityNotFoundError(str(entity_id))
    with pytest.raises(EntityNotFoundError):
        await entity_service.delete(entity_id)


# =====================================================================
# TwinService Tests
# =====================================================================

@pytest.mark.asyncio
async def test_twin_service_create_twin_success(twin_service, mock_twin_repo, mock_snapshot_repo, mock_history_repo, mock_entity_repo):
    entity_id = uuid4()
    mock_entity_repo.get_by_id.return_value = AsyncMock()
    
    mock_twin = DigitalTwin(id=uuid4(), entity_id=entity_id, state={"key": "val"}, metadata=TwinMetadata(), twin_version=1, last_snapshot_at=None, created_at="2026-06-25T00:00:00Z", updated_at="2026-06-25T00:00:00Z")
    mock_twin_repo.create.return_value = mock_twin
    
    data = DigitalTwinCreate(entity_id=entity_id, state={"key": "val"})
    twin = await twin_service.create_twin(data)
    
    mock_entity_repo.get_by_id.assert_called_once_with(entity_id)
    mock_twin_repo.create.assert_called_once_with(data)
    mock_snapshot_repo.create.assert_called_once()
    mock_history_repo.create.assert_called_once()
    assert twin.id == mock_twin.id

@pytest.mark.asyncio
async def test_twin_service_create_entity_validation_failure(twin_service, mock_entity_repo):
    entity_id = uuid4()
    mock_entity_repo.get_by_id.side_effect = EntityNotFoundError(str(entity_id))
    data = DigitalTwinCreate(entity_id=entity_id, state={"key": "val"})
    
    with pytest.raises(EntityNotFoundError):
        await twin_service.create_twin(data)

@pytest.mark.asyncio
async def test_twin_service_create_snapshot_failure_rollback(twin_service, mock_twin_repo, mock_snapshot_repo, mock_entity_repo):
    entity_id = uuid4()
    mock_entity_repo.get_by_id.return_value = AsyncMock()
    mock_twin = DigitalTwin(id=uuid4(), entity_id=entity_id, state={"key": "val"}, metadata=TwinMetadata(), twin_version=1, last_snapshot_at=None, created_at="2026-06-25T00:00:00Z", updated_at="2026-06-25T00:00:00Z")
    mock_twin_repo.create.return_value = mock_twin
    
    # Snapshot creation fails!
    mock_snapshot_repo.create.side_effect = RepositoryError("snapshot.create", "DB Error")
    
    data = DigitalTwinCreate(entity_id=entity_id, state={"key": "val"})
    with pytest.raises(ServiceError) as exc_info:
        await twin_service.create_twin(data)
        
    assert "Rolled back" in exc_info.value.detail
    # Rollback assertion
    mock_twin_repo.delete.assert_called_once_with(mock_twin.id)

@pytest.mark.asyncio
async def test_twin_service_create_history_failure_rollback(twin_service, mock_twin_repo, mock_snapshot_repo, mock_history_repo, mock_entity_repo):
    entity_id = uuid4()
    mock_entity_repo.get_by_id.return_value = AsyncMock()
    mock_twin = DigitalTwin(id=uuid4(), entity_id=entity_id, state={"key": "val"}, metadata=TwinMetadata(), twin_version=1, last_snapshot_at=None, created_at="2026-06-25T00:00:00Z", updated_at="2026-06-25T00:00:00Z")
    mock_twin_repo.create.return_value = mock_twin
    mock_snapshot_repo.create.return_value = AsyncMock()
    
    # History creation fails!
    mock_history_repo.create.side_effect = RepositoryError("history.create", "DB Error")
    
    data = DigitalTwinCreate(entity_id=entity_id, state={"key": "val"})
    with pytest.raises(ServiceError) as exc_info:
        await twin_service.create_twin(data)
        
    assert "Rolled back" in exc_info.value.detail
    # Rollback assertion
    mock_twin_repo.delete.assert_called_once_with(mock_twin.id)

@pytest.mark.asyncio
async def test_twin_service_update_failure(twin_service, mock_twin_repo):
    twin_id = uuid4()
    mock_twin_repo.update_with_snapshot.side_effect = TwinNotFoundError(str(twin_id))
    data = DigitalTwinUpdate(state={"new": "val"}, expected_version=1)
    
    with pytest.raises(TwinNotFoundError):
        await twin_service.update_twin(twin_id, data)

@pytest.mark.asyncio
async def test_twin_service_update_optimistic_concurrency_failure(twin_service, mock_twin_repo):
    twin_id = uuid4()
    mock_twin_repo.update_with_snapshot.side_effect = VersionConflictError(1, 2)
    data = DigitalTwinUpdate(state={"new": "val"}, expected_version=1)
    
    with pytest.raises(VersionConflictError):
        await twin_service.update_twin(twin_id, data)

@pytest.mark.asyncio
async def test_twin_service_delete_success(twin_service, mock_twin_repo):
    twin_id = uuid4()
    mock_twin_repo.get_by_id.return_value = AsyncMock()
    await twin_service.delete(twin_id)
    mock_twin_repo.delete.assert_called_once_with(twin_id)

@pytest.mark.asyncio
async def test_twin_service_delete_failure(twin_service, mock_twin_repo):
    twin_id = uuid4()
    mock_twin_repo.get_by_id.side_effect = TwinNotFoundError(str(twin_id))
    with pytest.raises(TwinNotFoundError):
        await twin_service.delete(twin_id)

@pytest.mark.asyncio
async def test_twin_service_get_snapshots_twin_not_found(twin_service, mock_twin_repo):
    twin_id = uuid4()
    mock_twin_repo.get_by_id.side_effect = TwinNotFoundError(str(twin_id))
    with pytest.raises(TwinNotFoundError):
        await twin_service.get_snapshots(twin_id)

@pytest.mark.asyncio
async def test_twin_service_get_history_twin_not_found(twin_service, mock_twin_repo):
    twin_id = uuid4()
    mock_twin_repo.get_by_id.side_effect = TwinNotFoundError(str(twin_id))
    with pytest.raises(TwinNotFoundError):
        await twin_service.get_history(twin_id)
