"""Global pytest fixtures."""

from unittest.mock import AsyncMock

import pytest
from app.api.v1.dependencies import (
    get_entity_repository,
    get_entity_service,
    get_history_repository,
    get_snapshot_repository,
    get_supabase_client,
    get_twin_repository,
    get_twin_service,
)
from app.services.supabase import SupabaseService
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singletons so each async test gets a client bound to its own event loop."""
    SupabaseService.reset()


@pytest.fixture(autouse=True)
def mock_qdrant_init(monkeypatch):
    """Mock QdrantService.initialize_collections to prevent real connection attempts during tests."""
    from app.services.qdrant import QdrantService

    async def mock_init(*args, **kwargs):
        pass

    monkeypatch.setattr(QdrantService, "initialize_collections", mock_init)


from unittest.mock import Mock  # noqa: E402


@pytest.fixture
def mock_supabase_client():
    """Returns a mocked Supabase AsyncClient."""
    mock = Mock()

    # Create a builder mock that uses AsyncMock for execute
    builder = Mock()
    mock_execute = AsyncMock()
    builder.select.return_value = builder
    builder.insert.return_value = builder
    builder.update.return_value = builder
    builder.delete.return_value = builder
    builder.eq.return_value = builder
    builder.order.return_value = builder
    builder.range.return_value = builder
    builder.limit.return_value = builder
    builder.execute = mock_execute

    # Route table and rpc calls to the builder
    mock.table.return_value = builder
    mock.rpc.return_value = builder

    return mock


@pytest.fixture
def mock_entity_repo(mock_supabase_client):
    return AsyncMock()


@pytest.fixture
def mock_twin_repo(mock_supabase_client):
    return AsyncMock()


@pytest.fixture
def mock_snapshot_repo(mock_supabase_client):
    return AsyncMock()


@pytest.fixture
def mock_history_repo(mock_supabase_client):
    return AsyncMock()


@pytest.fixture
def mock_entity_service():
    return AsyncMock()


@pytest.fixture
def mock_twin_service():
    return AsyncMock()


@pytest.fixture
def client(
    mock_supabase_client,
    mock_entity_repo,
    mock_twin_repo,
    mock_snapshot_repo,
    mock_history_repo,
    mock_entity_service,
    mock_twin_service,
):
    """Test client with all dependencies mocked for isolated API testing."""
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase_client
    app.dependency_overrides[get_entity_repository] = lambda: mock_entity_repo
    app.dependency_overrides[get_twin_repository] = lambda: mock_twin_repo
    app.dependency_overrides[get_snapshot_repository] = lambda: mock_snapshot_repo
    app.dependency_overrides[get_history_repository] = lambda: mock_history_repo
    app.dependency_overrides[get_entity_service] = lambda: mock_entity_service
    app.dependency_overrides[get_twin_service] = lambda: mock_twin_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def unmocked_client():
    """Test client without overrides, for integration testing."""
    with TestClient(app) as test_client:
        yield test_client
