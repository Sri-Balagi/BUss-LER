"""Gmail Reference Connector Implementation."""
from __future__ import annotations
from typing import Any
from app.connectors.sdk.polling import PollingConnector
from app.connectors.sdk.oauth import OAuthPKCEConnector
from app.connectors.canonical.message import CanonicalEmail


class GmailConnector(OAuthPKCEConnector, PollingConnector):
    """Reference skeleton for Gmail OAuth2 PKCE + Polling connector."""

    def __init__(self, connector_id: str = "gmail", profile_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(connector_id=connector_id, profile_id=profile_id, **kwargs)

    def get_capabilities(self) -> list[str]:
        return ["gmail.email_sync"]

    def _generate_pkce_pair(self) -> tuple[str, str]:
        return ("verifier_mock", "challenge_mock")

    def _build_auth_url(self, state: str) -> str:
        return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={self._client_id}&state={state}"

    async def _exchange_code(self, code: str, state: str) -> dict[str, Any]:
        return {"access_token": "mock_gmail_token"}

    async def _refresh_access_token(self) -> dict[str, Any]:
        return {"access_token": "mock_refreshed_gmail_token"}

    async def poll(self) -> Any:
        return await self.run_incremental_sync()

    async def _fetch_page(self, cursor: str | None = None) -> tuple[list[dict[str, Any]], str | None]:
        mock_msg = {"id": "msg_001", "subject": "Welcome to BizOS", "from": "info@bizos.ai"}
        return [mock_msg], None

    async def _process_record(self, record: dict[str, Any]) -> None:
        _ = CanonicalEmail(
            source_connector=self.connector_id,
            source_id=record["id"],
            subject=record["subject"],
            sender=record["from"],
        )
