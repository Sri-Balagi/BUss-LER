import pytest
from app.runtime.agents.specification import AgentSpecification, ExecutionType
from app.runtime.agents.interfaces import BaseAgent
from app.runtime.agents.factories import TransientFactory, SingletonFactory

class DummyAgent(BaseAgent):
    def initialize(self, context):
        pass
    async def execute(self):
        pass
    def suspend(self):
        pass
    def resume(self):
        pass
    def cancel(self):
        pass
    def shutdown(self):
        pass

def test_transient_factory():
    spec = AgentSpecification(identity="dummy", capabilities=[])
    factory = TransientFactory(DummyAgent)
    
    agent1 = factory.create_agent(spec)
    agent2 = factory.create_agent(spec)
    
    assert isinstance(agent1, DummyAgent)
    assert agent1 is not agent2

def test_singleton_factory():
    spec = AgentSpecification(identity="dummy", capabilities=[])
    factory = SingletonFactory(DummyAgent)
    
    agent1 = factory.create_agent(spec)
    agent2 = factory.create_agent(spec)
    
    assert isinstance(agent1, DummyAgent)
    assert agent1 is agent2
