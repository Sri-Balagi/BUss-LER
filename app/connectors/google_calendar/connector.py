"""BizOS Google Calendar Connector — Phase 2 Production Grade

Full production connector against Google Calendar API v3.
Supports: 20+ actions, all Calendar resource types, recurring events,
Google Meet integration, free/busy queries, delta sync, push notifications.

Same authentication model as Google Drive — single Google OAuth consent
covers both Drive and Calendar scopes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.connectors.auth.vault import ConnectorAuthVault
from app.connectors.auth.oauth_flow import UnifiedOAuthFlow
from app.connectors.sdk.base import (
    BaseConnector,
    ConnectorCapabilities,
    ConnectorOperatingMode,
    ConnectorResourceType,
    ConnectorEventType,
    ConnectorExecuteRequest,
)
from app.connectors.sdk.health import ConnectorHealthReport, ConnectorHealthStatus
from app.connectors.sdk.permissions import ConnectorPermission
from app.connectors.sdk.resilience import execute_with_resilience
from app.connectors.google_calendar.resources import (
    CalendarCalendarsResource,
    CalendarEventsResource,
    CalendarFreeBusyResource,
    CalendarWatchResource,
    CalendarSettingsResource,
)
from app.domain.shared.context import ExecutionContext

logger = structlog.get_logger(__name__)

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]


def _build_calendar_service(
    tenant_id: str = "default_tenant",
    account_id: str = "default_account",
) -> Any:
    """Build an authenticated Google Calendar API v3 service object."""
    tokens = ConnectorAuthVault.get_tokens("google", tenant_id=tenant_id, account_id=account_id)
    if not tokens:
        raise RuntimeError(
            "Google credentials not found. Authenticate via POST /api/v1/connectors/google/authenticate"
        )

    creds = Credentials(
        token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("GOOGLE_CLIENT_ID", ""),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        scopes=tokens.get("scopes", CALENDAR_SCOPES),
    )

    if ConnectorAuthVault.is_token_expired("google", tenant_id=tenant_id, account_id=account_id):
        creds.refresh(Request())
        ConnectorAuthVault.set_tokens(
            provider_id="google",
            access_token=creds.token or "",
            refresh_token=creds.refresh_token or "",
            tenant_id=tenant_id,
            account_id=account_id,
            expires_at=creds.expiry,
        )

    return build("calendar", "v3", credentials=creds, cache_discovery=False)


import hashlib
from app.perception.sources.interface import IObservationSource, PerceptionContext
from app.perception.models.observation import ExternalObservation, ObservationSourceType, UnifiedKnowledgeObject


class GoogleCalendarConnector(BaseConnector, IObservationSource):
    """Production-grade Google Calendar connector."""

    @property
    def connector_id(self) -> str:
        return "google_calendar"

    @property
    def source_id(self) -> str:
        return "google_calendar"

    @property
    def source_type(self) -> ObservationSourceType:
        return ObservationSourceType.CONNECTOR

    async def observe(self, context: PerceptionContext) -> list[ExternalObservation]:
        """Perception Layer observe implementation."""
        exec_ctx = ExecutionContext(tenant_id=context.tenant_id or "default")
        result = await self.execute(
            ConnectorExecuteRequest(
                capability_id="list_events",
                parameters={"max_results": context.limit},
                user_email=context.params.get("user_email", "user@example.com"),
            ),
            exec_ctx,
        )
        events = result.get("items", result.get("events", [])) if isinstance(result, dict) else []
        observations = []
        for event in events:
            event_id = str(event.get("id", hash(event.get("summary", ""))))
            obs = ExternalObservation(
                observation_id=event_id,
                source_id=self.connector_id,
                source_type=ObservationSourceType.CONNECTOR,
                resource_type="event",
                raw_payload=event,
                tenant_id=str(context.tenant_id) if context.tenant_id else None,
            )
            observations.append(obs)
        return observations

    def normalize(self, observation: ExternalObservation) -> UnifiedKnowledgeObject:
        """Perception Layer normalize implementation."""
        payload = observation.raw_payload
        event_id = str(payload.get("id", observation.observation_id))
        uko_id = hashlib.sha256(f"{self.connector_id}:{event_id}".encode("utf-8")).hexdigest()

        summary = str(payload.get("summary", "Untitled Event"))
        description = str(payload.get("description", ""))
        html_link = payload.get("htmlLink")
        organizer = payload.get("organizer", {}).get("email") if isinstance(payload.get("organizer"), dict) else None

        return UnifiedKnowledgeObject(
            uko_id=uko_id,
            source_connector=self.connector_id,
            resource_type="event",
            title=summary,
            content=description or summary,
            author=organizer,
            source_url=html_link,
            metadata={"event_id": event_id, "location": payload.get("location")},
        )


    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="google_calendar",
            display_name="Google Calendar",
            version="4.0.0",
            family="google_workspace",
            parent_connector_id="google_workspace",
            supports_realtime=True,
            supports_polling=True,
            supports_streaming=False,
            supports_batch=True,
            supports_delta_sync=True,
            supported_actions=[
                # Calendars
                "list_calendars", "get_calendar", "create_calendar", "update_calendar",
                "delete_calendar", "clear_calendar",
                # ACL
                "list_acl", "create_acl", "delete_acl",
                # Events
                "list_events", "get_event", "create_event", "create_event_with_meet",
                "update_event", "delete_event", "move_event", "import_event",
                "quick_add_event",
                # Recurring
                "list_instances",
                # Free/Busy
                "get_freebusy",
                # Watch
                "watch_events", "watch_calendar_list",
                # Settings
                "list_settings", "get_setting",
                # Sync
                "sync_events",
                # Batch
                "batch",
            ],
            supported_resources=[
                ConnectorResourceType.CALENDAR,
                ConnectorResourceType.EVENT,
                ConnectorResourceType.ATTENDEE,
                ConnectorResourceType.FREE_BUSY,
                ConnectorResourceType.WEBHOOK_SUBSCRIPTION,
            ],
            supported_events=[
                ConnectorEventType.EVENT_CREATED,
                ConnectorEventType.EVENT_MODIFIED,
                ConnectorEventType.EVENT_DELETED,
            ],
            required_scopes=CALENDAR_SCOPES,
            auth_type="oauth2",
            webhook_support=True,
            multi_account_support=True,
            operating_mode=ConnectorOperatingMode.PRODUCTION_OAUTH_MODE,
        )

    # ── Auth lifecycle ────────────────────────────────────────────────────────

    async def authenticate(
        self, user_email: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        """Initiate Google OAuth — same flow as Drive (shared token)."""
        flow = UnifiedOAuthFlow()
        return await flow.initiate(
            user_email=user_email,
            provider="google",
            tenant_id=tenant_id,
            account_id=account_id,
        )

    async def handle_callback(
        self, code: str, state: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        flow = UnifiedOAuthFlow()
        return await flow.handle_callback(provider="google", code=code, state=state)

    async def disconnect(
        self, user_id: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        revoked = ConnectorAuthVault.revoke_tokens("google", tenant_id=tenant_id, account_id=account_id)
        return {"status": "DISCONNECTED" if revoked else "NOT_FOUND", "provider": "google"}

    async def refresh(
        self, user_id: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        flow = UnifiedOAuthFlow()
        return await flow.refresh_token("google", user_id=user_id, tenant_id=tenant_id)

    # ── Introspection ─────────────────────────────────────────────────────────

    async def health(self) -> Dict[str, Any]:
        stored = ConnectorAuthVault.get_tokens("google")
        is_expired = ConnectorAuthVault.is_token_expired("google")
        if not stored:
            status, msg = ConnectorHealthStatus.AUTHENTICATION_REQUIRED, "Auth required."
        elif is_expired:
            status, msg = ConnectorHealthStatus.TOKEN_EXPIRED, "Token expired, will auto-refresh."
        else:
            status, msg = ConnectorHealthStatus.HEALTHY, "Google Calendar connector active."
        return ConnectorHealthReport(
            connector_id=self.connector_id, version="4.0.0",
            status=status, message=msg, vault_configured=bool(stored),
        ).model_dump()

    async def capabilities_report(self) -> Dict[str, Any]:
        return self.get_metadata()

    async def permissions(
        self, user_id: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        tokens = ConnectorAuthVault.get_tokens("google", tenant_id=tenant_id)
        return {"provider": "google", "scopes": tokens.get("scopes", []) if tokens else []}

    async def metadata(self) -> Dict[str, Any]:
        manifest = self._load_manifest()
        return {"connector_id": self.connector_id, "version": "4.0.0", "manifest": manifest}

    def _load_manifest(self) -> Dict[str, Any]:
        """Load the machine-readable manifest from the JSON file."""
        if _MANIFEST_PATH.exists():
            with open(_MANIFEST_PATH) as f:
                import json as _json
                return _json.load(f)
        return self.get_metadata()

    # ── CRUD ─────────────────────────────────────────────────────────────────

    async def search(
        self, query: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        res = CalendarEventsResource(svc)
        return await execute_with_resilience(
            self.connector_id,
            lambda: res.list_events(
                calendar_id=params.get("calendar_id", "primary"),
                query=query,
                time_min=params.get("time_min"),
                time_max=params.get("time_max"),
                max_results=params.get("page_size", 100),
            ),
        )

    async def list(
        self, resource_type: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        if resource_type in ("calendar", "calendars"):
            res = CalendarCalendarsResource(svc)
            return await execute_with_resilience(self.connector_id, res.list_calendars)
        elif resource_type in ("event", "events"):
            res2 = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.list_events(
                    calendar_id=params.get("calendar_id", "primary"),
                    time_min=params.get("time_min"),
                    time_max=params.get("time_max"),
                    max_results=params.get("page_size", 100),
                    sync_token=params.get("sync_token"),
                ),
            )
        elif resource_type in ("acl",):
            res3 = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res3.list_acl(params.get("calendar_id", "primary")),
            )
        raise ValueError(f"Unknown resource_type: '{resource_type}'")

    async def get(
        self,
        resource_type: str,
        resource_id: str,
        params: Dict[str, Any],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        if resource_type in ("calendar",):
            res = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id, lambda: res.get_calendar(resource_id)
            )
        elif resource_type in ("event",):
            res2 = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.get_event(params.get("calendar_id", "primary"), resource_id),
            )
        raise ValueError(f"Unknown resource_type: '{resource_type}'")

    async def create(
        self, resource_type: str, data: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        if resource_type in ("calendar",):
            res = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res.create_calendar(
                    summary=data["summary"],
                    description=data.get("description"),
                    time_zone=data.get("time_zone", "UTC"),
                ),
            )
        elif resource_type in ("event",):
            res2 = CalendarEventsResource(svc)
            if data.get("create_meet_link"):
                return await execute_with_resilience(
                    self.connector_id,
                    lambda: res2.create_event_with_meet(
                        calendar_id=data.get("calendar_id", "primary"),
                        summary=data["summary"],
                        start=data["start"],
                        end=data["end"],
                        attendees=data.get("attendees"),
                        description=data.get("description"),
                    ),
                )
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.create_event(
                    calendar_id=data.get("calendar_id", "primary"),
                    summary=data["summary"],
                    start=data["start"],
                    end=data["end"],
                    description=data.get("description"),
                    location=data.get("location"),
                    attendees=data.get("attendees"),
                    recurrence=data.get("recurrence"),
                    reminders=data.get("reminders"),
                    visibility=data.get("visibility", "default"),
                    status=data.get("status", "confirmed"),
                ),
            )
        raise ValueError(f"Unknown resource_type: '{resource_type}'")

    async def update(
        self,
        resource_type: str,
        resource_id: str,
        data: Dict[str, Any],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        if resource_type in ("event",):
            res = CalendarEventsResource(svc)
            calendar_id = data.pop("calendar_id", "primary")
            return await execute_with_resilience(
                self.connector_id,
                lambda: res.update_event(calendar_id, resource_id, data),
            )
        elif resource_type in ("calendar",):
            res2 = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.update_calendar(resource_id, **data),
            )
        raise ValueError(f"Unknown resource_type: '{resource_type}'")

    async def delete(
        self, resource_type: str, resource_id: str, context: ExecutionContext
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        if resource_type in ("event",):
            res = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res.delete_event("primary", resource_id),
            )
        elif resource_type in ("calendar",):
            res2 = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id, lambda: res2.delete_calendar(resource_id)
            )
        raise ValueError(f"Unknown resource_type: '{resource_type}'")

    async def move(
        self,
        resource_type: str,
        resource_id: str,
        destination: Dict[str, Any],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        if resource_type in ("event",):
            res = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res.move_event(
                    destination.get("calendar_id", "primary"),
                    resource_id,
                    destination["destination_calendar_id"],
                ),
            )
        raise ValueError(f"move() not supported for resource_type '{resource_type}'")

    async def copy(self, resource_type, resource_id, destination, context):
        raise NotImplementedError("Google Calendar does not support event copy natively. Use create_event.")

    async def share(
        self,
        resource_type: str,
        resource_id: str,
        share_config: Dict[str, Any],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        res = CalendarCalendarsResource(svc)
        return await execute_with_resilience(
            self.connector_id,
            lambda: res.create_acl(
                calendar_id=resource_id,
                role=share_config.get("role", "reader"),
                scope_type=share_config.get("scope_type", "user"),
                scope_value=share_config.get("email"),
            ),
        )

    async def export(self, resource_type, resource_id, export_format, context):
        """Export events as iCal (.ics) format via calendar URL."""
        return {
            "format": "ical",
            "url": f"https://calendar.google.com/calendar/ical/{resource_id}/public/basic.ics",
            "note": "Use the URL to download the iCal feed for this calendar.",
        }

    async def import_data(self, resource_type, data, params, context):
        svc = _build_calendar_service(context.tenant_id)
        res = CalendarEventsResource(svc)
        return await execute_with_resilience(
            self.connector_id,
            lambda: res.import_event(params.get("calendar_id", "primary"), params.get("event_data", {})),
        )

    async def watch(
        self, resource_type, resource_id, webhook_url, context
    ) -> Dict[str, Any]:
        import uuid
        svc = _build_calendar_service(context.tenant_id)
        watch_res = CalendarWatchResource(svc)
        channel_id = str(uuid.uuid4())
        if resource_id:
            return await execute_with_resilience(
                self.connector_id,
                lambda: watch_res.watch_events(
                    calendar_id=resource_id,
                    channel_id=channel_id,
                    webhook_url=webhook_url,
                ),
            )
        return await execute_with_resilience(
            self.connector_id,
            lambda: watch_res.watch_calendar_list(channel_id=channel_id, webhook_url=webhook_url),
        )

    async def sync(
        self, resource_type, sync_token, context
    ) -> Dict[str, Any]:
        svc = _build_calendar_service(context.tenant_id)
        res = CalendarEventsResource(svc)
        result = await execute_with_resilience(
            self.connector_id,
            lambda: res.list_events(
                calendar_id="primary",
                sync_token=sync_token,
                show_deleted=True,
                max_results=2500,
            ),
        )
        return {
            "connector": self.connector_id,
            "sync_token_used": sync_token,
            "new_sync_token": result.get("nextSyncToken"),
            "next_page_token": result.get("nextPageToken"),
            "events": result.get("items", []),
            "event_count": len(result.get("items", [])),
        }

    async def batch(
        self, operations: List[Dict[str, Any]], context: ExecutionContext
    ) -> Dict[str, Any]:
        results = []
        for op in operations:
            try:
                req = ConnectorExecuteRequest(
                    capability=op["capability"], params=op.get("params", {})
                )
                result = await self.execute(req, context)
                results.append({"capability": op["capability"], "status": "OK", "result": result})
            except Exception as e:
                results.append({"capability": op["capability"], "status": "ERROR", "error": str(e)})
        return {"connector": self.connector_id, "results": results}

    async def execute(
        self, request: ConnectorExecuteRequest, context: ExecutionContext
    ) -> Dict[str, Any]:
        """Universal capability dispatcher."""
        cap = request.capability
        p = request.params
        svc = _build_calendar_service(context.tenant_id, request.account_id)

        if cap == "list_calendars":
            res = CalendarCalendarsResource(svc)
            return await execute_with_resilience(self.connector_id, res.list_calendars)
        elif cap == "get_calendar":
            res = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id, lambda: res.get_calendar(p["calendar_id"])
            )
        elif cap == "create_calendar":
            res = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res.create_calendar(p["summary"], p.get("description"), p.get("time_zone", "UTC")),
            )
        elif cap == "delete_calendar":
            res = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id, lambda: res.delete_calendar(p["calendar_id"])
            )
        elif cap == "list_events":
            res2 = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.list_events(
                    calendar_id=p.get("calendar_id", "primary"),
                    time_min=p.get("time_min"),
                    time_max=p.get("time_max"),
                    query=p.get("query"),
                    max_results=request.page_size,
                    page_token=request.page_token,
                    sync_token=p.get("sync_token"),
                ),
            )
        elif cap == "get_event":
            res2 = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.get_event(p.get("calendar_id", "primary"), p["event_id"]),
            )
        elif cap == "create_event":
            return await self.create("event", p, context)
        elif cap == "create_event_with_meet":
            p["create_meet_link"] = True
            return await self.create("event", p, context)
        elif cap == "update_event":
            event_id = p.pop("event_id")
            return await self.update("event", event_id, p, context)
        elif cap == "delete_event":
            return await self.delete("event", p["event_id"], context)
        elif cap == "move_event":
            return await self.move("event", p["event_id"], p, context)
        elif cap == "quick_add_event":
            res2 = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.quick_add_event(p.get("calendar_id", "primary"), p["text"]),
            )
        elif cap == "list_instances":
            res2 = CalendarEventsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res2.list_instances(
                    p.get("calendar_id", "primary"), p["event_id"],
                    time_min=p.get("time_min"), time_max=p.get("time_max"),
                ),
            )
        elif cap == "get_freebusy":
            fb = CalendarFreeBusyResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: fb.query(
                    time_min=p["time_min"],
                    time_max=p["time_max"],
                    calendar_ids=p.get("calendar_ids", ["primary"]),
                    time_zone=p.get("time_zone", "UTC"),
                ),
            )
        elif cap == "watch_events":
            return await self.watch(
                "event", p.get("calendar_id", "primary"), p["webhook_url"], context
            )
        elif cap == "list_settings":
            settings = CalendarSettingsResource(svc)
            return await execute_with_resilience(self.connector_id, settings.list_settings)
        elif cap == "sync_events":
            return await self.sync("event", p.get("sync_token"), context)
        elif cap == "list_acl":
            res3 = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res3.list_acl(p.get("calendar_id", "primary")),
            )
        elif cap == "create_acl":
            res3 = CalendarCalendarsResource(svc)
            return await execute_with_resilience(
                self.connector_id,
                lambda: res3.create_acl(
                    p.get("calendar_id", "primary"),
                    role=p["role"],
                    scope_type=p["scope_type"],
                    scope_value=p.get("scope_value"),
                ),
            )
        elif cap == "batch":
            return await self.batch(p.get("operations", []), context)
        else:
            raise ValueError(
                f"Unknown capability '{cap}' for connector '{self.connector_id}'"
            )
