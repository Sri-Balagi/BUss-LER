from app.connectors.sdk.manifest import ConnectorManifest, ConnectorComplianceLevel

MANIFEST = ConnectorManifest(
    connector_id="microsoft_onenote",
    display_name="Microsoft OneNote",
    version="2.0.0",
    provider="microsoft",
    description="Enterprise Microsoft OneNote connector for managing notebooks, sections, and pages.",
    compliance_level=ConnectorComplianceLevel.ENTERPRISE_CERTIFIED,
    family="productivity",
    webhook_support=True,
    capabilities=[
        "productivity.notes.create",
        "productivity.notes.update",
        "productivity.notes.delete",
        "productivity.notes.list",
        "productivity.notes.get",
        "productivity.notes.search",
        "productivity.notes.copy",
        "productivity.notes.move",
        "productivity.notebooks.create",
        "productivity.notebooks.list",
        "productivity.sections.create",
        "productivity.sections.list",
    ],
    feature_flags={
        "enable_embedded_images": True,
        "enable_embedded_files": True,
        "enable_page_tags": True,
    },
)
