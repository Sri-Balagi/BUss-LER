"""Connector configuration schema framework."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class ConnectorConfigSchema(BaseModel):
    """
    Strongly typed, versioned connector configuration base.

    Connectors subclass this to declare typed config fields.

    Example::

        class GitHubConfig(ConnectorConfigSchema):
            client_id: str = Field(description="GitHub OAuth App Client ID")
            client_secret: str = Field(description="OAuth Client Secret", secret=True)
            webhook_secret: str = Field(default="", secret=True)
            base_url: str = Field(default="https://api.github.com")
    """

    version: str = "1.0"

    class Config:
        extra = "allow"

    def to_dict(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Serialize config, optionally masking secret fields."""
        data = self.model_dump()
        if mask_secrets:
            for name, field_info in self.model_fields.items():
                meta = field_info.metadata or []
                if any(getattr(m, "secret", False) for m in meta):
                    if name in data and data[name]:
                        data[name] = "***"
        return data


class ConnectorConfigValidator:
    """Validates a raw config dict against a typed ConnectorConfigSchema subclass."""

    @staticmethod
    def validate(
        schema_cls: type[ConnectorConfigSchema],
        raw: dict[str, Any],
    ) -> ConnectorConfigSchema:
        """
        Parse and validate raw config dict against the schema.

        Raises:
            pydantic.ValidationError: If required fields are missing or invalid.
        """
        return schema_cls.model_validate(raw)
