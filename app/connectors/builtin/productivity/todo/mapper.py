from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.connectors.sdk.canonical import CanonicalTodoTask

def _parse_dt(dt_obj: Optional[Dict[str, Any]]) -> Optional[datetime]:
    if not dt_obj or "dateTime" not in dt_obj:
        return None
    try:
        # Graph API dateTimeTimeZones don't always end in Z
        dt_str = dt_obj["dateTime"]
        if not dt_str.endswith("Z") and "+" not in dt_str and "-" not in dt_str[-6:]:
            dt_str += "Z"
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None

def map_task(raw: Dict[str, Any], list_id: str) -> CanonicalTodoTask:
    """Map a raw Graph TodoTask to CanonicalTodoTask."""
    return CanonicalTodoTask(
        task_id=raw["id"],
        list_id=list_id,
        title=raw.get("title", "Untitled Task"),
        status=raw.get("status", "notStarted"),
        importance=raw.get("importance", "normal"),
        due_date=_parse_dt(raw.get("dueDateTime")),
        completed_at=_parse_dt(raw.get("completedDateTime")),
        body=raw.get("body", {}).get("content"),
        reminder_at=_parse_dt(raw.get("reminderDateTime")),
        recurrence=raw.get("recurrence"),
        categories=raw.get("categories", []),
        checklist_items=raw.get("checklistItems", []),
        linked_resources=raw.get("linkedResources", []),
    )

def map_task_list(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "list_id": raw["id"],
        "display_name": raw.get("displayName", "Unnamed List"),
        "is_shared": raw.get("isShared", False),
        "is_owner": raw.get("isOwner", True),
    }

def map_checklist_item(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "item_id": raw["id"],
        "display_name": raw.get("displayName"),
        "is_checked": raw.get("isChecked", False)
    }

def map_linked_resource(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "resource_id": raw["id"],
        "web_url": raw.get("webUrl"),
        "application_name": raw.get("applicationName"),
        "display_name": raw.get("displayName")
    }
