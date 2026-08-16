from typing import Any
from app.domain.agents.models import Agent

class SDKAgent:
    """
    Fluent wrapper around an Agent domain model, providing a simplified developer interface
    to interact with the BizOS runtime orchestration layer.
    """
    def __init__(self, client: Any, model: Agent):
        self._client = client
        self.model = model

    @property
    def id(self) -> str:
        return self.model.id

    @property
    def name(self) -> str:
        return self.model.name
    
    @property
    def capabilities(self) -> list:
        return self.model.capabilities

    async def execute_goal(self, goal_description: str) -> dict:
        """
        Submits a goal to the Multi-Agent Orchestrator for this specific agent.
        """
        return await self._client.execute_goal(self.id, goal_description)

    async def get_state(self) -> dict:
        """
        Retrieves the current state of this agent from the orchestrator.
        """
        return await self._client.get_agent_state(self.id)

class SDKGoal:
    pass

class SDKWorkflow:
    pass

class SDKMemory:
    pass

class SDKModule:
    def __init__(self, client: Any, name: str, knowledge_model: Any):
        self._client = client
        self.name = name
        self.knowledge_model = knowledge_model

    def list_agent_templates(self) -> list:
        return getattr(self.knowledge_model, 'agent_templates', [])
