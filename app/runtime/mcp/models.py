from typing import Any

from pydantic import BaseModel, Field


class MCPNegotiationRequest(BaseModel):
    """Client capabilities sent during initial connection."""
    protocol_version: str = "2.0"
    capabilities: dict[str, Any] = Field(default_factory=dict)
    client_info: dict[str, str] = Field(default_factory=dict)


class MCPNegotiationResponse(BaseModel):
    """Server capabilities returned to client."""
    protocol_version: str = "2.0"
    capabilities: dict[str, Any] = Field(default_factory=dict)
    server_info: dict[str, str] = Field(default_factory=dict)


class MCPError(BaseModel):
    """Standardized error model for MCP."""
    code: int
    message: str
    data: dict[str, Any] | None = None


class MCPToolPermission(BaseModel):
    """Security metadata for a tool."""
    required_permissions: list[str] = Field(default_factory=list)
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    human_approval_required: bool = False


class MCPTool(BaseModel):
    """Tool definition exposed via MCP."""
    name: str
    description: str
    inputSchema: dict[str, Any]
    security: MCPToolPermission | None = Field(default_factory=MCPToolPermission)


class MCPCallRequest(BaseModel):
    """Request to invoke a tool."""
    name: str
    arguments: dict[str, Any]


class MCPCallResponse(BaseModel):
    """Result of a tool invocation."""
    content: list[dict[str, Any]]
    isError: bool = False
