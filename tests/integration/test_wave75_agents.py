import pytest
from app.domain.shared.context import ExecutionContext
from app.domain.session.models import Session, SessionParticipant
from app.domain.approval.models import Approval, ApprovalState
from app.domain.agents.models import Agent, Capability
from app.application.agents.registry import InMemoryAgentRegistry
from app.shared.enums import PrincipalType, ParticipantRole, AgentType, AgentStatus
from app.bootstrap.container import build_container, reset_container_for_testing
from app.domain.agents.interfaces import IAgentRegistry

def test_execution_context_backward_compatibility():
    # Constructing with legacy user_id
    ctx = ExecutionContext(
        tenant_id="t1",
        user_id="user_123",
        session_id="s1",
        conversation_id="c1",
        trace_id="tr1",
        correlation_id="corr1"
    )
    assert ctx.principal_id == "user_123"
    assert ctx.principal_type == PrincipalType.HUMAN
    assert ctx.user_id == "user_123"

def test_execution_context_agent_principal():
    ctx = ExecutionContext(
        tenant_id="t1",
        principal_id="agent_123",
        principal_type=PrincipalType.AGENT,
        session_id="s1",
        conversation_id="c1",
        trace_id="tr1",
        correlation_id="corr1"
    )
    assert ctx.principal_id == "agent_123"
    assert ctx.principal_type == PrincipalType.AGENT
    assert ctx.user_id is None

def test_session_backward_compatibility():
    # Constructing with legacy user_id
    session = Session(
        tenant_id="t1",
        user_id="user_123"
    )
    assert len(session.participants) == 1
    assert session.participants[0].id == "user_123"
    assert session.user_id == "user_123"

def test_session_multiple_participants():
    session = Session(
        tenant_id="t1",
        participants=[
            SessionParticipant(id="agent_1", type=PrincipalType.AGENT),
            SessionParticipant(id="user_1", type=PrincipalType.HUMAN, role=ParticipantRole.OWNER)
        ]
    )
    assert session.user_id == "user_1"
    assert len(session.participants) == 2

def test_approval_expiration():
    approval = Approval(
        target_type="job",
        target_id="job_1",
        requested_by="agent_1",
        state=ApprovalState.REQUIRED
    )
    assert approval.state == ApprovalState.REQUIRED
    approval.expire()
    assert approval.state == ApprovalState.EXPIRED
    assert approval.reason == "Approval request expired due to timeout."

def test_agent_registry():
    registry = InMemoryAgentRegistry()
    
    agent = Agent(
        name="Research Assistant",
        description="Assists in web research",
        agent_type=AgentType.RESEARCH,
        capabilities=[
            Capability(name="WebSearch", description="Searches the web")
        ]
    )
    
    registry.register_agent(agent)
    
    fetched = registry.get_agent(agent.id)
    assert fetched is not None
    assert fetched.name == "Research Assistant"
    
    by_type = registry.find_by_type(AgentType.RESEARCH)
    assert len(by_type) == 1
    
    by_cap = registry.find_by_capability("WebSearch")
    assert len(by_cap) == 1
