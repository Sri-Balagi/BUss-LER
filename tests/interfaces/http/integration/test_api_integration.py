from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.bootstrap.container import reset_container_for_testing
from app.main import app


@pytest.fixture(autouse=True)
def reset_container():
    """Ensure container is reset between tests so it rebuilds cleanly during lifespan."""
    reset_container_for_testing()
    yield
    reset_container_for_testing()


@patch("app.main.SupabaseService.get_client", new_callable=AsyncMock)
@patch("app.main.QdrantService.initialize_collections", new_callable=AsyncMock)
@patch("app.main.QdrantService.get_client")
@patch("app.main.QdrantService.close", new_callable=AsyncMock)
def test_health_check_endpoint(mock_close, mock_qdrant_get, mock_qdrant_init, mock_supabase):
    """Verify that the FastAPI app boots and the DI container builds successfully."""
    mock_qdrant_get.return_value = AsyncMock()
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@patch("app.main.SupabaseService.get_client", new_callable=AsyncMock)
@patch("app.main.QdrantService.initialize_collections", new_callable=AsyncMock)
@patch("app.main.QdrantService.get_client")
@patch("app.main.QdrantService.close", new_callable=AsyncMock)
@patch("app.infrastructure.ai.kernel.AIKernel.health_check", new_callable=AsyncMock)
def test_ai_health_check_endpoint(
    mock_health, mock_close, mock_qdrant_get, mock_qdrant_init, mock_supabase
):
    """Verify that the AI Platform dependencies resolve correctly from the DI container."""
    mock_qdrant_get.return_value = AsyncMock()
    mock_health.return_value = {"status": "ok", "providers": {"gemini": {"status": "healthy"}}}
    with TestClient(app) as client:
        response = client.get("/api/v1/health/ai")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
