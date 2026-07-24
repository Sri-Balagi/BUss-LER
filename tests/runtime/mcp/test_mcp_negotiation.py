import pytest

from app.runtime.mcp.bridge import MCPBridge
from app.runtime.mcp.models import MCPNegotiationRequest
from app.runtime.registry.store import InMemoryRegistryStore
from app.runtime.registry.tool_registry import ToolRegistry


@pytest.mark.asyncio
async def test_mcp_negotiation():
    store = InMemoryRegistryStore()
    registry = ToolRegistry("Tools", store)
    bridge = MCPBridge(registry)

    req = MCPNegotiationRequest(
        protocol_version="2.0",
        client_info={"name": "test-client"}
    )

    res = await bridge.negotiate(req)
    assert res.protocol_version == "2.0"
    assert res.server_info["name"] == "BizOS-MCP-Gateway"
    assert "tools" in res.capabilities
