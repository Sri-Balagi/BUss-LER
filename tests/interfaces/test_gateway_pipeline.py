import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.http.middleware.pipeline import register_gateway_pipeline
from app.interfaces.http.v1.schemas.response import BizOSResponse


@pytest.fixture
def app():
    # Create a minimal app to test the pipeline
    test_app = FastAPI()

    # Register the pipeline
    register_gateway_pipeline(test_app)

    @test_app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    @test_app.post("/mutate")
    async def mutate_endpoint():
        return {"status": "mutated"}

    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_gateway_pipeline_injects_tracing_headers(client):
    response = client.get("/test")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Correlation-ID" in response.headers
    assert "X-Trace-ID" in response.headers


def test_gateway_pipeline_rejects_invalid_jwt(client):
    response = client.get("/test", headers={"Authorization": "Bearer "})

    # Empty token string causes our simple middleware to reject it
    assert response.status_code == 401

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "unauthorized"


def test_gateway_pipeline_rate_limiter_allows_under_limit(client):
    # A single request should pass
    response = client.get("/test", headers={"X-Tenant-ID": "test-tenant"})
    assert response.status_code == 200


def test_gateway_pipeline_idempotency_ignores_get(client):
    # GET requests should not be cached by IdempotencyMiddleware
    response1 = client.get("/test", headers={"Idempotency-Key": "test-key-1"})
    response2 = client.get("/test", headers={"Idempotency-Key": "test-key-1"})

    assert response1.status_code == 200
    assert response2.status_code == 200
