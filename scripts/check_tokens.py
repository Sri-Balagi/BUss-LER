import asyncio
from app.infrastructure.persistence.postgres.supabase import SupabaseService
from app.config import get_settings

async def run():
    s = await SupabaseService.get_client(get_settings())
    r = await s.table('connector_oauth_tokens').select('*').execute()
    print("TOKENS in DB:")
    for row in r.data:
        print(f"- Tenant: {row['tenant_id']}, Provider: {row['provider_id']}")

if __name__ == "__main__":
    asyncio.run(run())
