import pytest
from unittest.mock import patch, MagicMock
from app.sdk.client.sync_client import BizOSClient
from app.sdk.client.config import SDKConfig

@patch("httpx.Client.get")
def test_sync_client_health(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "data": {"status": "ok"}}
    mock_get.return_value = mock_response
    
    config = SDKConfig(base_url="http://test")
    with BizOSClient(config=config) as client:
        health = client.get_health()
        assert health.success is True
        assert health.data["status"] == "ok"
