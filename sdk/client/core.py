from typing import Any, Optional

from app.bootstrap.container import get_container, build_container, ContainerNotInitializedError
from app.domain.agents.interfaces import IAgentRuntime
from app.domain.agents.models import Agent, AgentTemplate
from app.shared.enums import AgentCapability
from sdk.client.wrappers import SDKAgent, SDKModule



class BizOSClient:
    """
    Internal In-Process SDK Client for BizOS.
    Exposes high-level primitives (Agent, Goal, Workflow, Memory, Tool, Module)
    to interact with the underlying Engine without exposing DI wiring.
    """

    def __init__(self):
        try:
            self.container = get_container()
        except ContainerNotInitializedError:
            self.container = build_container()

        self.agent_runtime = self.container.resolve(IAgentRuntime)
        
        # Other registries/services would be resolved here as the SDK matures
        # self.memory_repo = self.container.resolve(IMemoryRepository)
        # self.workflow_service = self.container.resolve(IWorkflowService)

    async def create_agent(self, name: str, template: AgentTemplate | None = None, capabilities: list[AgentCapability] | None = None) -> SDKAgent:
        """Instantiate a new autonomous agent in the BizOS environment."""
        agent_model = await self.agent_runtime.spawn_agent(name, template, capabilities)
        return SDKAgent(self, agent_model)

    async def create_agent_from_template(self, name: str, template: AgentTemplate) -> SDKAgent:
        """Instantiate a new autonomous agent from a module template."""
        return await self.create_agent(name, template=template)

    async def execute_goal(self, agent_id: str, goal_description: str) -> dict:
        """Submit a goal for an agent to execute."""
        return await self.agent_runtime.execute_goal(agent_id, goal_description)

    async def get_agent_state(self, agent_id: str) -> dict:
        """Retrieve current state of an agent."""
        return await self.agent_runtime.get_agent_state(agent_id)

    # Placeholders for the remaining primitives requested
    async def create_memory(self, session_id: str, content: str) -> Any:
        """Store long-term memory for an entity."""
        pass

    async def trigger_workflow(self, workflow_id: str, context: dict) -> Any:
        """Trigger a predefined workflow."""
        pass

    def get_module(self, module_name: str) -> SDKModule:
        """Retrieve a domain module's Business Knowledge Model (BKM)."""
        import importlib
        try:
            module = importlib.import_module(f"app.modules.{module_name}.ai.cognition")
            for attr_name in dir(module):
                if attr_name.endswith('_KNOWLEDGE_MODEL'):
                    return SDKModule(self, module_name, getattr(module, attr_name))
            raise ValueError(f"No BusinessKnowledgeModel found in module {module_name}")
        except ImportError:
            raise ValueError(f"Module {module_name} not found")
