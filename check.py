import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


async def check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r1 = await ac.get("/health")
        print("Health:", r1.json())
        r2 = await ac.get("/api/v1/health/memory")
        print("Memory Health:", r2.json())


if __name__ == "__main__":
    asyncio.run(check())
