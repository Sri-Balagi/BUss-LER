import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from app.runtime.mcp.interfaces import IMCPTransport


class SSETransport(IMCPTransport):
    """
    Server-Sent Events (SSE) implementation of the MCP Transport.
    Usually involves a GET endpoint for the event stream and a POST endpoint for incoming messages.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False
        # Push a None to unblock consumers
        await self._queue.put(None) # type: ignore

    async def send(self, message: dict[str, Any]) -> None:
        """
        In SSE, the server 'sends' by yielding to the active HTTP connection.
        This method pushes to a queue that the SSE endpoint consumes.
        """
        if self._running:
            await self._queue.put(message)

    async def receive(self) -> AsyncGenerator[dict[str, Any], None]:
        """
        Yields messages from the queue to the client.
        """
        while self._running:
            message = await self._queue.get()
            if message is None:
                break
            yield message

    async def handle_post(self, message: dict[str, Any]) -> None:
        """
        Called by the POST endpoint to simulate the client sending a message to the server.
        Wait, IMCPTransport's receive is for the SERVER to receive messages from the client,
        or for the CLIENT to receive from the SERVER?
        Since we are implementing an MCP Server, 'send' sends to the client,
        and 'handle_post' receives from the client.
        """
        # In a real implementation, handle_post would push into a different queue
        # or invoke the IMCPServer directly.
        pass
