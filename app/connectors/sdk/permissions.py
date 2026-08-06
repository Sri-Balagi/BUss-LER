"""BizOS Connector Permission Scopes & Verification Engine — Phase 2 Production Grade"""

from enum import Enum
from typing import List, Set
from pydantic import BaseModel


class ConnectorPermission(str, Enum):
    """Explicit permission scopes for connector actions."""
    # ── Email ─────────────────────────────────────────────────────────────────
    READ_EMAIL = "READ_EMAIL"
    SEND_EMAIL = "SEND_EMAIL"
    MODIFY_EMAIL = "MODIFY_EMAIL"

    # ── Google Drive ──────────────────────────────────────────────────────────
    READ_DRIVE = "READ_DRIVE"
    WRITE_DRIVE = "WRITE_DRIVE"
    DELETE_DRIVE = "DELETE_DRIVE"
    MANAGE_DRIVE_PERMISSIONS = "MANAGE_DRIVE_PERMISSIONS"
    EXPORT_DRIVE = "EXPORT_DRIVE"
    WATCH_DRIVE = "WATCH_DRIVE"
    READ_DRIVE_ACTIVITY = "READ_DRIVE_ACTIVITY"
    MANAGE_SHARED_DRIVES = "MANAGE_SHARED_DRIVES"

    # ── Google Calendar ───────────────────────────────────────────────────────
    READ_CALENDAR = "READ_CALENDAR"
    WRITE_CALENDAR = "WRITE_CALENDAR"
    MANAGE_CALENDAR_ACL = "MANAGE_CALENDAR_ACL"
    WATCH_CALENDAR = "WATCH_CALENDAR"

    # ── Microsoft OneDrive ────────────────────────────────────────────────────
    READ_ONEDRIVE = "READ_ONEDRIVE"
    WRITE_ONEDRIVE = "WRITE_ONEDRIVE"
    DELETE_ONEDRIVE = "DELETE_ONEDRIVE"
    MANAGE_ONEDRIVE_PERMISSIONS = "MANAGE_ONEDRIVE_PERMISSIONS"
    WATCH_ONEDRIVE = "WATCH_ONEDRIVE"

    # ── Microsoft SharePoint ──────────────────────────────────────────────────
    READ_SHAREPOINT = "READ_SHAREPOINT"
    WRITE_SHAREPOINT = "WRITE_SHAREPOINT"
    DELETE_SHAREPOINT = "DELETE_SHAREPOINT"
    MANAGE_SHAREPOINT = "MANAGE_SHAREPOINT"
    WATCH_SHAREPOINT = "WATCH_SHAREPOINT"

    # ── Notion ────────────────────────────────────────────────────────────────
    READ_NOTION = "READ_NOTION"
    WRITE_NOTION = "WRITE_NOTION"
    MANAGE_NOTION = "MANAGE_NOTION"

    # ── Financial & Banking ───────────────────────────────────────────────────
    READ_FINANCIALS = "READ_FINANCIALS"
    READ_TRANSACTIONS = "READ_TRANSACTIONS"
    DISCOVER_ACCOUNTS = "DISCOVER_ACCOUNTS"
    INITIATE_PAYMENT = "INITIATE_PAYMENT"
    EXECUTE_PAYOUT = "EXECUTE_PAYOUT"

    # ── Social & Messaging ────────────────────────────────────────────────────
    READ_MESSAGES = "READ_MESSAGES"
    SEND_MESSAGES = "SEND_MESSAGES"
    READ_INSIGHTS = "READ_INSIGHTS"

    # ── Administrative ────────────────────────────────────────────────────────
    MANAGE_WEBHOOKS = "MANAGE_WEBHOOKS"
    ADMINISTER_CONNECTOR = "ADMINISTER_CONNECTOR"
    EXPORT_RESOURCES = "EXPORT_RESOURCES"
    WATCH_RESOURCES = "WATCH_RESOURCES"


class PermissionCheckResult(BaseModel):
    allowed: bool
    granted_permissions: List[ConnectorPermission]
    missing_permissions: List[ConnectorPermission]
    reason: str


def verify_connector_permissions(
    granted: List[ConnectorPermission], required: List[ConnectorPermission]
) -> PermissionCheckResult:
    """Verifies if granted permissions satisfy required permissions."""
    granted_set: Set[ConnectorPermission] = set(granted)
    required_set: Set[ConnectorPermission] = set(required)
    missing = list(required_set - granted_set)

    if not missing:
        return PermissionCheckResult(
            allowed=True,
            granted_permissions=granted,
            missing_permissions=[],
            reason="All required permissions are granted.",
        )

    return PermissionCheckResult(
        allowed=False,
        granted_permissions=granted,
        missing_permissions=missing,
        reason=f"Missing required permissions: {[m.value for m in missing]}",
    )
