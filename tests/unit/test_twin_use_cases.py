import uuid
from unittest.mock import AsyncMock

import pytest

from app.application.twin.create_twin import CreateTwinUseCase
from app.application.twin.get_twin import GetTwinUseCase
from app.interfaces.http.schemas.base import Entity
from app.interfaces.http.schemas.twin import DigitalTwin, DigitalTwinCreate
from app.shared.enums import EntityType


@pytest.fixture
def mock_twin_repo():
    return AsyncMock()


@pytest.fixture
def mock_entity_repo():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_twin_use_case(mock_twin_repo, mock_entity_repo):
    use_case = CreateTwinUseCase(repository=mock_twin_repo, entity_repository=mock_entity_repo)
    entity_id = uuid.uuid4()
    twin_id = uuid.uuid4()

    mock_entity = Entity(
        id=entity_id,
        user_id=uuid.uuid4(),
        name="Test Entity",
        entity_type=EntityType.INDIVIDUAL,
        description=None,
        metadata={},
        is_active=True,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_entity_repo.get_by_id.return_value = mock_entity

    mock_twin = DigitalTwin(
        id=twin_id,
        entity_id=entity_id,
        state={},
        metadata={"schema_version": 1},
        twin_version=1,
        last_snapshot_at=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_twin_repo.create.return_value = mock_twin

    data = DigitalTwinCreate(entity_id=entity_id)
    result = await use_case.execute(data=data)

    assert result.id == twin_id
    mock_entity_repo.get_by_id.assert_called_once_with(entity_id)
    mock_twin_repo.create.assert_called_once_with(data)


@pytest.mark.asyncio
async def test_get_twin_use_case(mock_twin_repo):
    use_case = GetTwinUseCase(repository=mock_twin_repo)
    twin_id = uuid.uuid4()
    entity_id = uuid.uuid4()

    mock_twin = DigitalTwin(
        id=twin_id,
        entity_id=entity_id,
        state={},
        metadata={"schema_version": 1},
        twin_version=1,
        last_snapshot_at=None,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_twin_repo.get_by_id.return_value = mock_twin

    result = await use_case.execute(twin_id=twin_id)

    assert result.id == twin_id
    mock_twin_repo.get_by_id.assert_called_once_with(twin_id)
