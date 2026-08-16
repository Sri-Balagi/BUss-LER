"""BizOS Background Token Refresh Scheduler

Runs background maintenance loops to proactively refresh OAuth2 tokens
nearing expiration (e.g. Google Workspace, Stripe Connect) before actions fail.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import structlog
from app.connectors.auth.vault import ConnectorAuthVault
from app.connectors.google_workspace.auth_manager import GoogleWorkspaceAuthProvider
from app.connectors.runtime.analytics import ConnectorAnalyticsTracker

logger = structlog.get_logger(__name__)


class BackgroundTokenRefreshScheduler:
    """Background task handling proactive token lifecycle maintenance."""

    _task: asyncio.Task | None = None
    _running: bool = False

    @classmethod
    async def start(cls, interval_seconds: int = 300):
        if cls._running:
            return
        cls._running = True
        cls._task = asyncio.create_task(cls._refresh_loop(interval_seconds))
        logger.info("Started BackgroundTokenRefreshScheduler", interval_seconds=interval_seconds)

    @classmethod
    async def stop(cls):
        cls._running = False
        if cls._task:
            cls._task.cancel()
            cls._task = None
        logger.info("Stopped BackgroundTokenRefreshScheduler")

    @classmethod
    async def run_refresh_cycle(cls) -> Dict[str, Any]:
        """Executes a single check and refresh cycle across vaulted tokens."""
        refreshed_count = 0
        failed_count = 0

        # Check Google Workspace tokens
        gw_tokens = ConnectorAuthVault.get_tokens("google_workspace")
        if gw_tokens and gw_tokens.get("expires_at"):
            exp = datetime.fromisoformat(gw_tokens["expires_at"])
            # Refresh if expiring within 10 minutes
            if datetime.now(timezone.utc) + timedelta(minutes=10) >= exp:
                logger.info("Proactively refreshing Google Workspace token nearing expiration")
                res = await GoogleWorkspaceAuthProvider.refresh_workspace_tokens(
                    client_id="default_client",
                    client_secret="default_secret",
                )
                if res.get("status") == "REFRESHED":
                    refreshed_count += 1
                    ConnectorAnalyticsTracker.record_token_refresh("google_workspace", True)
                else:
                    failed_count += 1
                    ConnectorAnalyticsTracker.record_token_refresh("google_workspace", False)

        return {
            "status": "COMPLETED",
            "refreshed": refreshed_count,
            "failed": failed_count,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    async def _refresh_loop(cls, interval_seconds: int):
        while cls._running:
            try:
                await cls.run_refresh_cycle()
            except Exception as exc:
                logger.error("Error in token refresh loop", error=str(exc))
            await asyncio.sleep(interval_seconds)
