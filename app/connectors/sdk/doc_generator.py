"""BizOS Connector Documentation Generator

Automatically generates Markdown documentation from ConnectorManifest and ConnectorCapabilities.
Surfaces manifest metadata, capabilities, permissions, feature flags, execution modes, and sandbox support.
"""

from typing import Any, Dict
from app.connectors.sdk.base import BaseConnector


class ConnectorDocGenerator:
    """Generates structured markdown documentation for any connector."""

    @staticmethod
    def generate_markdown_docs(connector: BaseConnector) -> str:
        meta = connector.get_metadata()
        caps = connector.capabilities

        md = []
        md.append(f"# {meta.get('display_name', caps.display_name)} Documentation")
        md.append(f"**Connector ID**: `{caps.connector_id}`  ")
        md.append(f"**Version**: `{meta.get('version', caps.version)}`  ")
        md.append(f"**Compliance Level**: `{meta.get('compliance_level', 'CERTIFIED')}`  ")
        md.append(f"**Family**: `{meta.get('family', caps.family)}`  ")
        md.append(f"**Auth Type**: `{caps.auth_type}`  \n")

        md.append("## Description")
        md.append(f"{meta.get('description', 'Enterprise connector for BizOS platform.')}\n")

        md.append("## Supported Actions & Capabilities")
        for act in caps.supported_actions:
            md.append(f"- `{act}`")
        md.append("")

        md.append("## Feature Flags")
        flags = meta.get("feature_flags", {})
        if flags:
            for flag, enabled in flags.items():
                status_icon = "✅" if enabled else "❌"
                md.append(f"- `{flag}`: {status_icon} `{enabled}`")
        else:
            md.append("- No feature flags configured.")
        md.append("")

        md.append("## Required Permissions")
        if caps.required_scopes:
            for scope in caps.required_scopes:
                md.append(f"- `{scope}`")
        else:
            md.append("- Standard connector permissions.")
        md.append("")

        md.append("## Operational Modes & Sandbox Support")
        md.append(f"- **Sandbox / Test Mode**: `{meta.get('supports_provider_sandbox', True)}`")
        md.append(f"- **Webhook Support**: `{caps.webhook_support}`")
        md.append(f"- **Multi-Account Support**: `{caps.multi_account_support}`\n")

        return "\n".join(md)
