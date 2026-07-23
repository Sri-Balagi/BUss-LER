import asyncio
import httpx
import uuid
import json

async def verify_mcp():
    print("--- MCP Verification ---")
    
    # Simulating the SSE connection and sending a message to the JSON-RPC endpoint
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Check if the server is up first
        try:
            health = await client.get("/api/v1/health")
            if health.status_code != 200:
                print("API server is not running. Start it with `uvicorn app.main:app`")
                return
        except Exception:
            print("API server is not running. Start it with `uvicorn app.main:app`")
            return

        print("Testing MCP Initialize...")
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "client_info": {"name": "TestClient", "version": "1.0"},
                "capabilities": {}
            }
        }
        # In a real scenario, the response goes through SSE, but the HTTP endpoint returns accepted
        res = await client.post("/api/v1/mcp/messages", json=payload)
        print(f"Initialize accepted: {res.status_code} - {res.text}")
        
        print("Testing MCP Tools List...")
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {}
        }
        res = await client.post("/api/v1/mcp/messages", json=payload)
        print(f"Tools List accepted: {res.status_code} - {res.text}")
        
        print("MCP Verification complete.")

if __name__ == "__main__":
    asyncio.run(verify_mcp())
