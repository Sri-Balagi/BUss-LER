import os

from pydantic import BaseModel, Field


class SDKConfig(BaseModel):
    """
    Shared configuration for BizOS synchronous and asynchronous SDK clients.
    Defaults can be overridden via environment variables for 12-factor compliance.
    """
    base_url: str = Field(default_factory=lambda: os.getenv("BIZOS_API_URL", "http://localhost:8000"))
    api_key: str | None = Field(default_factory=lambda: os.getenv("BIZOS_API_KEY"))
    jwt_token: str | None = Field(default_factory=lambda: os.getenv("BIZOS_JWT_TOKEN"))
    tenant_id: str | None = Field(default_factory=lambda: os.getenv("BIZOS_TENANT_ID"))
    timeout_seconds: float = 30.0
    max_retries: int = 3

    def get_auth_headers(self) -> dict[str, str]:
        """Constructs authentication headers based on config."""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        if self.tenant_id:
            headers["X-Tenant-ID"] = self.tenant_id

        return headers
