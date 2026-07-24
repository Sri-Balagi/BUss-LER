import asyncio
import uuid
from typing import Any

import pytest
from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_execution_context
from app.api.dependencies.authz import RequirePermission
from app.bootstrap.container import build_container, get_container, reset_container_for_testing
from app.domain.security.interfaces import (
    IAuditSink,
    IAuthenticationService,
    IPolicyEngine,
    IPolicyRepository,
    ITokenGenerator,
)
from app.domain.security.models import (
    AuthenticationStatus,
    ExecutionContext,
)
from app.domain.security.permissions import SystemPermission
from app.infrastructure.execution.factory import ExecutionStrategyFactory
from app.infrastructure.execution.sandboxed_strategy import SandboxedExecutionStrategy
from app.infrastructure.execution.strategy import ExecutionContext as SandboxExecutionContext
from app.infrastructure.execution.strategy import ExecutionStrategy
from app.infrastructure.security.audit import AuditSubscriber, InMemoryAuditSink
from app.shared.events.bus import EventBus

# We will create a test app and inject dependencies
app = FastAPI()
test_router = APIRouter()

@test_router.get("/protected")
async def protected_route(context: ExecutionContext = Depends(RequirePermission(SystemPermission.WORKFLOW_READ))):
    return {"message": "success", "user_id": str(context.user_id)}

app.include_router(test_router)


@pytest.fixture(scope="function", autouse=True)
def setup_container():
    reset_container_for_testing()
    container = build_container()

    # We must ensure AuditSubscriber is resolved so it listens to the EventBus
    from app.infrastructure.security.audit import AuditSubscriber
    container.resolve(AuditSubscriber)

    yield container
    reset_container_for_testing()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_startup_di_resolution(setup_container):
    """Test that all security services are registered in the DI container and resolve successfully."""
    container = setup_container
    assert container.resolve(IAuthenticationService) is not None
    assert container.resolve(IPolicyEngine) is not None
    assert container.resolve(IAuditSink) is not None
    assert container.resolve(EventBus) is not None
    assert container.resolve(ExecutionStrategyFactory) is not None


# Module-level functions for pickling
def slow_fn_sync():
    import time
    time.sleep(0.5)
    return "done"

def fast_fn_sync():
    return "success"


@pytest.mark.asyncio
async def test_full_auth_authz_audit_flow(client, setup_container):
    """Positive test: Valid mocked context -> Authz Allowed -> Request logs"""
    async def mock_admin_context():
        return ExecutionContext(
            user_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            roles=["system:admin"], # Admin has all permissions
            scopes=[],
            is_authenticated=True
        )

    app.dependency_overrides[get_execution_context] = mock_admin_context
    try:
        response = client.get("/protected")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()

    # Let's wait a bit and check the EventBus
    await asyncio.sleep(0.1)
    container = setup_container
    sink = container.resolve(IAuditSink)
    events = sink.get_events()
    assert len(events) > 0
    authz_events = [e for e in events if getattr(e, "category", None) == "AUTHORIZATION" and e.result == "SUCCESS"]
    assert len(authz_events) >= 1


@pytest.mark.asyncio
async def test_anonymous_request_rejected(client, setup_container):
    """Negative test: Anonymous request should be rejected by Authz (401)."""
    response = client.get("/protected")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_token_rejected(client, setup_container):
    """Negative test: Invalid token -> Auth fails -> context anonymous -> Authz rejects 401"""
    response = client.get("/protected", headers={"Authorization": "Bearer invalid.token.here"})
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_insufficient_permissions(client, setup_container):
    """Negative test: Valid auth but lacks permissions -> 403 Forbidden"""

    async def mock_get_context():
        return ExecutionContext(
            user_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            roles=["GUEST"],
            scopes=[],
            is_authenticated=True
        )

    app.dependency_overrides[get_execution_context] = mock_get_context
    try:
        response = client.get("/protected")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sandbox_execution_and_audit(setup_container):
    """Verify Sandbox limits and SecurityEvent emission."""
    container = setup_container
    factory = container.resolve(ExecutionStrategyFactory)
    strategy = factory.get_strategy(ExecutionStrategy.SANDBOXED)
    assert isinstance(strategy, SandboxedExecutionStrategy)

    # 1. Test timeout violation
    context = SandboxExecutionContext(timeout_seconds=0.1)

    result = await strategy.execute(slow_fn_sync, context)
    assert result.success is False
    assert "timed out" in str(result.error).lower() or "timeout" in str(result.error).lower() or "process pool broken" in str(result.error).lower()

    # Ensure audit event was captured by the sink
    sink = container.resolve(IAuditSink)
    # The EventBus is async, we may need to yield to event loop
    await asyncio.sleep(0.1)

    events = sink.get_events()
    assert len(events) > 0
    timeout_events = [e for e in events if getattr(e, "action", None) == "EXECUTION_TIMEOUT"]
    assert len(timeout_events) >= 1

    # 2. Test successful execution
    result2 = await strategy.execute(fast_fn_sync, SandboxExecutionContext())
    assert result2.success is True

    await asyncio.sleep(0.1)
    events2 = sink.get_events()
    success_events = [e for e in events2 if getattr(e, "action", None) == "EXECUTION_COMPLETED" and e.result == "SUCCESS"]
    assert len(success_events) >= 1
