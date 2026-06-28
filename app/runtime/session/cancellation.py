import asyncio
from typing import Callable, Awaitable
from app.runtime.interfaces.cancellation import ICancellationToken

class CancellationToken(ICancellationToken):
    """
    Async-safe cancellation token with a callback registry.
    """
    def __init__(self):
        self._cancelled = False
        self._reason: str | None = None
        self._callbacks: list[Callable[[], Awaitable[None]]] = []
        self._lock = asyncio.Lock()

    def is_cancelled(self) -> bool:
        return self._cancelled

    def get_reason(self) -> str | None:
        return self._reason

    def register_callback(self, callback: Callable[[], Awaitable[None]]) -> None:
        if self._cancelled:
            # If already cancelled, execute immediately as a fire-and-forget task
            asyncio.create_task(callback())
        else:
            self._callbacks.append(callback)

    async def cancel(self, reason: str = "Manual cancellation") -> None:
        """
        Signals cancellation and awaits all registered callbacks.
        """
        async with self._lock:
            if self._cancelled:
                return
            self._cancelled = True
            self._reason = reason

        # Fire callbacks concurrently
        if self._callbacks:
            await asyncio.gather(*(cb() for cb in self._callbacks), return_exceptions=True)
