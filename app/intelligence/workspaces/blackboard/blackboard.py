from abc import ABC, abstractmethod
from typing import List, Callable

class Hypothesis:
    def __init__(self, description: str):
        self.description = description

class IExecutiveBlackboard(ABC):
    @abstractmethod
    def post_hypothesis(self, hypothesis: Hypothesis) -> None:
        pass

    @abstractmethod
    def subscribe(self, topic: str, handler: Callable) -> None:
        pass

class ExecutiveBlackboard(IExecutiveBlackboard):
    """
    The ephemeral shared cognitive workspace.
    Subsystems post hypotheses, observations, recommendations, and simulations here.
    """
    def __init__(self):
        self._hypotheses: List[Hypothesis] = []
        self._subscribers: dict = {}

    def post_hypothesis(self, hypothesis: Hypothesis) -> None:
        self._hypotheses.append(hypothesis)
        if "hypotheses" in self._subscribers:
            for handler in self._subscribers["hypotheses"]:
                handler(hypothesis)

    def subscribe(self, topic: str, handler: Callable) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
