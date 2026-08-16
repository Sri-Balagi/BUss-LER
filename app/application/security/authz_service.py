import time
import uuid
from dataclasses import asdict
from typing import Any

import structlog

from app.domain.security.interfaces import IAuditPublisher, IPolicyEngine, IPolicyRepository
from app.domain.security.models import AuthorizationDecision, DecisionSource, ExecutionContext
from app.domain.security.permissions import SystemPermission
from app.shared.events.models import AuditCategory, SecurityEvent

logger = structlog.get_logger()

class AuthorizationService(IPolicyEngine):
    """
    Stateless Authorization Service that implements the Policy Engine.
    Evaluates an ExecutionContext against required permissions.
    """

    def __init__(self, policy_repo: IPolicyRepository, audit_publisher: IAuditPublisher | None = None):
        self._policy_repo = policy_repo
        self._audit_publisher = audit_publisher

    def _emit_audit(self, decision: AuthorizationDecision, context: ExecutionContext, resource: Any | None) -> None:
        if not self._audit_publisher:
            return

        action = "AUTHORIZE"
        event_result = "SUCCESS" if decision.is_allowed else "FAILURE"

        ctx_dict = asdict(context) if context else None

        # We try to represent the resource as a string for auditing
        resource_str = str(resource) if resource is not None else None

        event = SecurityEvent(
            correlation_id=context.correlation_id if context and context.correlation_id else str(uuid.uuid4()),
            category=AuditCategory.AUTHORIZATION,
            action=action,
            result=event_result,
            execution_context=ctx_dict,
            user_id=str(context.user_id) if context and context.user_id else None,
            tenant_id=str(context.tenant_id) if context and context.tenant_id else None,
            resource=resource_str,
            metadata=asdict(decision),
            severity="INFO" if event_result == "SUCCESS" else "WARNING"
        )
        self._audit_publisher.publish_audit(event)

    async def authorize(
        self,
        context: ExecutionContext,
        permission: SystemPermission,
        resource: Any | None = None
    ) -> AuthorizationDecision:
        start_time = time.perf_counter()

        # 1. Anonymous contexts are fundamentally unauthorized for any specific permission.
        if not context.is_authenticated:
            logger.info("authz_denied_anonymous", permission=permission.value)
            duration_ms = (time.perf_counter() - start_time) * 1000
            decision = AuthorizationDecision.deny(
                required_permission=permission.value,
                reason="Anonymous execution context is not allowed.",
                source=DecisionSource.DEFAULT_DENY,
                evaluated_roles=context.roles,
                evaluated_permissions=context.scopes,
                evaluation_duration_ms=duration_ms
            )
            self._emit_audit(decision, context, resource)
            return decision

        # 2. Check for direct permissions in the context scopes (e.g. from API Key or JWT scopes)
        if permission.value in context.scopes:
            logger.debug("authz_granted_via_direct_permission", permission=permission.value, subject=context.user_id or context.api_key_id)
            duration_ms = (time.perf_counter() - start_time) * 1000
            decision = AuthorizationDecision.allow(
                required_permission=permission.value,
                matched_permissions=[permission.value],
                source=DecisionSource.DIRECT_PERMISSION,
                reason="Granted via direct permission (scope)",
                evaluated_roles=context.roles,
                evaluated_permissions=context.scopes,
                evaluation_duration_ms=duration_ms
            )
            self._emit_audit(decision, context, resource)
            return decision

        # 3. Resolve Roles to Permissions via the Policy Repository
        if context.roles:
            resolved_permissions = await self._policy_repo.get_permissions_for_roles(context.roles)

            # System Admin Role usually acts as a master key.
            if SystemPermission.SYSTEM_ADMIN.value in resolved_permissions:
                logger.debug("authz_granted_via_admin_role", permission=permission.value, subject=context.user_id)
                duration_ms = (time.perf_counter() - start_time) * 1000
                decision = AuthorizationDecision.allow(
                    required_permission=permission.value,
                    matched_permissions=[SystemPermission.SYSTEM_ADMIN.value],
                    source=DecisionSource.ROLE,
                    reason="Granted via System Admin privileges",
                    evaluated_roles=context.roles,
                    evaluated_permissions=list(resolved_permissions),
                    evaluation_duration_ms=duration_ms
                )
                self._emit_audit(decision, context, resource)
                return decision

            if permission.value in resolved_permissions:
                logger.debug("authz_granted_via_role", permission=permission.value, subject=context.user_id)
                duration_ms = (time.perf_counter() - start_time) * 1000
                decision = AuthorizationDecision.allow(
                    required_permission=permission.value,
                    matched_permissions=[permission.value],
                    source=DecisionSource.ROLE,
                    reason="Granted via resolved role permissions",
                    evaluated_roles=context.roles,
                    evaluated_permissions=list(resolved_permissions),
                    evaluation_duration_ms=duration_ms
                )
                self._emit_audit(decision, context, resource)
                return decision

        # 4. If resource is provided, we would evaluate resource-level policies here
        # (e.g. evaluating if the user is the owner of the resource). Deferred for now.
        if resource is not None:
            # Placeholder for ABAC / resource-based policy evaluation
            pass

        # 5. Default Deny
        logger.info("authz_denied", permission=permission.value, subject=context.user_id or context.api_key_id)
        duration_ms = (time.perf_counter() - start_time) * 1000
        decision = AuthorizationDecision.deny(
            required_permission=permission.value,
            reason="Subject lacks required permissions.",
            source=DecisionSource.DEFAULT_DENY,
            evaluated_roles=context.roles,
            evaluated_permissions=context.scopes,
            evaluation_duration_ms=duration_ms
        )
        self._emit_audit(decision, context, resource)
        return decision
