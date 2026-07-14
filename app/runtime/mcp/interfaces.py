from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, Dict

from app.runtime.mcp.models import MCPCallRequest, MCPCallResponse, MCPNegotiationRequest, MCPNegotiationResponse


class IMCPTransport(ABC):
    """
    Decouples MCP protocol logic from the underlying transport (SSE, WebSocket, stdio).
    """

    @abstractmethod
    async def start(self) -> None:
        """Starts listening or connects to the transport."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Closes the transport connection."""
        pass

    @abstractmethod
    async def send(self, message: Dict[str, Any]) -> None:
        """Sends a JSON-RPC message over the transport."""
        pass

    @abstractmethod
    def receive(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Yields incoming JSON-RPC messages."""
        pass


class IMCPServer(ABC):
    """
    Interface for an MCP Server that exposes tools/capabilities to clients.
    """

    @abstractmethod
    async def negotiate(self, request: MCPNegotiationRequest) -> MCPNegotiationResponse:
        """Handles the initial capability handshake."""
        pass

    @abstractmethod
    async def list_tools(self) -> Dict[str, Any]:
        """Returns all tools available on this server."""
        pass

    @abstractmethod
    async def call_tool(self, request: MCPCallRequest) -> MCPCallResponse:
        """Executes a tool and returns the result."""
        pass


class IMCPClient(ABC):
    """
    Interface for an MCP Client that connects to remote servers.
    """

    @abstractmethod
    async def connect(self, transport: IMCPTransport) -> None:
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPCallResponse:
        pass
