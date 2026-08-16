from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import re
from app.connectors.sdk.canonical import CanonicalNote

def _parse_dt(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)

def map_notebook(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "notebook_id": raw["id"],
        "display_name": raw.get("displayName", "Unnamed Notebook"),
        "is_default": raw.get("isDefault", False),
        "is_shared": raw.get("isShared", False),
        "links": raw.get("links", {})
    }

def map_section(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "section_id": raw["id"],
        "display_name": raw.get("displayName", "Unnamed Section"),
        "is_default": raw.get("isDefault", False),
        "parent_notebook_id": raw.get("parentNotebook", {}).get("id")
    }

def map_page(raw: Dict[str, Any]) -> CanonicalNote:
    """Map a raw Graph OneNote Page to CanonicalNote."""
    parent_section = raw.get("parentSection", {})
    parent_notebook = raw.get("parentNotebook", {})
    
    # Try to extract tags from content_html if it was provided (we do this in the connector)
    tags = []
    content = raw.get("content_html")
    if content:
        # Very basic tag extraction from meta tags or data-tag attributes
        # OneNote HTML often has <meta name="tag" content="urgent">
        tag_matches = re.findall(r'<meta[^>]*name=["\']tag["\'][^>]*content=["\']([^"\']+)["\']', content)
        tags.extend(tag_matches)
        
    return CanonicalNote(
        note_id=raw["id"],
        notebook_id=parent_notebook.get("id", ""),
        section_id=parent_section.get("id", ""),
        section_name=parent_section.get("displayName", ""),
        title=raw.get("title", "Untitled Page"),
        content_html=content,
        created_at=_parse_dt(raw.get("createdDateTime")),
        modified_at=_parse_dt(raw.get("lastModifiedDateTime")),
        web_url=raw.get("links", {}).get("oneNoteWebUrl", {}).get("href"),
        self_url=raw.get("self"),
        tags=tags
    )

def map_page_preview(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "preview_text": raw.get("previewText", ""),
        "links": raw.get("links", {})
    }
