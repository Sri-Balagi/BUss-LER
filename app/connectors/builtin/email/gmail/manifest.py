from app.connectors.sdk.manifest import ConnectorManifest, ConnectorComplianceLevel
from app.connectors.sdk.permissions import ConnectorPermission

MANIFEST = ConnectorManifest(
    connector_id="gmail",
    display_name="Google Gmail",
    version="3.0.0",
    provider="google",
    description="Connects to Google Gmail to read, search, and send emails.",
    compliance_level=ConnectorComplianceLevel.CERTIFIED,
    family="communication",
    parent_connector_id="google_workspace",
    capabilities=[
        "email.outbound.send",
        "email.inbox.list",
        "email.inbox.read",
        "email.inbox.search",
        "email.labels.list",
        "email.attachments.download",
        "email.threads.list",
    ],
    permissions=[
        ConnectorPermission.MODIFY_EMAIL,
        ConnectorPermission.SEND_EMAIL,
        ConnectorPermission.READ_EMAIL,
    ],
    supported_execution_modes=["SIMULATION", "PRODUCTION"],
    auth_type="oauth2",
    webhook_support=True,
    multi_account_support=True,
)
