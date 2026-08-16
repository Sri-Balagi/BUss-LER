from typing import Any

from pydantic import BaseModel

from app.runtime.registry.base import BaseRegistry


class WorkflowMetadata(BaseModel):
    id: str
    name: str
    description: str
    version: str = "1.0.0"


class WorkflowRegistry(BaseRegistry[WorkflowMetadata]):
    """
    Registry for managing Workflows.
    """

    def _deserialize_item(self, data: dict[str, Any]) -> WorkflowMetadata:
        return WorkflowMetadata.model_validate(data)
