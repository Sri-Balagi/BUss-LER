import asyncio

from app.sdk.client.sync_client import BizOSClient
from app.sdk.client.async_client import AsyncBizOSClient

def verify_sync():
    print("--- Synchronous SDK Verification ---")
    with BizOSClient() as client:
        health = client.get_health()
        print(f"Health: {health.success}")
        
        workflows = client.list_active_workflows()
        print(f"Active Workflows: {workflows}")
        
        items = client.list_registry_items("ToolRegistry")
        print(f"Tool Registry Items: {len(items)}")

async def verify_async():
    print("--- Asynchronous SDK Verification ---")
    async with AsyncBizOSClient() as client:
        health = await client.get_health()
        print(f"Health: {health.success}")
        
        workflows = await client.list_active_workflows()
        print(f"Active Workflows: {workflows}")
        
        items = await client.list_registry_items("ToolRegistry")
        print(f"Tool Registry Items: {len(items)}")

if __name__ == "__main__":
    verify_sync()
    asyncio.run(verify_async())
    print("SDK Verification complete.")
