from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.http.v1.routers.mcp import _active_transports, mcp_router
from app.runtime.mcp.models import (
    MCPCallRequest,
    MCPCallResponse,
    MCPNegotiationRequest,
    MCPNegotiationResponse,
)

app = FastAPI()
app.include_router(mcp_router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_transports():
    _active_transports.clear()
    yield
    _active_transports.clear()

@pytest.fixture
def mock_bridge():
    with patch('app.interfaces.http.v1.routers.mcp._get_bridge') as mock:
        bridge = AsyncMock()
        mock.return_value = bridge
        yield bridge

def test_mcp_messages_no_transport():
    response = client.post("/messages", json={"method": "tools/list", "id": 1})
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "no_connection"

@pytest.mark.asyncio
async def test_mcp_messages_initialize(mock_bridge):
    mock_transport = AsyncMock()
    _active_transports["testclient"] = mock_transport

    mock_bridge.negotiate.return_value = MCPNegotiationResponse(
        protocol_version="2.0",
        capabilities={},
        server_info={"name": "test"}
    )

    response = client.post("/messages", json={
        "method": "initialize",
        "params": {"client_info": {"name": "test"}, "protocol_version": "2.0"},
        "id": 1
    })

    assert response.status_code == 200
    assert response.json()["success"] is True

    mock_bridge.negotiate.assert_called_once()
    mock_transport.send.assert_called_once()

@pytest.mark.asyncio
async def test_mcp_messages_tools_list(mock_bridge):
    mock_transport = AsyncMock()
    _active_transports["testclient"] = mock_transport

    mock_bridge.list_tools.return_value = [{"name": "tool1"}]

    response = client.post("/messages", json={
        "method": "tools/list",
        "id": 2
    })

    assert response.status_code == 200
    mock_bridge.list_tools.assert_called_once()
    mock_transport.send.assert_called_once()
    args = mock_transport.send.call_args[0][0]
    assert args["result"] == [{"name": "tool1"}]

@pytest.mark.asyncio
async def test_mcp_messages_tools_call(mock_bridge):
    mock_transport = AsyncMock()
    _active_transports["testclient"] = mock_transport

    mock_bridge.call_tool.return_value = MCPCallResponse(
        content=[{"text": "ok"}]
    )

    response = client.post("/messages", json={
        "method": "tools/call",
        "params": {"name": "tool1", "arguments": {}},
        "id": 3
    })

    assert response.status_code == 200
    mock_bridge.call_tool.assert_called_once()
    mock_transport.send.assert_called_once()

@pytest.mark.asyncio
async def test_mcp_messages_unknown_method(mock_bridge):
    mock_transport = AsyncMock()
    _active_transports["testclient"] = mock_transport

    response = client.post("/messages", json={
        "method": "unknown_method",
        "id": 4
    })

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "method_not_found"
