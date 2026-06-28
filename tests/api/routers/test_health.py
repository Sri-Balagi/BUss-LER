import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app
from app.api.v1.dependencies import (
    get_memory_metadata_repository,
    get_memory_vector_repository,
    get_ai_kernel,
)


@pytest.fixture
def mock_metadata_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_vector_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_ai_kernel():
    kernel = AsyncMock()
    return kernel


@pytest.mark.asyncio
async def test_health_memory_all_healthy(mock_metadata_repo, mock_vector_repo, mock_ai_kernel):
    app.dependency_overrides[get_memory_metadata_repository] = lambda: mock_metadata_repo
    app.dependency_overrides[get_memory_vector_repository] = lambda: mock_vector_repo
    app.dependency_overrides[get_ai_kernel] = lambda: mock_ai_kernel

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health/memory")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "healthy" in data["subsystems"]["metadata_repository"]
    assert "healthy" in data["subsystems"]["vector_repository"]
    assert "healthy" in data["subsystems"]["ai_kernel"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_memory_degraded(mock_metadata_repo, mock_vector_repo, mock_ai_kernel):
    # Simulate DB failure
    mock_metadata_repo.list_by_twin.side_effect = Exception("DB Connection Failed")
    
    app.dependency_overrides[get_memory_metadata_repository] = lambda: mock_metadata_repo
    app.dependency_overrides[get_memory_vector_repository] = lambda: mock_vector_repo
    app.dependency_overrides[get_ai_kernel] = lambda: mock_ai_kernel

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health/memory")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert "unhealthy" in data["subsystems"]["metadata_repository"]
    assert "healthy" in data["subsystems"]["vector_repository"]

    app.dependency_overrides.clear()
