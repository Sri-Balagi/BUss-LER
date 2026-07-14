from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SDKResponse(BaseModel):
    """
    Standardized response envelope mapped from BizOSResponse.
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class RegistryItemModel(BaseModel):
    """
    Generic model representing an item from the BizOS Registries.
    """
    id: str
    name: str
    type: str
    metadata: Dict[str, Any]


class ToolExecutionRequest(BaseModel):
    """
    Model for invoking a tool via the SDK.
    """
    tool_name: str
    arguments: Dict[str, Any]
