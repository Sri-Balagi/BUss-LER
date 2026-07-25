"""Canonical User and Organization models."""
from __future__ import annotations
from app.connectors.canonical.base import CanonicalObject


class CanonicalUser(CanonicalObject):
    email: str = ""
    name: str = ""
    display_name: str | None = None
    username: str | None = None
    avatar_url: str | None = None
    phone: str | None = None
    timezone: str | None = None
    locale: str | None = None
    is_active: bool = True
    role: str | None = None


class CanonicalOrganization(CanonicalObject):
    name: str = ""
    display_name: str | None = None
    domain: str | None = None
    website: str | None = None
    member_count: int | None = None
    avatar_url: str | None = None
