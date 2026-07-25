"""Outlook Mail Connector Implementation."""
from __future__ import annotations
from typing import Any
from app.connectors.sdk.oauth import OAuthConnector
from app.connectors.canonical.message import CanonicalEmail


class OutlookConnector(OAuthConnector):
    """Outlook Graph API email connector implementation."""

    def __init__(self, connector_id: str = "outlook", profile_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(connector_id=connector_id, profile_id=profile_id, **kwargs)

    def get_capabilities(self) -> list[str]:
        return ["outlook.email_sync"]

    def _build_auth_url(self, state: str) -> str:
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={self._client_id}&state={state}"

    async def _exchange_code(self, code: str, state: str) -> dict[str, Any]:
        return {"access_token": "mock_outlook_token"}

    async def _refresh_access_token(self) -> dict[str, Any]:
        return {"access_token": "mock_refreshed_outlook_token"}

    async def _fetch_page(self, cursor: str | None = None) -> tuple[list[dict[str, Any]], str | None]:
        mock_msg = {"id": "outlook_001", "subject": "Quarterly Report", "from": "exec@company.com"}
        return [mock_msg], None

    async def _process_record(self, record: dict[str, Any]) -> None:
        _ = CanonicalEmail(
            source_connector=self.connector_id,
            source_id=record["id"],
            subject=record["subject"],
            sender=record["from"],
        )
