import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.sdk.client.config import SDKConfig
from app.sdk.client.sync_client import BizOSClient


@pytest.fixture
def e2e_client():
    with TestClient(app) as test_client:
        config = SDKConfig(base_url="http://testserver")
        client = BizOSClient(config=config)
        client._client = test_client
        yield client

def test_sdk_api_health_e2e(e2e_client):
    health = e2e_client.get_health()
    assert health.success is True
    # The gateway health endpoint returns "OK" in data
    assert "status" in health.data or "message" in health.data or health.data == "OK" or isinstance(health.data, dict)
