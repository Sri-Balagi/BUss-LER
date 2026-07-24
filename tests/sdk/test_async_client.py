from unittest.mock import MagicMock, patch

import pytest

from app.sdk.client.async_client import AsyncBizOSClient
from app.sdk.client.config import SDKConfig


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_async_client_health(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "data": {"status": "ok"}}
    mock_get.return_value = mock_response

    config = SDKConfig(base_url="http://test")
    async with AsyncBizOSClient(config=config) as client:
        health = await client.get_health()
        assert health.success is True
        assert health.data["status"] == "ok"
