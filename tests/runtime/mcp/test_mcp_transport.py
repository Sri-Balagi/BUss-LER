import pytest
import asyncio
from app.runtime.mcp.transport.sse import SSETransport

@pytest.mark.asyncio
async def test_sse_transport_send_receive():
    transport = SSETransport()
    await transport.start()
    
    await transport.send({"test": "message"})
    
    gen = transport.receive()
    msg = await anext(gen)
    assert msg == {"test": "message"}
    
    await transport.stop()
    
    # Next should raise StopAsyncIteration since queue receives None
    with pytest.raises(StopAsyncIteration):
        await anext(gen)
