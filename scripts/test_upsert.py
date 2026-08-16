import asyncio
from app.infrastructure.persistence.postgres.supabase import SupabaseService
from app.config import get_settings

async def run():
    s = await SupabaseService.get_client(get_settings())
    try:
        r = await s.table('connector_oauth_tokens').delete().eq('access_token', 'test').execute()
        print("DELETE RESPONSE:", r)
    except Exception as e:
        print("DELETE ERROR:", str(e))

if __name__ == "__main__":
    asyncio.run(run())
