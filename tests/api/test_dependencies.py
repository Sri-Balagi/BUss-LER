import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID

from fastapi import Request, BackgroundTasks

from app.api.v1.dependencies import (
    get_supabase_client,
    get_qdrant_client,
    get_current_user,
    get_operation_context,
    check_rate_limit,
    audit_log_request,
    get_entity_repository,
    get_twin_repository,
    get_snapshot_repository,
    get_history_repository,
    get_memory_metadata_repository,
    get_memory_vector_repository,
    get_event_bus,
    get_twin_service,
    get_entity_service,
    get_ai_kernel,
    get_memory_service
)
from app.config import Settings
from app.core.context import OperationContext

@pytest.fixture
def mock_settings():
    return Settings(
        supabase_url="http://test", 
        supabase_key="test",
        qdrant_host="test",
        qdrant_port=6333,
        gemini_api_key="test"
    )

@pytest.mark.asyncio
async def test_get_supabase_client(mock_settings):
    with patch("app.services.supabase.SupabaseService.get_client", new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = "supabase_client"
        client = await get_supabase_client(mock_settings)
        assert client == "supabase_client"
        mock_get_client.assert_called_once_with(mock_settings)

@pytest.mark.asyncio
async def test_get_qdrant_client(mock_settings):
    with patch("app.services.qdrant.QdrantService.get_client", new_callable=Mock) as mock_get_client:
        mock_get_client.return_value = "qdrant_client"
        client = await get_qdrant_client(mock_settings)
        assert client == "qdrant_client"
        mock_get_client.assert_called_once_with(mock_settings)

@pytest.mark.asyncio
async def test_get_current_user():
    user_id = await get_current_user()
    assert isinstance(user_id, UUID)
    assert str(user_id) == "00000000-0000-0000-0000-000000000000"

@pytest.mark.asyncio
async def test_get_operation_context():
    request = MagicMock(spec=Request)
    request.headers = {"X-Correlation-ID": "test-corr-id"}
    request.state = MagicMock()
    
    user_id = UUID("00000000-0000-0000-0000-000000000000")
    
    ctx = await get_operation_context(request, user_id)
    assert isinstance(ctx, OperationContext)
    assert ctx.correlation_id == "test-corr-id"
    assert ctx.user_id == user_id
    assert hasattr(request.state, "request_id")
    assert ctx.request_id == request.state.request_id

@pytest.mark.asyncio
async def test_hooks():
    request = MagicMock(spec=Request)
    # Just ensure they don't crash
    await check_rate_limit(request)
    await audit_log_request(request)

@pytest.mark.asyncio
async def test_repositories(mock_settings):
    client = MagicMock()
    
    entity_repo = await get_entity_repository(client)
    assert entity_repo is not None
    
    twin_repo = await get_twin_repository(client)
    assert twin_repo is not None
    
    snapshot_repo = await get_snapshot_repository(client)
    assert snapshot_repo is not None
    
    history_repo = await get_history_repository(client)
    assert history_repo is not None
    
    memory_meta_repo = await get_memory_metadata_repository(client)
    assert memory_meta_repo is not None
    
    memory_vec_repo = await get_memory_vector_repository(client, mock_settings)
    assert memory_vec_repo is not None

@pytest.mark.asyncio
async def test_get_event_bus():
    bg_tasks = BackgroundTasks()
    bus = await get_event_bus(bg_tasks)
    assert bus is not None

@pytest.mark.asyncio
async def test_services():
    twin_repo = MagicMock()
    snap_repo = MagicMock()
    hist_repo = MagicMock()
    entity_repo = MagicMock()
    
    twin_svc = await get_twin_service(twin_repo, snap_repo, hist_repo, entity_repo)
    assert twin_svc is not None
    
    entity_svc = await get_entity_service(entity_repo)
    assert entity_svc is not None

@pytest.mark.asyncio
async def test_get_ai_kernel(mock_settings):
    kernel = await get_ai_kernel(mock_settings)
    assert kernel is not None

@pytest.mark.asyncio
async def test_get_memory_service():
    meta_repo = MagicMock()
    vec_repo = MagicMock()
    kernel = MagicMock()
    bus = MagicMock()
    
    mem_svc = await get_memory_service(meta_repo, vec_repo, kernel, bus)
    assert mem_svc is not None
    bus.subscribe.assert_called_once()
