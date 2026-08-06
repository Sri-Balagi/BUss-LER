"""BizOS Connector Permission Scopes & Verification Engine"""

from enum import Enum
from typing import List, Set
from pydantic import BaseModel


class ConnectorPermission(str, Enum):
    """Explicit permission scopes for connector actions."""
    # Email Permissions
    READ_EMAIL = "READ_EMAIL"
    SEND_EMAIL = "SEND_EMAIL"
    MODIFY_EMAIL = "MODIFY_EMAIL"

    # Drive & Files Permissions
    READ_DRIVE = "READ_DRIVE"
    WRITE_DRIVE = "WRITE_DRIVE"
    DELETE_DRIVE = "DELETE_DRIVE"

    # Calendar Permissions
    READ_CALENDAR = "READ_CALENDAR"
    WRITE_CALENDAR = "WRITE_CALENDAR"

    # CRM Permissions
    READ_CONTACTS = "READ_CONTACTS"
    WRITE_CONTACTS = "WRITE_CONTACTS"
    READ_ACCOUNTS = "READ_ACCOUNTS"
    WRITE_ACCOUNTS = "WRITE_ACCOUNTS"
    READ_DEALS = "READ_DEALS"
    WRITE_DEALS = "WRITE_DEALS"
    READ_LEADS = "READ_LEADS"
    WRITE_LEADS = "WRITE_LEADS"
    READ_TASKS = "READ_TASKS"
    WRITE_TASKS = "WRITE_TASKS"
    READ_EVENTS = "READ_EVENTS"
    WRITE_EVENTS = "WRITE_EVENTS"
    READ_CUSTOM_OBJECTS = "READ_CUSTOM_OBJECTS"
    WRITE_CUSTOM_OBJECTS = "WRITE_CUSTOM_OBJECTS"

    # Financial & Banking Permissions
    READ_FINANCIALS = "READ_FINANCIALS"
    READ_TRANSACTIONS = "READ_TRANSACTIONS"
    DISCOVER_ACCOUNTS = "DISCOVER_ACCOUNTS"
    INITIATE_PAYMENT = "INITIATE_PAYMENT"
    EXECUTE_PAYOUT = "EXECUTE_PAYOUT"

    # Social & Messaging Permissions
    READ_MESSAGES = "READ_MESSAGES"
    SEND_MESSAGES = "SEND_MESSAGES"
    READ_INSIGHTS = "READ_INSIGHTS"

    # Administrative Permissions
    MANAGE_WEBHOOKS = "MANAGE_WEBHOOKS"
    ADMINISTER_CONNECTOR = "ADMINISTER_CONNECTOR"


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
