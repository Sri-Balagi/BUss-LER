import pytest
from datetime import datetime, timezone
from fastapi import HTTPException

from app.domain.security.models import ExecutionContext, DecisionSource
from app.domain.security.permissions import SystemPermission
from app.infrastructure.security.policy_repository import InMemoryPolicyRepository
from app.application.security.authz_service import AuthorizationService
from app.api.dependencies.authz import RequirePermission

@pytest.fixture
def policy_repo():
    return InMemoryPolicyRepository()

@pytest.fixture
def authz_service(policy_repo):
    return AuthorizationService(policy_repo)

@pytest.mark.asyncio
async def test_authz_anonymous_denied(authz_service):
    context = ExecutionContext.anonymous()
    decision = await authz_service.authorize(context, SystemPermission.WORKFLOW_READ)
    
    assert decision.is_allowed is False
    assert decision.decision_source == DecisionSource.DEFAULT_DENY
    assert decision.evaluation_duration_ms is not None
    assert decision.evaluation_duration_ms > 0
    assert decision.evaluated_roles == []
    assert decision.evaluated_permissions == []

@pytest.mark.asyncio
async def test_authz_direct_permission_allowed(authz_service):
    context = ExecutionContext(
        is_authenticated=True,
        scopes=[SystemPermission.WORKFLOW_EXECUTE.value]
    )
    decision = await authz_service.authorize(context, SystemPermission.WORKFLOW_EXECUTE)
    
    assert decision.is_allowed is True
    assert decision.decision_source == DecisionSource.DIRECT_PERMISSION
    assert SystemPermission.WORKFLOW_EXECUTE.value in decision.matched_permissions
    assert decision.evaluation_duration_ms is not None
    assert decision.evaluated_roles == []
    assert decision.evaluated_permissions == [SystemPermission.WORKFLOW_EXECUTE.value]

@pytest.mark.asyncio
async def test_authz_role_permission_allowed(authz_service):
    context = ExecutionContext(
        is_authenticated=True,
        roles=["viewer"] # Has WORKFLOW_READ
    )
    decision = await authz_service.authorize(context, SystemPermission.WORKFLOW_READ)
    
    assert decision.is_allowed is True
    assert decision.decision_source == DecisionSource.ROLE
    assert decision.evaluation_duration_ms is not None
    assert decision.evaluated_roles == ["viewer"]
    assert SystemPermission.WORKFLOW_READ.value in decision.evaluated_permissions

@pytest.mark.asyncio
async def test_authz_role_permission_denied(authz_service):
    context = ExecutionContext(
        is_authenticated=True,
        roles=["viewer"] # Lacks WORKFLOW_WRITE
    )
    decision = await authz_service.authorize(context, SystemPermission.WORKFLOW_WRITE)
    
    assert decision.is_allowed is False
    assert decision.decision_source == DecisionSource.DEFAULT_DENY
    assert decision.evaluation_duration_ms is not None
    assert decision.evaluated_roles == ["viewer"]

@pytest.mark.asyncio
async def test_authz_admin_allowed_everything(authz_service):
    context = ExecutionContext(
        is_authenticated=True,
        roles=["system:admin"] 
    )
    # Admin should be allowed any explicit permission check that exists in their set
    decision = await authz_service.authorize(context, SystemPermission.WORKFLOW_WRITE)
    assert decision.is_allowed is True
    assert decision.decision_source == DecisionSource.ROLE
    assert SystemPermission.SYSTEM_ADMIN.value in decision.matched_permissions
    assert decision.evaluation_duration_ms is not None
    assert decision.evaluated_roles == ["system:admin"]

@pytest.mark.asyncio
async def test_require_permission_dependency(authz_service):
    require = RequirePermission(SystemPermission.WORKFLOW_READ)
    
    context = ExecutionContext(
        is_authenticated=True,
        roles=["developer"]
    )
    
    # Should succeed and return context
    result = await require(context=context, engine=authz_service)
    assert result == context

@pytest.mark.asyncio
async def test_require_permission_dependency_401(authz_service):
    require = RequirePermission(SystemPermission.WORKFLOW_READ)
    context = ExecutionContext.anonymous()
    
    with pytest.raises(HTTPException) as exc:
        await require(context=context, engine=authz_service)
        
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_require_permission_dependency_403(authz_service):
    require = RequirePermission(SystemPermission.WORKFLOW_WRITE)
    context = ExecutionContext(
        is_authenticated=True,
        roles=["viewer"]
    )
    
    with pytest.raises(HTTPException) as exc:
        await require(context=context, engine=authz_service)
        
    assert exc.value.status_code == 403
