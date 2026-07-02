from abc import ABC, abstractmethod


class IBackoffStrategy(ABC):
    """
    Pure mathematical abstraction for retry delays.
    Returns delay in milliseconds.
    """

    @abstractmethod
    def calculate_delay_ms(self, attempt: int) -> float:
        pass


class FixedDelay(IBackoffStrategy):
    def __init__(self, delay_ms: float):
        self.delay_ms = delay_ms

    def calculate_delay_ms(self, attempt: int) -> float:
        return self.delay_ms


class LinearBackoff(IBackoffStrategy):
    def __init__(self, base_delay_ms: float):
        self.base_delay_ms = base_delay_ms

    def calculate_delay_ms(self, attempt: int) -> float:
        return self.base_delay_ms * attempt


class ExponentialBackoff(IBackoffStrategy):
    def __init__(
        self, base_delay_ms: float, multiplier: float = 2.0, max_delay_ms: float = 60000.0
    ):
        self.base_delay_ms = base_delay_ms
        self.multiplier = multiplier
        self.max_delay_ms = max_delay_ms

    def calculate_delay_ms(self, attempt: int) -> float:
        delay = self.base_delay_ms * (self.multiplier ** (attempt - 1))
        return min(delay, self.max_delay_ms)
