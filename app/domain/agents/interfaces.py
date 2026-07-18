from typing import List, Optional
from abc import ABC, abstractmethod

from app.domain.agents.models import Agent
from app.shared.enums import AgentType

class IAgentRegistry(ABC):
    @abstractmethod
    def register_agent(self, agent: Agent) -> None:
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        pass

    @abstractmethod
    def list_agents(self) -> List[Agent]:
        pass

    @abstractmethod
    def find_by_type(self, agent_type: AgentType) -> List[Agent]:
        pass

    @abstractmethod
    def find_by_capability(self, capability_name: str) -> List[Agent]:
        pass
