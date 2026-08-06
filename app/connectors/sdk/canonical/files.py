"""Canonical Files Business SDK — re-exports from existing canonical models.

Providers:
  Google Drive      → CanonicalFile, CanonicalFolder, CanonicalPermission, CanonicalRevision
  Microsoft OneDrive→ CanonicalFile, CanonicalFolder, CanonicalDeltaChange
  SharePoint        → CanonicalFile, CanonicalFolder, CanonicalSharePointSite
  Notion            → CanonicalNotionPage, CanonicalNotionDatabase
"""
from app.connectors.sdk.canonical_crm import (  # noqa: F401 - re-exported
    CanonicalFile,
    CanonicalFolder,
    CanonicalPermission,
    CanonicalRevision,
    CanonicalComment,
    CanonicalDriveActivity,
) if False else None  # type: ignore

# Re-export from the monolithic canonical module for backward-compat.
try:
    from app.connectors.sdk.canonical import (  # noqa: F401
        CanonicalFile,          # type: ignore
        CanonicalFolder,        # type: ignore
        CanonicalPermission,    # type: ignore
        CanonicalRevision,      # type: ignore
    )
except ImportError:
    pass
