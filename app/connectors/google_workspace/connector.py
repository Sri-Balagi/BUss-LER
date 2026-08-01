"""Google Workspace Parent Ecosystem Connector

Parent connector orchestrating auth, token lifecycle, account discovery,
and child connectors (Gmail, Google Drive, Google Calendar, Docs, Sheets, Meet, Contacts).
"""

from typing import Any, Dict, List, Optional
import structlog

from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities, ConnectorOperatingMode
from app.connectors.google_workspace.auth_manager import GoogleWorkspaceAuthProvider
from app.connectors.auth.vault import ConnectorAuthVault
from app.domain.shared.context import ExecutionContext

logger = structlog.get_logger(__name__)


class GoogleWorkspaceConnector(BaseConnector):
    """Parent connector managing Google Workspace authentication and child services."""

    def __init__(self):
        self._child_connectors: Dict[str, BaseConnector] = {}

    @property
    def connector_id(self) -> str:
        return "google_workspace"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="google_workspace",
            display_name="Google Workspace Ecosystem",
            version="3.0.0",
            family="google_workspace",
            supports_realtime=True,
            supports_polling=True,
            supported_actions=[
                "workspace_auth_status",
                "workspace_refresh_tokens",
                "workspace_list_services",
                "send_email",
                "read_inbox",
                "search_messages",
                "upload_file",
                "list_files",
                "list_events",
                "create_event",
            ],
            required_scopes=[
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/calendar",
            ],
            auth_type="oauth2",
            webhook_support=True,
            multi_account_support=True,
            operating_mode=ConnectorOperatingMode.PRODUCTION_OAUTH_MODE,
        )

    def register_child_connector(self, child: BaseConnector) -> None:
        """Registers a child service (Gmail, Drive, Calendar, Docs, Sheets, etc.)."""
        self._child_connectors[child.connector_id] = child
        logger.info(
            "Registered child service under GoogleWorkspaceConnector",
            child_id=child.connector_id,
        )

    async def execute_action(
        self, action: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        """Routes parent workspace actions or delegates to child service."""
        if action == "workspace_auth_status":
            tokens = ConnectorAuthVault.get_tokens("google_workspace")
            return {
                "status": "AUTHENTICATED" if tokens else "UNCONFIGURED",
                "has_access_token": bool(tokens and tokens.get("access_token")),
                "has_refresh_token": bool(tokens and tokens.get("refresh_token")),
                "registered_services": list(self._child_connectors.keys()),
            }

        if action == "workspace_refresh_tokens":
            res = await GoogleWorkspaceAuthProvider.refresh_workspace_tokens(
                client_id=params.get("client_id", ""),
                client_secret=params.get("client_secret", ""),
            )
            return res

        if action == "workspace_list_services":
            return {
                "parent_connector_id": self.connector_id,
                "services": [c.get_metadata() for c in self._child_connectors.values()],
            }

        # Delegate action to child connector supporting it
        for child in self._child_connectors.values():
            if action in child.capabilities.supported_actions:
                return await child.execute_action(action, params, context)

        raise ValueError(f"Action '{action}' is not supported by Google Workspace ecosystem.")

    async def health_check(self) -> Dict[str, Any]:
        """Verifies health of workspace auth and all child connectors."""
        tokens = ConnectorAuthVault.get_tokens("google_workspace")
        child_health = {}
        for cid, child in self._child_connectors.items():
            child_health[cid] = await child.health_check()

        return {
            "connector_id": self.connector_id,
            "auth_vault_configured": bool(tokens),
            "status": "ok" if tokens else "unconfigured",
            "child_services": child_health,
        }
