"""BizOS v6.0.0 — Application Settings.

Uses pydantic-settings to load configuration from environment variables and .env files.
All mandatory settings are validated at startup — the application will not start if
required values are missing or invalid.

Settings reference: configs/settings_reference.md
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Required settings (no defaults): supabase_url, supabase_key, gemini_api_key
    All other settings have production-safe defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Supabase (Required) ───────────────────────────────────────────────────
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon/service key")

    # ── Qdrant ────────────────────────────────────────────────────────────────
    qdrant_host: str = Field("localhost", description="Qdrant host")
    qdrant_port: int = Field(6333, ge=1, le=65535, description="Qdrant port")
    qdrant_collection: str = Field("memories", description="Default Qdrant collection name")
    qdrant_vector_size: int = Field(768, ge=1, description="Embedding vector dimensions")
    qdrant_distance_metric: str = Field("Cosine", description="Vector distance metric")

    # ── Gemini (Required) ─────────────────────────────────────────────────────
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    gemini_pro_model: str = Field("gemini-2.5-pro", description="Gemini Pro model name")
    gemini_flash_model: str = Field("gemini-2.5-flash", description="Gemini Flash model name")
    gemini_embedding_model: str = Field(
        "gemini-embedding-001", description="Gemini embedding model name"
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_env: str = Field(
        "development", description="Runtime environment: development|test|production"
    )
    app_debug: bool = Field(False, description="Enable debug mode (never true in production)")
    log_level: str = Field("INFO", description="Log level: DEBUG|INFO|WARNING|ERROR")
    app_version: str = Field("6.0.0", description="Application version")

    # ── Security ──────────────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins. Restrict to specific domains in production.",
    )
    encryption_key_base64: str | None = Field(
        None, description="Base64 encoded AES-256-GCM encryption key"
    )
    jwt_secret: str | None = Field(
        None, description="Secret key for signing JWTs. If not provided, fallback is used."
    )
    bcrypt_rounds: int = Field(12, ge=4, description="Bcrypt hashing rounds")

    # ── Observability ─────────────────────────────────────────────────────────
    otel_enabled: bool = Field(False, description="Enable OpenTelemetry tracing")
    otel_exporter_otlp_endpoint: str | None = Field(
        None, description="OTLP endpoint (e.g. http://otel-collector:4318)"
    )
    metrics_token: str | None = Field(
        None, description="Token required to access the /metrics endpoint"
    )

    # ── Feature Flags ─────────────────────────────────────────────────────────
    enable_background_processing: bool = Field(
        True, description="Enable background task processing"
    )
    enable_ai_summarization: bool = Field(True, description="Enable AI-powered summarization")
    enable_vector_storage: bool = Field(True, description="Enable Qdrant vector storage")

    # ── Operational ───────────────────────────────────────────────────────────
    request_timeout_seconds: float = Field(
        30.0, gt=0, description="Default request timeout in seconds"
    )

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("supabase_url")
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            msg = "SUPABASE_URL must be a valid HTTP/HTTPS URL"
            raise ValueError(msg)
        return v.rstrip("/")

    @field_validator("supabase_key")
    @classmethod
    def validate_supabase_key(cls, v: str) -> str:
        if len(v) < 10:  # noqa: PLR2004
            msg = "SUPABASE_KEY appears invalid (too short). Check your Supabase project settings."
            raise ValueError(msg)
        return v

    @field_validator("gemini_api_key")
    @classmethod
    def validate_gemini_key(cls, v: str) -> str:
        if len(v) < 10:  # noqa: PLR2004
            msg = "GEMINI_API_KEY appears invalid (too short). Get your key from ai.google.dev."
            raise ValueError(msg)
        return v

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        allowed = {"development", "test", "staging", "production"}
        if v not in allowed:
            msg = f"APP_ENV must be one of: {', '.join(sorted(allowed))}"
            raise ValueError(msg)
        return v

    @field_validator("encryption_key_base64")
    @classmethod
    def validate_encryption_key(cls, v: str | None, info) -> str | None:
        # info.data might not have app_env if it failed validation, but assuming it did:
        env = info.data.get("app_env", "development")
        if env == "production" and not v:
            raise ValueError("ENCRYPTION_KEY_BASE64 is strictly required in production")
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str | None, info) -> str | None:
        env = info.data.get("app_env", "development")
        if env == "production" and not v:
            raise ValueError("JWT_SECRET is strictly required in production")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            msg = f"LOG_LEVEL must be one of: {', '.join(sorted(allowed))}"
            raise ValueError(msg)
        return v.upper()

    # ── Computed Properties ───────────────────────────────────────────────────

    @property
    def is_production(self) -> bool:
        """True when running in the production environment."""
        return self.app_env == "production"

    @property
    def is_test(self) -> bool:
        """True when running in the test environment."""
        return self.app_env == "test"

    @property
    def qdrant_url(self) -> str:
        """Fully-qualified Qdrant URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


@lru_cache
def get_settings() -> Settings:
    """Return the application settings singleton.

    Uses lru_cache so environment variables are read exactly once
    per application lifecycle.
    """
    _logger = logging.getLogger(__name__)
    if _logger.isEnabledFor(logging.DEBUG):
        critical_keys = ["SUPABASE_URL", "SUPABASE_KEY", "GEMINI_API_KEY"]
        for key in critical_keys:
            _logger.debug(
                "Config bootstrap check",
                extra={"key": key, "present": key in os.environ},
            )

    return Settings()
