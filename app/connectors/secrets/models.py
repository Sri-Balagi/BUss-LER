"""Secret management models."""
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, SecretStr


class SecretType(StrEnum):
    OAUTH_TOKEN = "oauth_token"
    REFRESH_TOKEN = "refresh_token"
    API_KEY = "api_key"
    JWT_KEY = "jwt_key"
    PRIVATE_KEY = "private_key"
    CERTIFICATE = "certificate"
    WEBHOOK_SECRET = "webhook_secret"
    SERVICE_ACCOUNT = "service_account"
    ENCRYPTION_KEY = "encryption_key"
    CUSTOM = "custom"


class SecretRecord(BaseModel):
    """An encrypted secret stored in the vault. Never exposes value as plaintext."""

    secret_id: str
    connector_id: str
    profile_id: str = "default"
    secret_type: SecretType
    value: SecretStr  # Pydantic SecretStr — masked in logs/repr
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    rotated_at: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(UTC) >= self.expires_at

    def masked_display(self) -> str:
        """Returns a masked representation safe for logging."""
        raw = self.value.get_secret_value()
        if len(raw) <= 8:
            return "***"
        return raw[:4] + "***" + raw[-4:]

    class Config:
        # Ensure SecretStr is never accidentally serialized
        json_encoders = {SecretStr: lambda v: "***"}
