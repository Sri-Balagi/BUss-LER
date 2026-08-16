from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.bootstrap.container import get_container
from app.interfaces.http.v1.schemas.response import BizOSResponse
from app.runtime.mcp.bridge import MCPBridge
from app.runtime.mcp.models import MCPCallRequest, MCPNegotiationRequest
from app.runtime.mcp.transport.sse import SSETransport

mcp_router = APIRouter(tags=["MCP"])

def _get_bridge() -> MCPBridge:
    return get_container().resolve(MCPBridge)


# We maintain active transports per session/client
_active_transports: dict[str, SSETransport] = {}


@mcp_router.get("/sse")
async def mcp_sse(request: Request):
    """
    Establishes an SSE connection for an MCP Client.
    """
    transport = SSETransport()
    await transport.start()

    # Store transport by some connection ID (using client host for simplicity here)
    client_id = request.client.host if request.client else "unknown"
    _active_transports[client_id] = transport

    async def event_generator():
        try:
            async for message in transport.receive():
                if await request.is_disconnected():
                    break
                yield message
        finally:
            await transport.stop()
            if client_id in _active_transports:
                del _active_transports[client_id]

    return EventSourceResponse(event_generator())


@mcp_router.post("/messages")
async def mcp_messages(request: Request, payload: dict):
    """
    Receives JSON-RPC messages from the MCP Client.
    """
    # Route based on JSON-RPC method (simplified for MVP)
    method = payload.get("method")
    params = payload.get("params", {})
    message_id = payload.get("id")

    client_id = request.client.host if request.client else "unknown"
    transport = _active_transports.get(client_id)

    if not transport:
        return BizOSResponse.fail("no_connection", "No active SSE connection found.")

    bridge = _get_bridge()

    if method == "initialize":
        init_req = MCPNegotiationRequest(**params)
        init_res = await bridge.negotiate(init_req)
        response = init_res.model_dump(mode="json")

    elif method == "tools/list":
        response = await bridge.list_tools()

    elif method == "tools/call":
        call_req = MCPCallRequest(**params)
        call_res = await bridge.call_tool(call_req)
        response = call_res.model_dump(mode="json")

    else:
        return BizOSResponse.fail("method_not_found", f"Method {method} not supported.")

    # Send response back via SSE
    if response and message_id:
        await transport.send({
            "jsonrpc": "2.0",
            "id": message_id,
            "result": response
        })

    return BizOSResponse.ok(data={"status": "accepted"})
