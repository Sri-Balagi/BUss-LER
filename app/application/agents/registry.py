from threading import Lock

from app.domain.agents.interfaces import IAgentRegistry
from app.domain.agents.models import Agent
from app.shared.enums import AgentType


class InMemoryAgentRegistry(IAgentRegistry):
    def __init__(self):
        self._agents: dict[str, Agent] = {}
        self._lock = Lock()

    def register_agent(self, agent: Agent) -> None:
        with self._lock:
            self._agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> Agent | None:
        with self._lock:
            return self._agents.get(agent_id)

    def list_agents(self) -> list[Agent]:
        with self._lock:
            return list(self._agents.values())

    def find_by_type(self, agent_type: AgentType) -> list[Agent]:
        with self._lock:
            return [a for a in self._agents.values() if a.agent_type == agent_type]

    def find_by_capability(self, capability_name: str) -> list[Agent]:
        with self._lock:
            return [
                a for a in self._agents.values()
                if any(c.name == capability_name for c in a.capabilities)
            ]
