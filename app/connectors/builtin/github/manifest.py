"""GitHub Reference Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="github",
    name="GitHub Connector",
    version="1.0.0",
    description="GitHub enterprise integration for repository management, issue tracking, and PR workflows.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2,
    scopes=["repo", "user", "admin:repo_hook"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="github.issue_management",
            name="Issue Management",
            description="Manage GitHub issues, comments, and labels",
            operations=["create_issue", "list_issues", "close_issue"],
            canonical_model="CanonicalIssue",
            tool_ids=["github.create_issue"],
        ),
        CapabilityDeclaration(
            capability_id="github.repository_management",
            name="Repository Management",
            description="Access repository metadata and pull requests",
            operations=["list_repos", "get_repo"],
            canonical_model="CanonicalRepository",
        ),
    ],
    supported_events=["IssueCreatedEvent", "PullRequestCreatedEvent"],
    supported_sync_types=[SyncType.FULL, SyncType.INCREMENTAL],
    supports_webhooks=True,
    supports_polling=True,
    ai_metadata=AIMetadata(
        description="Integrates GitHub code repositories, issues, and pull requests.",
        business_vocabulary=["repository", "issue", "pull request", "branch", "commit"],
        natural_language_aliases=["GitHub", "git repo", "codebase"],
        supported_operations=["create_issue", "list_issues"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.DEVTOOLS,
        tags=["git", "code", "issues"],
        pricing="free",
    ),
)
