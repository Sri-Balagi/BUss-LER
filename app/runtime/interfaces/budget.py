from abc import ABC, abstractmethod


class IExecutionBudget(ABC):
    """
    Resource limits for a given execution scope.
    """

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        pass

    @property
    @abstractmethod
    def max_time_ms(self) -> int:
        pass

    @property
    @abstractmethod
    def max_recursion_depth(self) -> int:
        pass

    @property
    @abstractmethod
    def max_retries(self) -> int:
        pass

    @property
    @abstractmethod
    def max_cost_cents(self) -> int:
        pass
