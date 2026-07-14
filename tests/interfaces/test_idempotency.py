import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.http.middleware.idempotency import IdempotencyMiddleware


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.add_middleware(IdempotencyMiddleware)
    
    counter = {"count": 0}
    
    @test_app.post("/mutate")
    async def mutate_endpoint():
        counter["count"] += 1
        return {"count": counter["count"]}

    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_idempotency_caches_post_requests(client):
    # First request: should execute and return count=1
    response1 = client.post("/mutate", headers={"Idempotency-Key": "key-123"})
    assert response1.status_code == 200
    assert response1.json() == {"count": 1}
    
    # Second request with SAME key: should return cached count=1 without executing
    response2 = client.post("/mutate", headers={"Idempotency-Key": "key-123"})
    assert response2.status_code == 200
    assert response2.json() == {"count": 1}
    
    # Third request with NEW key: should execute and return count=2
    response3 = client.post("/mutate", headers={"Idempotency-Key": "key-456"})
    assert response3.status_code == 200
    assert response3.json() == {"count": 2}


def test_idempotency_does_not_cache_without_key(client):
    response1 = client.post("/mutate")
    assert response1.json() == {"count": 1}
    
    response2 = client.post("/mutate")
    assert response2.json() == {"count": 2}
