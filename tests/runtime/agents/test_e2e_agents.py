import pytest
import asyncio
from app.runtime.agents.interfaces import BaseAgent, IAgentHooks
from app.runtime.agents.results import AgentResult, AgentStatus
from app.runtime.agents.specification import AgentSpecification, ExecutionType
from app.runtime.agents.capability import Capability
from app.runtime.agents.permissions import AgentPermission

class BaseMockAgent(BaseAgent):
    def initialize(self, context):
        self.context = context

    async def execute(self):
        return AgentResult(status=AgentStatus.SUCCESS)

    def suspend(self): pass
    def resume(self): pass
    def cancel(self): pass
    def shutdown(self): pass

class EchoAgent(BaseMockAgent):
    async def execute(self):
        inputs = self.context.scope.get_task_input()
        return AgentResult(status=AgentStatus.SUCCESS, outputs={"echo": inputs.get("message", "")})

class MathAgent(BaseMockAgent):
    async def execute(self):
        inputs = self.context.scope.get_task_input()
        result = inputs.get("a", 0) + inputs.get("b", 0)
        return AgentResult(status=AgentStatus.SUCCESS, outputs={"sum": result})

class SleepAgent(BaseMockAgent):
    async def execute(self):
        inputs = self.context.scope.get_task_input()
        await asyncio.sleep(inputs.get("duration", 0.1))
        return AgentResult(status=AgentStatus.SUCCESS)

class FailingAgent(BaseMockAgent):
    async def execute(self):
        raise ValueError("Intentional Failure")
