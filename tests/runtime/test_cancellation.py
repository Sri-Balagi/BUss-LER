import asyncio
from app.runtime.session.cancellation import CancellationToken

def test_cancellation_token_basic():
    async def _run():
        token = CancellationToken()
        assert not token.is_cancelled()
        
        await token.cancel(reason="timeout")
        assert token.is_cancelled()
        assert token.get_reason() == "timeout"
    asyncio.run(_run())

def test_cancellation_token_callbacks():
    async def _run():
        token = CancellationToken()
        callback_fired = False
        
        async def my_callback():
            nonlocal callback_fired
            callback_fired = True
            
        token.register_callback(my_callback)
        
        await token.cancel()
        assert callback_fired
    asyncio.run(_run())

def test_cancellation_token_late_callback():
    async def _run():
        token = CancellationToken()
        await token.cancel()
        
        callback_fired = False
        
        async def my_callback():
            nonlocal callback_fired
            callback_fired = True
            
        token.register_callback(my_callback)
        await asyncio.sleep(0.01)
        assert callback_fired
    asyncio.run(_run())
