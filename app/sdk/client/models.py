from typing import Any

from pydantic import BaseModel


class SDKResponse(BaseModel):
    """
    Standardized response envelope mapped from BizOSResponse.
    """
    success: bool
    data: Any | None = None
    error: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None


class RegistryItemModel(BaseModel):
    """
    Generic model representing an item from the BizOS Registries.
    """
    id: str
    name: str
    type: str
    metadata: dict[str, Any]


class ToolExecutionRequest(BaseModel):
    """
    Model for invoking a tool via the SDK.
    """
    tool_name: str
    arguments: dict[str, Any]
