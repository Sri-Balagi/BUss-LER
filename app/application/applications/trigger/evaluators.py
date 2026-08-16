from app.domain.applications.trigger.interfaces import IConditionEvaluator
from app.domain.applications.trigger.models import TriggerCondition, TriggerContext


class AlwaysTrueEvaluator(IConditionEvaluator):
    """A dummy evaluator that always returns True, for testing or manual triggers."""
    @property
    def condition_type(self) -> str:
        return "always_true"

    async def evaluate(self, condition: TriggerCondition, context: TriggerContext) -> bool:
        return True


class ConditionEvaluatorRegistry:
    """Registry to resolve condition evaluators dynamically."""
    def __init__(self):
        self._evaluators: dict[str, IConditionEvaluator] = {}

        # Register defaults
        self.register(AlwaysTrueEvaluator())

    def register(self, evaluator: IConditionEvaluator) -> None:
        self._evaluators[evaluator.condition_type] = evaluator

    def resolve(self, condition_type: str) -> IConditionEvaluator:
        if condition_type not in self._evaluators:
            raise ValueError(f"No condition evaluator found for type: {condition_type}")
        return self._evaluators[condition_type]
