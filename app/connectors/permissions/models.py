"""Connector permission models."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class PermissionScope(StrEnum):
    """Standard permission scopes available to connectors."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    WEBHOOK = "webhook"
    OFFLINE_ACCESS = "offline_access"
    # Fine-grained scopes
    READ_USERS = "read:users"
    READ_MESSAGES = "read:messages"
    SEND_MESSAGES = "send:messages"
    READ_FILES = "read:files"
    WRITE_FILES = "write:files"
    READ_ISSUES = "read:issues"
    WRITE_ISSUES = "write:issues"
    READ_CALENDAR = "read:calendar"
    WRITE_CALENDAR = "write:calendar"
    READ_CONTACTS = "read:contacts"
    READ_PAYMENTS = "read:payments"
    WRITE_PAYMENTS = "write:payments"


class ConnectorPermission(BaseModel):
    """A single permission granted to or required by a connector."""

    scope: PermissionScope
    description: str = ""
    required: bool = True
    reason: str = Field(default="", description="Why this permission is needed.")

    def __hash__(self) -> int:
        return hash(self.scope)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ConnectorPermission):
            return self.scope == other.scope
        return NotImplemented


class PermissionSet(BaseModel):
    """Immutable set of permissions for a connector."""

    permissions: list[ConnectorPermission] = Field(default_factory=list)

    def has(self, scope: PermissionScope) -> bool:
        return any(p.scope == scope for p in self.permissions)

    def required_scopes(self) -> list[PermissionScope]:
        return [p.scope for p in self.permissions if p.required]

    def optional_scopes(self) -> list[PermissionScope]:
        return [p.scope for p in self.permissions if not p.required]

    def scope_strings(self) -> list[str]:
        """Returns scope strings suitable for OAuth scope parameter."""
        return [p.scope.value for p in self.permissions]
