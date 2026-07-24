
from app.domain.applications.context.models import ApplicationContext
from app.domain.applications.policy.interfaces import IApplicationPolicyEngine
from app.domain.applications.policy.models import ApplicationPolicy


class ApplicationPolicyEngine(IApplicationPolicyEngine):
    async def evaluate(self, context: ApplicationContext, policy: ApplicationPolicy) -> bool:
        # Enforce basic policy rules
        if not policy.allowed_capabilities:
            return False

        return True
