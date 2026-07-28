"""Declarative Business Rule Engine for validating rules and policies across modules."""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class BusinessRule(BaseModel):
    """Declarative Business Rule definition."""

    rule_id: str
    module_id: str
    name: str
    description: str
    entity_type: str
    priority: int = 100
    is_active: bool = True


class BusinessRuleEngine:
    """Evaluates business rules registered by modules."""

    def __init__(self) -> None:
        self._rules: dict[str, tuple[BusinessRule, Callable[[Any], bool]]] = {}

    def register_rule(self, rule: BusinessRule, validator: Callable[[Any], bool]) -> None:
        """Register a business rule with its validation function."""
        self._rules[rule.rule_id] = (rule, validator)

    def evaluate_rules(self, entity_type: str, target: Any) -> tuple[bool, list[str]]:
        """Evaluate all active rules for a specific entity type."""
        violations = []
        for rule, validator in self._rules.values():
            if rule.is_active and rule.entity_type == entity_type:
                try:
                    if not validator(target):
                        violations.append(f"Rule '{rule.name}' failed: {rule.description}")
                except Exception as e:
                    violations.append(f"Rule '{rule.name}' evaluation error: {e}")

        return len(violations) == 0, violations
