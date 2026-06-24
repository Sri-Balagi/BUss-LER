"""Smoke tests for Milestone 0.

Verifies basic application health and configuration without requiring
a running database or external services.
"""

import os
from unittest import mock

import pytest
from httpx import AsyncClient, ASGITransport

from app.config import get_settings
from app.main import app
from app.services.qdrant import QdrantService
from app.services.supabase import SupabaseService


@pytest.fixture
def mock_qdrant_init():
    """Mocks Qdrant collection initialization to prevent network calls during testing."""
    with mock.patch("app.main.QdrantService.initialize_collections") as mock_init:
        yield mock_init


@pytest.fixture
def mock_env():
    """Sets up a mock environment for tests."""
    with mock.patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "http://localhost:8000",
            "SUPABASE_KEY": "test-key",
            "GEMINI_API_KEY": "test-gemini-key",
        },
    ):
        # Clear lru_cache to ensure we load the mocked environment
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()


def test_settings_loading(mock_env):
    """Verify settings can be loaded from the environment."""
    settings = get_settings()
    assert settings.supabase_url == "http://localhost:8000"
    assert settings.supabase_key == "test-key"
    assert settings.gemini_api_key == "test-gemini-key"
    assert settings.qdrant_host == "localhost"
    assert settings.qdrant_port == 6333


@pytest.mark.asyncio
async def test_health_check(mock_env, mock_qdrant_init):
    """Verify the health check endpoint returns 200 OK.
    
    Uses ASGITransport to test the FastAPI app directly, which triggers
    the lifespan context manager. mock_qdrant_init prevents network calls.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_supabase_service_init(mock_env):
    """Verify SupabaseService can instantiate the async client."""
    settings = get_settings()
    
    with mock.patch("app.services.supabase.create_async_client") as mock_create:
        SupabaseService.reset()
        await SupabaseService.get_client(settings)
        
        mock_create.assert_called_once_with(
            "http://localhost:8000",
            "test-key"
        )


def test_qdrant_service_init(mock_env):
    """Verify QdrantService can instantiate the client."""
    settings = get_settings()
    
    with mock.patch("app.services.qdrant.AsyncQdrantClient") as mock_client:
        QdrantService._instance = None  # Reset singleton
        QdrantService.get_client(settings)
        
        mock_client.assert_called_once_with(
            host="localhost",
            port=6333
        )
