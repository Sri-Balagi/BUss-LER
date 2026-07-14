from typing import Any, Dict

from app.runtime.agents.specification import AgentSpecification
from app.runtime.registry.base import BaseRegistry


class AgentRegistry(BaseRegistry[AgentSpecification]):
    """
    Registry for managing Agent metadata and specifications.
    Inherits sync, broadcast, and lifecycle capabilities from BaseRegistry.
    """

    def _deserialize_item(self, data: Dict[str, Any]) -> AgentSpecification:
        return AgentSpecification.model_validate(data)
