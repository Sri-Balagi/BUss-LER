from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable


class ICancellationToken(ABC):
    """
    Asynchronous cancellation signal with callbacks.
    """

    @abstractmethod
    def is_cancelled(self) -> bool:
        pass

    @abstractmethod
    async def cancel(self, reason: str = "Manual cancellation") -> None:
        pass

    @abstractmethod
    def get_reason(self) -> str | None:
        pass

    @abstractmethod
    def register_callback(self, callback: Callable[[], Awaitable[None]]) -> None:
        pass
