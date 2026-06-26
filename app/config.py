"""BizOS application settings.

Uses Pydantic Settings to load configuration from environment variables
and .env files. All external service credentials are validated at startup.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Supabase ---
    supabase_url: str
    supabase_key: str

    # --- Qdrant ---
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "memories"
    qdrant_vector_size: int = 768  # Fully configurable default
    qdrant_distance_metric: str = "Cosine"

    # --- Gemini ---
    gemini_api_key: str

    # --- App ---
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "INFO"

    # --- Gemini Model Names ---
    gemini_pro_model: str = "gemini-2.5-pro"
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    
    # --- Feature Flags ---
    enable_background_processing: bool = True
    enable_ai_summarization: bool = True
    enable_vector_storage: bool = True

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Create and return application settings.

    Uses lru_cache so that environment variables are only read from
    disk once per application lifecycle.
    """
    return Settings()
