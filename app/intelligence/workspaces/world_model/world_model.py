from typing import Any, Dict


class Belief:
    def __init__(self, key: str, value: Any, confidence: float):
        self.key = key
        self.value = value
        self.confidence = confidence

class BusinessWorldModel:
    """
    Differentiates beliefs from facts. Derives high-level states
    (e.g., "customer sentiment declining") from the factual EnterpriseContext.
    """
    def __init__(self):
        self.beliefs: dict[str, Belief] = {}

    def update_belief(self, belief: Belief):
        self.beliefs[belief.key] = belief

    def get_belief(self, key: str) -> Belief:
        return self.beliefs.get(key)
