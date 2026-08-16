import pytest

from app.runtime.mcp.models import MCPTool, MCPToolPermission


def test_mcp_tool_security_metadata():
    perm = MCPToolPermission(
        required_permissions=["fs:read", "fs:write"],
        risk_level="HIGH",
        human_approval_required=True
    )

    tool = MCPTool(
        name="edit_file",
        description="Edits a file",
        inputSchema={"type": "object"},
        security=perm
    )

    assert tool.security.risk_level == "HIGH"
    assert tool.security.human_approval_required is True
    assert "fs:read" in tool.security.required_permissions
