from typing import Any

from pydantic import BaseModel

from app.runtime.registry.base import BaseRegistry


class PromptMetadata(BaseModel):
    id: str
    name: str
    template: str
    version: str = "1.0.0"


class PromptRegistry(BaseRegistry[PromptMetadata]):
    """
    Registry for managing System Prompts and Templates.
    """

    def _deserialize_item(self, data: dict[str, Any]) -> PromptMetadata:
        return PromptMetadata.model_validate(data)
