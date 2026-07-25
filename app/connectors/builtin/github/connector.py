"""GitHub Reference Connector Implementation."""
from __future__ import annotations
from typing import Any
from app.connectors.sdk.oauth import OAuthConnector
from app.connectors.sdk.webhook import WebhookConnector
from app.connectors.sdk.base import SyncResult, SyncType, ValidationResult, WebhookResult, ConnectorHealthResult
from app.connectors.canonical.issue import CanonicalIssue


class GitHubConnector(OAuthConnector, WebhookConnector):
    """Reference implementation of a GitHub connector combining OAuth, Webhooks, and Polling."""

    def __init__(self, connector_id: str = "github", profile_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(connector_id=connector_id, profile_id=profile_id, **kwargs)

    def get_capabilities(self) -> list[str]:
        return ["github.issue_management", "github.repository_management"]

    def _build_auth_url(self, state: str) -> str:
        return f"https://github.com/login/oauth/authorize?client_id={self._client_id}&state={state}"

    async def _exchange_code(self, code: str, state: str) -> dict[str, Any]:
        return {"access_token": "mock_gh_token", "token_type": "bearer"}

    async def _refresh_access_token(self) -> dict[str, Any]:
        return {"access_token": "mock_refreshed_gh_token"}

    def _verify_signature(self, payload_bytes: bytes, signature_header: str) -> bool:
        return True  # Reference mock verification

    async def _route_event(self, event_type: str, payload: dict[str, Any]) -> None:
        pass

    async def _fetch_page(self, cursor: str | None = None) -> tuple[list[dict[str, Any]], str | None]:
        # Mock fetching GitHub issues page
        mock_issue = {
            "id": "101",
            "title": "Bug in API authentication",
            "state": "open",
        }
        return [mock_issue], None

    async def _process_record(self, record: dict[str, Any]) -> None:
        # Convert to canonical issue
        _ = CanonicalIssue(
            source_connector=self.connector_id,
            source_id=str(record["id"]),
            title=record["title"],
            status=record["state"],
        )
