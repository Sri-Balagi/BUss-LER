import abc

from app.domain.applications.context.models import ApplicationContext
from app.domain.applications.policy.models import ApplicationPolicy


class IApplicationPolicyEngine(abc.ABC):
    """Engine to enforce policies on application execution."""

    @abc.abstractmethod
    async def evaluate(self, context: ApplicationContext, policy: ApplicationPolicy) -> bool:
        """Evaluate if the context meets the policy constraints."""
        pass
