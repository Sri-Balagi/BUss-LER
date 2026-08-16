from app.connectors.sdk.manifest import ConnectorManifest, ConnectorComplianceLevel

MANIFEST = ConnectorManifest(
    connector_id="microsoft_todo",
    display_name="Microsoft To Do",
    version="2.0.0",
    provider="microsoft",
    description="Enterprise Microsoft To Do connector for managing tasks, checklists, and linked resources.",
    compliance_level=ConnectorComplianceLevel.ENTERPRISE_CERTIFIED,
    family="productivity",
    webhook_support=False,  # Graph API for To Do doesn't support full webhooks yet
    capabilities=[
        "productivity.tasks.create",
        "productivity.tasks.update",
        "productivity.tasks.complete",
        "productivity.tasks.delete",
        "productivity.tasks.list",
        "productivity.tasks.get",
        "productivity.tasks.search",
        "productivity.task_lists.create",
        "productivity.task_lists.list",
        "productivity.task_lists.delete",
    ],
    feature_flags={
        "enable_recurrence": True,
        "enable_reminders": True,
        "enable_checklists": True,
        "enable_linked_resources": True,
    },
)
