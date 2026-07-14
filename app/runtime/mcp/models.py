from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MCPNegotiationRequest(BaseModel):
    """Client capabilities sent during initial connection."""
    protocol_version: str = "2.0"
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    client_info: Dict[str, str] = Field(default_factory=dict)


class MCPNegotiationResponse(BaseModel):
    """Server capabilities returned to client."""
    protocol_version: str = "2.0"
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    server_info: Dict[str, str] = Field(default_factory=dict)


class MCPError(BaseModel):
    """Standardized error model for MCP."""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class MCPToolPermission(BaseModel):
    """Security metadata for a tool."""
    required_permissions: List[str] = Field(default_factory=list)
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    human_approval_required: bool = False


class MCPTool(BaseModel):
    """Tool definition exposed via MCP."""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    security: Optional[MCPToolPermission] = Field(default_factory=MCPToolPermission)


class MCPCallRequest(BaseModel):
    """Request to invoke a tool."""
    name: str
    arguments: Dict[str, Any]


class MCPCallResponse(BaseModel):
    """Result of a tool invocation."""
    content: List[Dict[str, Any]]
    isError: bool = False
