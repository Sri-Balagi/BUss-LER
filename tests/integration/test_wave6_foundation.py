import pytest
from fastapi.testclient import TestClient
import uuid

from app.bootstrap.container import build_container, reset_container_for_testing, get_container
from app.infrastructure.applications.gateway.app import create_gateway_app
from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.domain.applications.policy.interfaces import IApplicationPolicyEngine
from app.domain.applications.prompt.interfaces import IPromptBuilder

from app.domain.applications.base import ICognitiveApplication, ApplicationResponse
from app.domain.applications.context.models import ApplicationContext
from app.domain.applications.registry.models import ApplicationMetadata
from app.domain.intelligence.capability import CapabilityType

class MockCopilotApp(ICognitiveApplication):
    def metadata(self) -> ApplicationMetadata:
        return ApplicationMetadata(
            id="test-copilot",
            name="Test Copilot",
            description="A test copilot",
            version="1.0.0",
            supported_capabilities=[CapabilityType.REASONING]
        )

    def supported_capabilities(self):
        return [CapabilityType.REASONING]

    async def execute(self, context: ApplicationContext) -> ApplicationResponse:
        return ApplicationResponse(data={"message": "hello"})

    def health(self) -> bool:
        return True

@pytest.fixture
def test_container():
    reset_container_for_testing()
    container = build_container()
    
    # Register a mock app for testing registry
    registry = container.resolve(IApplicationRegistry)
    registry.register(MockCopilotApp())
    
    yield container
    reset_container_for_testing()

@pytest.fixture
def test_client(test_container):
    app = create_gateway_app()
    return TestClient(app)

def test_di_resolution(test_container):
    """Validate DI container resolves Wave 6 services."""
    registry = test_container.resolve(IApplicationRegistry)
    policy = test_container.resolve(IApplicationPolicyEngine)
    prompt = test_container.resolve(IPromptBuilder)
    
    assert registry is not None
    assert policy is not None
    assert prompt is not None

def test_registry_discovery(test_container):
    """Validate Registry logic."""
    registry = test_container.resolve(IApplicationRegistry)
    app = registry.resolve("test-copilot")
    assert app is not None
    assert app.metadata().id == "test-copilot"

def test_gateway_health(test_client):
    """Validate health endpoint works without auth."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_gateway_auth_required(test_client):
    """Validate auth middleware protects apps routes."""
    response = test_client.get("/apps/")
    assert response.status_code == 401
    
def test_gateway_trace_propagation(test_client):
    """Validate OpenTelemetry trace propagation."""
    headers = {
        "Authorization": "Bearer valid-test-token",
        "X-B3-TraceId": "custom-trace-id",
        "X-B3-SpanId": "custom-span-id"
    }
    response = test_client.get("/apps/", headers=headers)
    assert response.status_code == 200
    assert response.headers["x-b3-traceid"] == "custom-trace-id"
    assert response.headers["x-b3-spanid"] == "custom-span-id"

def test_gateway_routing_to_registry(test_client):
    """Validate gateway routes to registry correctly."""
    headers = {"Authorization": "Bearer valid-test-token"}
    response = test_client.get("/apps/test-copilot", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-copilot"
