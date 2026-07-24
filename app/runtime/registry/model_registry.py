from typing import Any

from pydantic import BaseModel

from app.runtime.registry.base import BaseRegistry


class ModelMetadata(BaseModel):
    id: str
    provider: str
    name: str
    context_window: int
    cost_per_1k_tokens: float = 0.0


class ModelRegistry(BaseRegistry[ModelMetadata]):
    """
    Registry for managing AI Models.
    """

    def _deserialize_item(self, data: dict[str, Any]) -> ModelMetadata:
        return ModelMetadata.model_validate(data)
