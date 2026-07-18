import abc
from typing import Dict, Any

from app.domain.applications.trigger.models import TriggerContext, TriggerCondition


class IConditionEvaluator(abc.ABC):
    """Abstraction for evaluating trigger conditions."""

    @property
    @abc.abstractmethod
    def condition_type(self) -> str:
        """The type of condition this evaluator handles (e.g., 'threshold', 'boolean')."""
        pass

    @abc.abstractmethod
    async def evaluate(self, condition: TriggerCondition, context: TriggerContext) -> bool:
        """Evaluate the condition against the context.

        Args:
            condition: The condition configuration to evaluate.
            context: The context in which the trigger fired.

        Returns:
            bool: True if the condition is met, False otherwise.
        """
        pass
