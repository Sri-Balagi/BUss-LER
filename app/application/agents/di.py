from app.bootstrap.container import Container
from app.domain.agents.interfaces import IAgentRegistry
from app.application.agents.registry import InMemoryAgentRegistry

def register_agent_dependencies(container: Container) -> None:
    container.register_singleton(IAgentRegistry, InMemoryAgentRegistry())
