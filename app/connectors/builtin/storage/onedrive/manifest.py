from app.connectors.sdk.manifest import ConnectorManifest, ConnectorComplianceLevel

MANIFEST = ConnectorManifest(
    connector_id="microsoft_onedrive",
    display_name="Microsoft OneDrive",
    version="2.0.0",
    provider="microsoft",
    description="Enterprise Microsoft OneDrive connector for file storage, sharing, and delta sync.",
    compliance_level=ConnectorComplianceLevel.ENTERPRISE_CERTIFIED,
    family="storage",
    webhook_support=True,
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
    feature_flags={
        "enable_large_upload": True,
        "enable_delta_sync": True,
        "enable_version_history": True,
        "enable_recycle_bin": True,
    },
)
