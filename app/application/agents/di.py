from app.bootstrap.container import Container
from app.domain.agents.interfaces import IAgentRegistry
from app.application.agents.registry import InMemoryAgentRegistry

from app.application.agents.runtime import AgentRuntime
from app.application.agents.behaviors.planner import PlannerBehavior
from app.application.agents.behaviors.research import ResearchBehavior
from app.application.agents.behaviors.reasoning import ReasoningBehavior
from app.application.agents.behaviors.executor import ExecutorBehavior
from app.shared.enums import AgentType
from app.shared.events.bus import EventBus
from app.domain.session.repository import ISessionRepository
from app.domain.tasks.repository import ITaskRepository
from app.domain.intelligence.platform import IIntelligencePlatform
from app.application.memory.retriever import MemoryRetriever
from app.application.memory.context import ContextBuilder
from app.domain.memory.platform import IMemoryPlatform

def register_agent_dependencies(container: Container) -> None:
    registry = InMemoryAgentRegistry()
    container.register_singleton(IAgentRegistry, registry)
    
    # We will instantiate AgentRuntime dynamically or register a factory that pulls event_bus and session_repo
    def build_agent_runtime(c: Container) -> AgentRuntime:
        event_bus = c.resolve(EventBus)
        session_repo = c.resolve(ISessionRepository)
        task_repo = c.resolve(ITaskRepository)
        platform = c.resolve(IIntelligencePlatform)
        retriever = c.resolve(MemoryRetriever)
        context_builder = c.resolve(ContextBuilder)
        memory_platform = c.resolve(IMemoryPlatform)
        runtime = AgentRuntime(registry, event_bus, session_repo, task_repo)
        
        # Register behaviors
        runtime.register_behavior(AgentType.PLANNER, PlannerBehavior(event_bus, registry, task_repo, platform))
        runtime.register_behavior(AgentType.RESEARCH, ResearchBehavior(platform, retriever, context_builder, memory_platform))
        runtime.register_behavior(AgentType.REASONING, ReasoningBehavior(platform, retriever, context_builder, memory_platform))
        runtime.register_behavior(AgentType.EXECUTOR, ExecutorBehavior())
        return runtime
        
    container.register_singleton(AgentRuntime, build_agent_runtime(container))
