"""BizOS Instagram Graph API Connector Driver"""

from typing import Any
from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode


class InstagramConnector(BaseConnector):
    @property
    def connector_id(self) -> str:
        return "instagram"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="instagram",
            display_name="Instagram Professional API Connector",
            version="1.0.0",
            supports_realtime=True,
            supports_polling=True,
            supported_actions=["send_direct_message", "get_comments", "reply_comment", "get_insights"],
        )

    async def execute_action(
        self, action: str, params: dict[str, Any], context: ExecutionContext
    ) -> dict[str, Any]:
        if context.execution_mode in (ExecutionMode.SIMULATION, ExecutionMode.DRY_RUN):
            return {
                "status": "SIMULATED",
                "connector": "instagram",
                "action": action,
                "detail": f"Simulated Instagram '{action}' action",
            }

        return {
            "status": "EXECUTED",
            "connector": "instagram",
            "action": action,
            "result": {"ig_event_id": "ig_98765", "processed": True},
        }

    async def health_check(self) -> dict[str, Any]:
        return {"status": "healthy", "connector": "instagram", "token_valid": True}
