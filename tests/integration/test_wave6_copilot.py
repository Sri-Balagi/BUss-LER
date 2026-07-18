import pytest
import uuid

from app.bootstrap.container import build_container, reset_container_for_testing
from app.application.applications.copilot.app import CopilotApplication
from app.domain.applications.context.models import ChatContext
from app.domain.intelligence.capability import CapabilityType
from app.domain.applications.registry.interfaces import IApplicationRegistry

@pytest.fixture
def test_container():
    reset_container_for_testing()
    container = build_container()
    # Force resolve of CopilotApplication so it registers itself
    container.resolve(CopilotApplication)
    yield container
    reset_container_for_testing()

@pytest.mark.asyncio
async def test_copilot_metadata(test_container):
    registry = test_container.resolve(IApplicationRegistry)
    app = registry.resolve("bizos.copilot.v1")
    
    assert app is not None
    assert app.metadata().id == "bizos.copilot.v1"
    assert app.metadata().name == "BizOS Conversational Copilot"
    assert CapabilityType.REASONING in app.supported_capabilities()

@pytest.mark.asyncio
async def test_copilot_execution(test_container):
    registry = test_container.resolve(IApplicationRegistry)
    app = registry.resolve("bizos.copilot.v1")
    
    context = ChatContext(
        user_id="user-1",
        tenant_id=str(uuid.uuid4()),
        session_id="session-1",
        variables={"message": "Analyze this business scenario."}
    )
    
    response = await app.execute(context)
    
    assert response is not None
    assert hasattr(response, "data")
    assert hasattr(response, "metadata")
