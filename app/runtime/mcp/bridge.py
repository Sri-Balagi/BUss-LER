import logging
from typing import Any

from app.runtime.mcp.interfaces import IMCPServer
from app.runtime.mcp.models import (
    MCPCallRequest,
    MCPCallResponse,
    MCPNegotiationRequest,
    MCPNegotiationResponse,
)
from app.runtime.registry.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class MCPBridge(IMCPServer):
    """
    Translates between the external MCP Protocol and BizOS internal subsystems.
    Acts as the default IMCPServer implementation.
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry

    async def negotiate(self, request: MCPNegotiationRequest) -> MCPNegotiationResponse:
        """
        Handles the handshake, verifying client capabilities and exposing server capabilities.
        """
        logger.info(f"MCP Negotiation from client: {request.client_info}")

        # We declare that we support 'tools'
        server_caps = {
            "tools": {"listChanged": True},
            "logging": {}
        }

        return MCPNegotiationResponse(
            protocol_version="2.0",
            capabilities=server_caps,
            server_info={"name": "BizOS-MCP-Gateway", "version": "6.0.0"}
        )

    async def list_tools(self) -> dict[str, Any]:
        """
        Retrieves tools from the internal ToolRegistry and formats them for MCP.
        """
        tools = await self.tool_registry.list_all()
        mcp_tools = []
        for t in tools:
            # We map our internal ToolMetadata to MCP format
            mcp_tools.append({
                "name": t.name,
                "description": t.description,
                "inputSchema": {
                    "type": "object",
                    "properties": {} # Simplified for milestone
                }
            })

        return {"tools": mcp_tools}

    async def call_tool(self, request: MCPCallRequest) -> MCPCallResponse:
        """
        Translates an MCP call tool request into a BizOS syscall or workflow execution.
        """
        tool = await self.tool_registry.get(request.name)
        if not tool:
            return MCPCallResponse(
                content=[{"type": "text", "text": f"Tool '{request.name}' not found."}],
                isError=True
            )

        # In a full implementation, we would route this to the SystemBus/Kernel for execution.
        # For M2 scope, we simulate successful invocation.
        logger.info(f"Invoked tool {request.name} via MCP Bridge.")
        return MCPCallResponse(
            content=[{"type": "text", "text": f"Successfully invoked {request.name}"}],
            isError=False
        )
