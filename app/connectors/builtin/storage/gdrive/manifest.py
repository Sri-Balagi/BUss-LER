from app.connectors.sdk.manifest import ConnectorManifest, ConnectorComplianceLevel
from app.connectors.sdk.permissions import ConnectorPermission

MANIFEST = ConnectorManifest(
    connector_id="google_drive",
    display_name="Google Drive",
    version="4.0.0",
    provider="google",
    description="Production-grade Google Drive connector. Provides full access to Google Drive API v3 including files, folders, shared drives, permissions, revisions, comments, labels, activity tracking, delta sync, and push notifications.",
    compliance_level=ConnectorComplianceLevel.ENTERPRISE_CERTIFIED,
    family="google_workspace",
    parent_connector_id="google_workspace",
    capabilities=[
        "storage.files.upload",
        "storage.files.download",
        "storage.files.delete",
        "storage.files.copy",
        "storage.files.search",
        "storage.files.move",
        "storage.files.share",
        "storage.files.version_history",
        "storage.files.restore_version",
        "storage.folders.create",
        "storage.folders.list",
        "storage.folders.delete",
        "storage.sync.delta",
    ],
    permissions=[
        ConnectorPermission.READ_DRIVE,
        ConnectorPermission.WRITE_DRIVE,
    ],
    supported_execution_modes=["SIMULATION", "DRY_RUN", "PRODUCTION"],
    auth_type="oauth2",
    webhook_support=True,
    multi_account_support=True,
)
