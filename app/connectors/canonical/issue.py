"""Canonical project/development models."""
from __future__ import annotations
from datetime import datetime
from app.connectors.canonical.base import CanonicalObject


class CanonicalIssue(CanonicalObject):
    title: str = ""
    description: str = ""
    status: str = "open"   # open, in_progress, closed, resolved
    priority: str | None = None
    assignee_id: str | None = None
    reporter_id: str | None = None
    labels: list[str] = []
    milestone: str | None = None
    url: str | None = None
    closed_at: datetime | None = None


class CanonicalRepository(CanonicalObject):
    name: str = ""
    full_name: str = ""
    description: str = ""
    url: str | None = None
    clone_url: str | None = None
    default_branch: str = "main"
    is_private: bool = False
    star_count: int = 0
    fork_count: int = 0
    language: str | None = None


class CanonicalPullRequest(CanonicalObject):
    title: str = ""
    description: str = ""
    status: str = "open"  # open, merged, closed
    author_id: str = ""
    base_branch: str = ""
    head_branch: str = ""
    url: str | None = None
    merged_at: datetime | None = None
    merged_by: str | None = None
    review_count: int = 0
    comment_count: int = 0
