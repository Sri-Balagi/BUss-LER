from app.connectors.sdk.manifest import ConnectorManifest, ConnectorComplianceLevel
from app.connectors.sdk.permissions import ConnectorPermission

MANIFEST = ConnectorManifest(
    connector_id="google_calendar",
    display_name="Google Calendar",
    version="4.0.0",
    provider="google",
    description="Production-grade Google Calendar connector.",
    compliance_level=ConnectorComplianceLevel.ENTERPRISE_CERTIFIED,
    family="google_workspace",
    parent_connector_id="google_workspace",
    capabilities=[
        "calendar.events.list",
        "calendar.events.create",
        "calendar.events.update",
        "calendar.events.delete",
        "calendar.calendars.list",
    ],
    permissions=[
        ConnectorPermission.READ_CALENDAR,
        ConnectorPermission.WRITE_CALENDAR,
    ],
    supported_execution_modes=["SIMULATION", "PRODUCTION"],
    auth_type="oauth2",
    webhook_support=True,
    multi_account_support=True,
)
