import uuid
from unittest.mock import AsyncMock

import pytest

from app.application.entity.create_entity import CreateEntityUseCase
from app.application.entity.get_entity import GetEntityUseCase
from app.interfaces.http.schemas.base import Entity, EntityCreate
from app.shared.enums import EntityType


@pytest.fixture
def mock_entity_repo():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_entity_use_case(mock_entity_repo):
    use_case = CreateEntityUseCase(repository=mock_entity_repo)
    user_id = uuid.uuid4()
    entity_id = uuid.uuid4()

    mock_entity = Entity(
        id=entity_id,
        user_id=user_id,
        name="Test Entity",
        entity_type=EntityType.INDIVIDUAL,
        description=None,
        metadata={},
        is_active=True,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_entity_repo.create.return_value = mock_entity

    data = EntityCreate(name="Test Entity", entity_type=EntityType.INDIVIDUAL)
    result = await use_case.execute(user_id=user_id, data=data)

    assert result.id == entity_id
    mock_entity_repo.create.assert_called_once_with(user_id=user_id, data=data)


@pytest.mark.asyncio
async def test_get_entity_use_case(mock_entity_repo):
    use_case = GetEntityUseCase(repository=mock_entity_repo)
    user_id = uuid.uuid4()
    entity_id = uuid.uuid4()

    mock_entity = Entity(
        id=entity_id,
        user_id=user_id,
        name="Test Entity",
        entity_type=EntityType.INDIVIDUAL,
        description=None,
        metadata={},
        is_active=True,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )
    mock_entity_repo.get_by_id.return_value = mock_entity

    result = await use_case.execute(entity_id=entity_id)

    assert result.id == entity_id
    mock_entity_repo.get_by_id.assert_called_once_with(entity_id)
