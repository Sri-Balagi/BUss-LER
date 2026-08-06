import asyncio
from app.connectors.oauth.token_repository import OAuthTokenRepository

async def main():
    repo = OAuthTokenRepository()
    token = await repo.get('microsoft', 'default_tenant')
    if token:
        print(f"Microsoft token found: {token.access_token[:40]}...")
    else:
        print("No Microsoft token in DB - authentication required")

asyncio.run(main())
