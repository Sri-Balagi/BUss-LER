import pytest

from app.runtime.mcp.bridge import MCPBridge
from app.runtime.mcp.models import MCPCallRequest
from app.runtime.registry.store import InMemoryRegistryStore
from app.runtime.registry.tool_registry import ToolMetadata, ToolRegistry


@pytest.mark.asyncio
async def test_mcp_discovery():
    store = InMemoryRegistryStore()
    registry = ToolRegistry("Tools", store)
    bridge = MCPBridge(registry)

    await registry.register("calculator", ToolMetadata(id="calculator", name="calculator", description="Math tool"))

    tools = await bridge.list_tools()
    assert len(tools["tools"]) == 1
    assert tools["tools"][0]["name"] == "calculator"
    assert tools["tools"][0]["description"] == "Math tool"

@pytest.mark.asyncio
async def test_mcp_call_tool():
    store = InMemoryRegistryStore()
    registry = ToolRegistry("Tools", store)
    bridge = MCPBridge(registry)

    await registry.register("calculator", ToolMetadata(id="calculator", name="calculator", description="Math tool"))

    req = MCPCallRequest(name="calculator", arguments={"expr": "1+1"})
    res = await bridge.call_tool(req)

    assert res.isError is False
    assert res.content[0]["text"] == "Successfully invoked calculator"

@pytest.mark.asyncio
async def test_mcp_call_unknown_tool():
    store = InMemoryRegistryStore()
    registry = ToolRegistry("Tools", store)
    bridge = MCPBridge(registry)

    req = MCPCallRequest(name="unknown", arguments={})
    res = await bridge.call_tool(req)

    assert res.isError is True
    assert "not found" in res.content[0]["text"]
