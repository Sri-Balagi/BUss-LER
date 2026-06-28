import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.intent import Intent, IntentCreate, IntentUpdate, IntentAnalysis
from app.models.enums import IntentStatus, IntentType, IntentConfidence
from app.models.exceptions import IntentNotFoundError, RepositoryError
from app.repositories.intent_repository import IntentRepository

@pytest.fixture
def mock_supabase_client():
    return MagicMock()

@pytest.fixture
def repository(mock_supabase_client):
    return IntentRepository(mock_supabase_client)

def test_deserialize():
    row = {
        "id": str(uuid.uuid4()),
        "twin_id": str(uuid.uuid4()),
        "raw_text": "hello",
        "intent_type": IntentType.GENERAL.value,
        "status": IntentStatus.PENDING.value,
        "analysis": {"intent_type": "general", "business_domain": "HR", "confidence": "high", "entities": []},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    intent = IntentRepository._deserialize(row)
    assert isinstance(intent, Intent)
    assert intent.analysis.business_domain == "HR"

@pytest.mark.asyncio
async def test_create_success(repository, mock_supabase_client):
    intent_id = uuid.uuid4()
    twin_id = uuid.uuid4()
    
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[{
        "id": str(intent_id),
        "twin_id": str(twin_id),
        "raw_text": "Test",
        "intent_type": IntentType.GENERAL.value,
        "status": IntentStatus.PENDING.value,
        "title": "Title",
        "analysis": {"intent_type": "general", "business_domain": "HR", "confidence": "high", "entities": []},
        "metadata": {"test": True},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }])
    mock_supabase_client.table().insert().execute = mock_execute
    
    data = IntentCreate(
        raw_text="Test",
        intent_type=IntentType.GENERAL,
        status=IntentStatus.PENDING,
        title="Title",
        analysis=IntentAnalysis(intent_type=IntentType.GENERAL, business_domain="HR", confidence=IntentConfidence.HIGH, entities=[]),
        metadata={"test": True}
    )
    
    result = await repository.create(twin_id, data)
    assert result.id == intent_id
    assert result.title == "Title"

@pytest.mark.asyncio
async def test_create_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().insert().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.create(uuid.uuid4(), IntentCreate(raw_text="Test", intent_type=IntentType.GENERAL, status=IntentStatus.PENDING))

@pytest.mark.asyncio
async def test_get_by_id_success(repository, mock_supabase_client):
    intent_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[{
        "id": str(intent_id),
        "twin_id": str(uuid.uuid4()),
        "raw_text": "Test",
        "intent_type": IntentType.GENERAL.value,
        "status": IntentStatus.PENDING.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }])
    mock_supabase_client.table().select().eq().execute = mock_execute
    
    result = await repository.get_by_id(intent_id)
    assert result.id == intent_id

@pytest.mark.asyncio
async def test_get_by_id_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[])
    mock_supabase_client.table().select().eq().execute = mock_execute
    
    with pytest.raises(IntentNotFoundError):
        await repository.get_by_id(uuid.uuid4())

@pytest.mark.asyncio
async def test_get_by_id_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.get_by_id(uuid.uuid4())

@pytest.mark.asyncio
async def test_list_by_twin_success(repository, mock_supabase_client):
    twin_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(
        data=[{
            "id": str(uuid.uuid4()),
            "twin_id": str(twin_id),
            "raw_text": "Test",
            "intent_type": IntentType.GENERAL.value,
            "status": IntentStatus.FULFILLED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }],
        count=1
    )
    
    mock_query = MagicMock()
    mock_query.execute = mock_execute
    mock_query.eq.return_value = mock_query
    mock_query.is_.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.range.return_value = mock_query
    
    mock_supabase_client.table().select().eq.return_value = mock_query
    
    result = await repository.list_by_twin(
        twin_id, 
        status=IntentStatus.FULFILLED, 
        intent_type=IntentType.GENERAL,
        include_deleted=False
    )
    assert result.total_count == 1
    assert len(result.items) == 1

@pytest.mark.asyncio
async def test_list_by_twin_failure(repository, mock_supabase_client):
    mock_query = MagicMock()
    mock_query.execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().eq.return_value = mock_query
    with pytest.raises(RepositoryError):
        await repository.list_by_twin(uuid.uuid4(), include_deleted=True)

@pytest.mark.asyncio
async def test_update_success(repository, mock_supabase_client):
    intent_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[{
        "id": str(intent_id),
        "twin_id": str(uuid.uuid4()),
        "raw_text": "Updated",
        "intent_type": IntentType.GENERAL.value,
        "status": IntentStatus.FULFILLED.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }])
    mock_supabase_client.table().update().eq().execute = mock_execute
    
    now = datetime.now(timezone.utc)
    update = IntentUpdate(
        status=IntentStatus.FULFILLED,
        intent_type=IntentType.GENERAL,
        analysis=IntentAnalysis(intent_type=IntentType.GENERAL, business_domain="HR", confidence=IntentConfidence.HIGH, entities=[]),
        classified_at=now,
        fulfilled_at=now
    )
    result = await repository.update(intent_id, update)
    assert result.status == IntentStatus.FULFILLED

@pytest.mark.asyncio
async def test_update_empty(repository, mock_supabase_client):
    intent_id = uuid.uuid4()
    
    mock_get = AsyncMock()
    mock_get.return_value = MagicMock(data=[{
        "id": str(intent_id),
        "twin_id": str(uuid.uuid4()),
        "raw_text": "Test",
        "intent_type": IntentType.GENERAL.value,
        "status": IntentStatus.PENDING.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }])
    mock_supabase_client.table().select().eq().execute = mock_get
    
    result = await repository.update(intent_id, IntentUpdate())
    assert str(result.id) == str(intent_id)

@pytest.mark.asyncio
async def test_update_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[])
    mock_supabase_client.table().update().eq().execute = mock_execute
    with pytest.raises(IntentNotFoundError):
        await repository.update(uuid.uuid4(), IntentUpdate(status=IntentStatus.FULFILLED))

@pytest.mark.asyncio
async def test_update_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().update().eq().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.update(uuid.uuid4(), IntentUpdate(status=IntentStatus.FULFILLED))

@pytest.mark.asyncio
async def test_soft_delete_success(repository, mock_supabase_client):
    intent_id = uuid.uuid4()
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[{"id": str(intent_id)}])
    mock_supabase_client.table().update().eq().is_().execute = mock_execute
    
    await repository.soft_delete(intent_id)

@pytest.mark.asyncio
async def test_soft_delete_not_found(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_execute.return_value = MagicMock(data=[])
    mock_supabase_client.table().update().eq().is_().execute = mock_execute
    with pytest.raises(IntentNotFoundError):
        await repository.soft_delete(uuid.uuid4())

@pytest.mark.asyncio
async def test_soft_delete_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().update().eq().is_().execute = mock_execute
    with pytest.raises(RepositoryError):
        await repository.soft_delete(uuid.uuid4())

@pytest.mark.asyncio
async def test_health_check_success(repository, mock_supabase_client):
    mock_execute = AsyncMock()
    mock_supabase_client.table().select().limit().execute = mock_execute
    
    health = await repository.health_check()
    assert health["status"] == "healthy"

@pytest.mark.asyncio
async def test_health_check_failure(repository, mock_supabase_client):
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase_client.table().select().limit().execute = mock_execute
    
    health = await repository.health_check()
    assert health["status"] == "unhealthy"
    assert "DB Error" in health["detail"]
