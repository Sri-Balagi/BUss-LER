from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.connectors.sdk.canonical import CanonicalDriveItem

def _parse_dt(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)

def map_drive_item(raw: Dict[str, Any]) -> CanonicalDriveItem:
    """Map a raw Graph DriveItem to CanonicalDriveItem."""
    item_type = "folder" if "folder" in raw else "file"
    
    parent_ref = raw.get("parentReference", {})
    parent_path = parent_ref.get("path")
    if parent_path and parent_path.startswith("/drive/root:"):
        parent_path = parent_path[12:] or "/"
    
    # Extract mimetype from file facet if present
    mime_type = raw.get("file", {}).get("mimeType")
    
    return CanonicalDriveItem(
        item_id=raw["id"],
        name=raw.get("name", "Unknown"),
        item_type=item_type,
        mime_type=mime_type,
        size_bytes=raw.get("size"),
        parent_path=parent_path,
        web_url=raw.get("webUrl"),
        download_url=raw.get("@microsoft.graph.downloadUrl"),
        created_at=_parse_dt(raw.get("createdDateTime")),
        modified_at=_parse_dt(raw.get("lastModifiedDateTime")),
        etag=raw.get("eTag"),
        ctag=raw.get("cTag"),
        version=None
    )

def map_drive_item_list(raw_list: List[Dict[str, Any]]) -> List[CanonicalDriveItem]:
    return [map_drive_item(item) for item in raw_list]

def map_permission(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map Graph permission object to standard dict."""
    granted_to = raw.get("grantedToV2", {}).get("user", {})
    return {
        "permission_id": raw.get("id"),
        "roles": raw.get("roles", []),
        "user_email": granted_to.get("email"),
        "user_name": granted_to.get("displayName"),
        "link": raw.get("link", {}).get("webUrl")
    }

def map_version(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map Graph DriveItemVersion object to standard dict."""
    last_modified_by = raw.get("lastModifiedBy", {}).get("user", {})
    return {
        "version_id": raw.get("id"),
        "modified_at": _parse_dt(raw.get("lastModifiedDateTime")).isoformat(),
        "modified_by_name": last_modified_by.get("displayName"),
        "modified_by_email": last_modified_by.get("email"),
        "size_bytes": raw.get("size")
    }
