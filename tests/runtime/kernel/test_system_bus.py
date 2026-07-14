import pytest
import asyncio
from app.shared.bus.system_bus import LocalSystemBus

@pytest.mark.asyncio
async def test_local_system_bus_events():
    bus = LocalSystemBus()
    
    class TestEvent:
        pass
        
    received = False
    
    async def handler(event):
        nonlocal received
        received = True
        
    bus.subscribe_event(TestEvent, handler)
    bus.publish_event(TestEvent())
    
    # Yield to event loop so the task can run
    await asyncio.sleep(0.01)
    
    assert received is True

@pytest.mark.asyncio
async def test_local_system_bus_commands():
    bus = LocalSystemBus()
    
    class TestCommand:
        pass
        
    async def handler(cmd):
        return "success"
        
    bus.register_command_handler(TestCommand, handler)
    
    result = await bus.send_command(TestCommand())
    assert result == "success"

@pytest.mark.asyncio
async def test_local_system_bus_queries():
    bus = LocalSystemBus()
    
    class TestQuery:
        pass
        
    async def handler(query):
        return "data"
        
    bus.register_query_handler(TestQuery, handler)
    
    result = await bus.execute_query(TestQuery())
    assert result == "data"
