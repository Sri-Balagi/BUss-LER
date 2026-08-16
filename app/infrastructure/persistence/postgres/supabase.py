"""Supabase client wrapper.

Provides a singleton connection to Supabase for the application lifecycle.
"""

from supabase import AsyncClient, create_async_client

from app.config import Settings


class SupabaseService:
    """Wrapper for the Supabase Python client."""

    _instance: AsyncClient | None = None

    @classmethod
    async def get_client(cls, settings: Settings) -> AsyncClient:
        """Get or initialize the Supabase client singleton."""
        if cls._instance is None:
            cls._instance = await create_async_client(
                settings.supabase_url,
                settings.supabase_key,
            )
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
