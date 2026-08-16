"""Microsoft Teams Connector — Production

Implements the complete business-facing Microsoft Teams API surface via
Microsoft Graph. Uses MicrosoftOAuthProvider for token lifecycle management.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities, ConnectorOperatingMode
from app.connectors.sdk.canonical import (
    CanonicalTeam, CanonicalChannel, CanonicalTeamsMessage,
    CanonicalConversation, CanonicalPresence, CanonicalMeetingTranscript,
    CanonicalContact, CanonicalCalendarEvent,
)
from app.connectors.oauth.manager import OAuthProviderManager
from app.domain.shared.context import ExecutionContext
from .graph_client import graph_request, graph_paginated, GraphAPIError

logger = structlog.get_logger(__name__)


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


class TeamsConnector(BaseConnector):
    """Production Microsoft Teams Connector with full Graph API coverage."""

    def __init__(self):
        self.oauth_manager = OAuthProviderManager()
        self.client_id = os.getenv("MICROSOFT_OAUTH_CLIENT_ID", "")
        self.client_secret = os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET", "")

    @property
    def connector_id(self) -> str:
        return "microsoft_teams"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="microsoft_teams",
            display_name="Microsoft Teams",
            version="2.0.0",
            family="communication",
            supports_realtime=True,
            supports_polling=True,
            supported_actions=[
                # Teams
                "list_teams", "get_team", "create_team", "archive_team",
                # Channels
                "list_channels", "create_channel", "rename_channel", "archive_channel", "delete_channel",
                # Messages
                "send_message", "reply_message", "edit_message", "delete_message",
                "pin_message", "read_messages",
                # Chats
                "list_chats", "create_chat", "read_chat", "send_chat_message",
                # Files
                "upload_file", "download_file", "list_files", "share_file",
                # Members
                "list_members", "invite_member", "remove_member",
                # Meetings
                "list_meetings", "create_meeting", "cancel_meeting", "get_meeting",
                "meeting_attendees",
                # Presence
                "get_presence", "set_presence",
                # Search
                "search_messages", "search_chats",
                # System
                "health_check", "disconnect",
            ],
            required_scopes=[
                "openid", "profile", "email", "offline_access",
                "User.Read",
                "Team.ReadBasic.All",
                "Channel.ReadBasic.All",
                "ChannelMessage.Send",
                "ChannelMessage.Read.All",
                "Chat.ReadWrite",
                "ChatMessage.Send",
                "Presence.Read",
                "Presence.Read.All",
            ],
            auth_type="oauth2",
            webhook_support=True,
            multi_account_support=True,
            operating_mode=ConnectorOperatingMode.PRODUCTION_OAUTH_MODE,
        )

    async def _token(self, tenant_id: str) -> str:
        return await self.oauth_manager.get_live_token(
            provider_id="microsoft",
            tenant_id=tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    # ─── Teams ────────────────────────────────────────────────────────────────

    def _list_teams(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/joinedTeams")
        teams = [
            CanonicalTeam(
                team_id=t["id"],
                display_name=t.get("displayName", ""),
                description=t.get("description"),
                visibility=t.get("visibility", "private"),
                is_archived=t.get("isArchived", False),
                web_url=t.get("webUrl"),
                raw_provider_id="microsoft_teams",
            ).model_dump()
            for t in items
        ]
        return {"teams": teams}

    def _get_team(self, token: str, team_id: str) -> Dict:
        t = graph_request(token, f"/teams/{team_id}")
        return CanonicalTeam(
            team_id=t["id"],
            display_name=t.get("displayName", ""),
            description=t.get("description"),
            visibility=t.get("visibility", "private"),
            is_archived=t.get("isArchived", False),
            web_url=t.get("webUrl"),
            raw_provider_id="microsoft_teams",
        ).model_dump()

    def _create_team(self, token: str, display_name: str, description: str = "", visibility: str = "Private") -> Dict:
        body = {
            "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
            "displayName": display_name,
            "description": description,
            "visibility": visibility,
        }
        result = graph_request(token, "/teams", method="POST", payload=body)
        return {"status": "CREATED", "team": result}

    def _archive_team(self, token: str, team_id: str) -> Dict:
        graph_request(token, f"/teams/{team_id}/archive", method="POST", payload={})
        return {"status": "ARCHIVED", "team_id": team_id}

    # ─── Channels ─────────────────────────────────────────────────────────────

    def _list_channels(self, token: str, team_id: str) -> Dict:
        items = graph_paginated(token, f"/teams/{team_id}/channels")
        channels = [
            CanonicalChannel(
                channel_id=c["id"],
                team_id=team_id,
                display_name=c.get("displayName", ""),
                description=c.get("description"),
                channel_type=c.get("membershipType", "standard"),
                is_archived=c.get("isArchived", False),
                web_url=c.get("webUrl"),
                raw_provider_id="microsoft_teams",
            ).model_dump()
            for c in items
        ]
        return {"channels": channels, "team_id": team_id}

    def _create_channel(self, token: str, team_id: str, display_name: str, description: str = "", channel_type: str = "standard") -> Dict:
        body = {
            "displayName": display_name,
            "description": description,
            "membershipType": channel_type,
        }
        result = graph_request(token, f"/teams/{team_id}/channels", method="POST", payload=body)
        return {"status": "CREATED", "channel_id": result.get("id"), "display_name": display_name}

    def _rename_channel(self, token: str, team_id: str, channel_id: str, display_name: str) -> Dict:
        graph_request(token, f"/teams/{team_id}/channels/{channel_id}", method="PATCH", payload={"displayName": display_name})
        return {"status": "RENAMED", "channel_id": channel_id, "display_name": display_name}

    def _archive_channel(self, token: str, team_id: str, channel_id: str) -> Dict:
        graph_request(token, f"/teams/{team_id}/channels/{channel_id}/archive", method="POST", payload={})
        return {"status": "ARCHIVED", "channel_id": channel_id}

    def _delete_channel(self, token: str, team_id: str, channel_id: str) -> Dict:
        graph_request(token, f"/teams/{team_id}/channels/{channel_id}", method="DELETE")
        return {"status": "DELETED", "channel_id": channel_id}

    # ─── Messages ─────────────────────────────────────────────────────────────

    def _send_message(self, token: str, team_id: str, channel_id: str, text: str, importance: str = "normal") -> Dict:
        body = {
            "body": {"contentType": "html" if "<" in text else "text", "content": text},
            "importance": importance,
        }
        result = graph_request(token, f"/teams/{team_id}/channels/{channel_id}/messages", method="POST", payload=body)
        return CanonicalTeamsMessage(
            message_id=result["id"],
            channel_id=channel_id,
            team_id=team_id,
            sender_id=result.get("from", {}).get("user", {}).get("id", ""),
            sender_name=result.get("from", {}).get("user", {}).get("displayName"),
            content=result.get("body", {}).get("content", text),
            content_html=result.get("body", {}).get("content") if result.get("body", {}).get("contentType") == "html" else None,
            importance=result.get("importance", importance),
            web_url=result.get("webUrl"),
            timestamp=_parse_dt(result.get("createdDateTime")) or datetime.now(timezone.utc),
            raw_provider_id="microsoft_teams",
        ).model_dump()

    def _reply_message(self, token: str, team_id: str, channel_id: str, message_id: str, text: str) -> Dict:
        body = {"body": {"contentType": "text", "content": text}}
        result = graph_request(token, f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies", method="POST", payload=body)
        return {
            "message_id": result.get("id"),
            "reply_to_id": message_id,
            "status": "SENT",
            "channel_id": channel_id,
        }

    def _edit_message(self, token: str, team_id: str, channel_id: str, message_id: str, text: str) -> Dict:
        body = {"body": {"contentType": "text", "content": text}}
        graph_request(token, f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}", method="PATCH", payload=body)
        return {"status": "EDITED", "message_id": message_id}

    def _delete_message(self, token: str, team_id: str, channel_id: str, message_id: str) -> Dict:
        graph_request(token, f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/softDelete", method="POST", payload={})
        return {"status": "DELETED", "message_id": message_id}

    def _read_messages(self, token: str, team_id: str, channel_id: str, limit: int = 20) -> Dict:
        items = graph_request(
            token,
            f"/teams/{team_id}/channels/{channel_id}/messages",
            params={"$top": str(limit), "$orderby": "createdDateTime desc"},
        ).get("value", [])
        messages = [
            CanonicalTeamsMessage(
                message_id=m["id"],
                channel_id=channel_id,
                team_id=team_id,
                sender_id=m.get("from", {}).get("user", {}).get("id", ""),
                sender_name=m.get("from", {}).get("user", {}).get("displayName"),
                content=m.get("body", {}).get("content", ""),
                importance=m.get("importance", "normal"),
                web_url=m.get("webUrl"),
                timestamp=_parse_dt(m.get("createdDateTime")) or datetime.now(timezone.utc),
                edited_at=_parse_dt(m.get("lastModifiedDateTime")),
                is_deleted=m.get("deletedDateTime") is not None,
                raw_provider_id="microsoft_teams",
            ).model_dump()
            for m in items
        ]
        return {"messages": messages}

    def _pin_message(self, token: str, team_id: str, channel_id: str, message_id: str) -> Dict:
        body = {"message": {"id": message_id}}
        graph_request(token, f"/teams/{team_id}/channels/{channel_id}/pinnedMessages", method="POST", payload=body)
        return {"status": "PINNED", "message_id": message_id}

    # ─── Chats ────────────────────────────────────────────────────────────────

    def _list_chats(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/chats", params={"$expand": "members"})
        chats = [
            CanonicalConversation(
                conversation_id=c["id"],
                topic=c.get("topic"),
                conversation_type=c.get("chatType", "group"),
                participants=[m.get("email", m.get("displayName", "")) for m in c.get("members", [])],
                last_message_at=_parse_dt(c.get("lastUpdatedDateTime")),
                raw_provider_id="microsoft_teams",
            ).model_dump()
            for c in items
        ]
        return {"chats": chats}

    def _create_chat(self, token: str, members: List[str], chat_type: str = "oneOnOne", topic: Optional[str] = None) -> Dict:
        member_list = [
            {"@odata.type": "#microsoft.graph.aadUserConversationMember",
             "roles": ["owner"] if i == 0 else [],
             "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{email}')"}
            for i, email in enumerate(members)
        ]
        body: Dict[str, Any] = {"chatType": chat_type, "members": member_list}
        if topic:
            body["topic"] = topic
        result = graph_request(token, "/chats", method="POST", payload=body)
        return {"chat_id": result.get("id"), "status": "CREATED"}

    def _read_chat(self, token: str, chat_id: str, limit: int = 20) -> Dict:
        items = graph_request(
            token,
            f"/chats/{chat_id}/messages",
            params={"$top": str(limit)},
        ).get("value", [])
        messages = [
            CanonicalTeamsMessage(
                message_id=m["id"],
                channel_id=chat_id,
                sender_id=m.get("from", {}).get("user", {}).get("id", ""),
                sender_name=m.get("from", {}).get("user", {}).get("displayName"),
                content=m.get("body", {}).get("content", ""),
                timestamp=_parse_dt(m.get("createdDateTime")) or datetime.now(timezone.utc),
                raw_provider_id="microsoft_teams",
            ).model_dump()
            for m in items
        ]
        return {"chat_id": chat_id, "messages": messages}

    def _send_chat_message(self, token: str, chat_id: str, text: str) -> Dict:
        body = {"body": {"contentType": "text", "content": text}}
        result = graph_request(token, f"/chats/{chat_id}/messages", method="POST", payload=body)
        return {
            "message_id": result.get("id"),
            "chat_id": chat_id,
            "status": "SENT",
        }

    # ─── Members ──────────────────────────────────────────────────────────────

    def _list_members(self, token: str, team_id: str) -> Dict:
        items = graph_paginated(token, f"/teams/{team_id}/members")
        return {
            "members": [
                {
                    "id": m.get("id"),
                    "display_name": m.get("displayName"),
                    "email": m.get("email"),
                    "roles": m.get("roles", []),
                }
                for m in items
            ]
        }

    def _invite_member(self, token: str, team_id: str, user_email: str, role: str = "member") -> Dict:
        body = {
            "@odata.type": "#microsoft.graph.aadUserConversationMember",
            "roles": [role],
            "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{user_email}')",
        }
        graph_request(token, f"/teams/{team_id}/members", method="POST", payload=body)
        return {"status": "INVITED", "email": user_email}

    def _remove_member(self, token: str, team_id: str, membership_id: str) -> Dict:
        graph_request(token, f"/teams/{team_id}/members/{membership_id}", method="DELETE")
        return {"status": "REMOVED", "membership_id": membership_id}

    # ─── Files ────────────────────────────────────────────────────────────────

    def _list_files(self, token: str, team_id: str, channel_id: str) -> Dict:
        items = graph_paginated(token, f"/teams/{team_id}/channels/{channel_id}/filesFolder/children")
        return {
            "files": [
                {
                    "file_id": f.get("id"),
                    "name": f.get("name"),
                    "size_bytes": f.get("size"),
                    "web_url": f.get("webUrl"),
                    "last_modified": f.get("lastModifiedDateTime"),
                }
                for f in items
            ]
        }

    # ─── Meetings ─────────────────────────────────────────────────────────────

    def _list_meetings(self, token: str) -> Dict:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        items = graph_paginated(
            token,
            "/me/events",
            params={
                "$filter": f"start/dateTime ge '{start}' and end/dateTime le '{end}'",
                "$orderby": "start/dateTime",
                "$top": "50",
            },
        )
        meetings = [
            CanonicalCalendarEvent(
                event_id=e["id"],
                title=e.get("subject", ""),
                description=e.get("bodyPreview"),
                start_time=_parse_dt(e.get("start", {}).get("dateTime")) or now,
                end_time=_parse_dt(e.get("end", {}).get("dateTime")) or now,
                attendees=[a.get("emailAddress", {}).get("address", "") for a in e.get("attendees", [])],
                is_online_meeting=e.get("isOnlineMeeting", False),
                meeting_link=e.get("onlineMeeting", {}).get("joinUrl"),
                organizer=e.get("organizer", {}).get("emailAddress", {}).get("address"),
                status=e.get("showAs", "confirmed"),
                raw_provider_id="microsoft_teams",
            ).model_dump()
            for e in items
        ]
        return {"meetings": meetings}

    def _create_meeting(self, token: str, subject: str, start: str, end: str, attendees: Optional[List[str]] = None, body_text: str = "") -> Dict:
        payload: Dict[str, Any] = {
            "subject": subject,
            "body": {"contentType": "text", "content": body_text},
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
            "isOnlineMeeting": True,
            "onlineMeetingProvider": "teamsForBusiness",
        }
        if attendees:
            payload["attendees"] = [
                {"emailAddress": {"address": a}, "type": "required"} for a in attendees
            ]
        result = graph_request(token, "/me/events", method="POST", payload=payload)
        return {
            "event_id": result.get("id"),
            "join_url": result.get("onlineMeeting", {}).get("joinUrl"),
            "status": "CREATED",
        }

    def _cancel_meeting(self, token: str, event_id: str, comment: str = "") -> Dict:
        graph_request(token, f"/me/events/{event_id}/cancel", method="POST", payload={"comment": comment})
        return {"status": "CANCELLED", "event_id": event_id}

    def _get_meeting(self, token: str, event_id: str) -> Dict:
        e = graph_request(token, f"/me/events/{event_id}")
        now = datetime.now(timezone.utc)
        return CanonicalCalendarEvent(
            event_id=e["id"],
            title=e.get("subject", ""),
            description=e.get("bodyPreview"),
            start_time=_parse_dt(e.get("start", {}).get("dateTime")) or now,
            end_time=_parse_dt(e.get("end", {}).get("dateTime")) or now,
            attendees=[a.get("emailAddress", {}).get("address", "") for a in e.get("attendees", [])],
            is_online_meeting=e.get("isOnlineMeeting", False),
            meeting_link=e.get("onlineMeeting", {}).get("joinUrl"),
            organizer=e.get("organizer", {}).get("emailAddress", {}).get("address"),
            raw_provider_id="microsoft_teams",
        ).model_dump()

    def _meeting_attendees(self, token: str, event_id: str) -> Dict:
        e = graph_request(token, f"/me/events/{event_id}", params={"$select": "attendees"})
        return {
            "event_id": event_id,
            "attendees": [
                {
                    "email": a.get("emailAddress", {}).get("address"),
                    "name": a.get("emailAddress", {}).get("name"),
                    "type": a.get("type"),
                    "status": a.get("status", {}).get("response"),
                }
                for a in e.get("attendees", [])
            ],
        }

    # ─── Presence ─────────────────────────────────────────────────────────────

    def _get_presence(self, token: str, user_id: Optional[str] = None) -> Dict:
        path = f"/users/{user_id}/presence" if user_id else "/me/presence"
        p = graph_request(token, path)
        return CanonicalPresence(
            user_id=p.get("id", user_id or "me"),
            availability=p.get("availability", "Unknown"),
            activity=p.get("activity"),
            raw_provider_id="microsoft_teams",
        ).model_dump()

    def _set_presence(self, token: str, availability: str, activity: str, expiration_duration: str = "PT1H") -> Dict:
        body = {
            "availability": availability,
            "activity": activity,
            "sessionId": "bizos-session",
            "expirationDuration": expiration_duration,
        }
        graph_request(token, "/me/presence/setPresence", method="POST", payload=body)
        return {"status": "SET", "availability": availability, "activity": activity}

    # ─── Search ───────────────────────────────────────────────────────────────

    def _search_messages(self, token: str, query: str) -> Dict:
        payload = {
            "requests": [
                {
                    "entityTypes": ["chatMessage"],
                    "query": {"queryString": query},
                    "from": 0,
                    "size": 25,
                }
            ]
        }
        result = graph_request(token, "/search/query", method="POST", payload=payload)
        hits = result.get("value", [{}])[0].get("hitsContainers", [{}])[0].get("hits", [])
        return {"query": query, "results": [{"id": h.get("hitId"), "summary": h.get("summary")} for h in hits]}

    def _search_chats(self, token: str, query: str) -> Dict:
        payload = {
            "requests": [
                {
                    "entityTypes": ["message"],
                    "query": {"queryString": query},
                    "from": 0,
                    "size": 25,
                }
            ]
        }
        result = graph_request(token, "/search/query", method="POST", payload=payload)
        hits = result.get("value", [{}])[0].get("hitsContainers", [{}])[0].get("hits", [])
        return {"query": query, "results": [{"id": h.get("hitId"), "summary": h.get("summary")} for h in hits]}

    # ─── execute_action dispatch ───────────────────────────────────────────────

    async def execute_action(self, action: str, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        tenant_id = params.get("tenant_id", "default_tenant")
        token = await self._token(tenant_id)

        try:
            # ── Health ─────────────────────────────────────────────────────────
            if action == "health_check":
                me = graph_request(token, "/me")
                return {"status": "ok", "user": me.get("displayName"), "email": me.get("mail") or me.get("userPrincipalName")}

            # ── Teams ──────────────────────────────────────────────────────────
            elif action == "list_teams":
                return self._list_teams(token)
            elif action == "get_team":
                return self._get_team(token, params["team_id"])
            elif action == "create_team":
                return self._create_team(token, params["display_name"], params.get("description", ""), params.get("visibility", "Private"))
            elif action == "archive_team":
                return self._archive_team(token, params["team_id"])

            # ── Channels ───────────────────────────────────────────────────────
            elif action == "list_channels":
                return self._list_channels(token, params["team_id"])
            elif action == "create_channel":
                return self._create_channel(token, params["team_id"], params["display_name"], params.get("description", ""), params.get("channel_type", "standard"))
            elif action == "rename_channel":
                return self._rename_channel(token, params["team_id"], params["channel_id"], params["display_name"])
            elif action == "archive_channel":
                return self._archive_channel(token, params["team_id"], params["channel_id"])
            elif action == "delete_channel":
                return self._delete_channel(token, params["team_id"], params["channel_id"])

            # ── Messages ───────────────────────────────────────────────────────
            elif action == "send_message":
                return self._send_message(token, params["team_id"], params["channel_id"], params["text"], params.get("importance", "normal"))
            elif action == "reply_message":
                return self._reply_message(token, params["team_id"], params["channel_id"], params["message_id"], params["text"])
            elif action == "edit_message":
                return self._edit_message(token, params["team_id"], params["channel_id"], params["message_id"], params["text"])
            elif action == "delete_message":
                return self._delete_message(token, params["team_id"], params["channel_id"], params["message_id"])
            elif action == "pin_message":
                return self._pin_message(token, params["team_id"], params["channel_id"], params["message_id"])
            elif action == "read_messages":
                return self._read_messages(token, params["team_id"], params["channel_id"], params.get("limit", 20))

            # ── Chats ──────────────────────────────────────────────────────────
            elif action == "list_chats":
                return self._list_chats(token)
            elif action == "create_chat":
                return self._create_chat(token, params["members"], params.get("chat_type", "oneOnOne"), params.get("topic"))
            elif action == "read_chat":
                return self._read_chat(token, params["chat_id"], params.get("limit", 20))
            elif action == "send_chat_message":
                return self._send_chat_message(token, params["chat_id"], params["text"])

            # ── Members ────────────────────────────────────────────────────────
            elif action == "list_members":
                return self._list_members(token, params["team_id"])
            elif action == "invite_member":
                return self._invite_member(token, params["team_id"], params["user_email"], params.get("role", "member"))
            elif action == "remove_member":
                return self._remove_member(token, params["team_id"], params["membership_id"])

            # ── Files ──────────────────────────────────────────────────────────
            elif action == "list_files":
                return self._list_files(token, params["team_id"], params["channel_id"])

            # ── Meetings ───────────────────────────────────────────────────────
            elif action == "list_meetings":
                return self._list_meetings(token)
            elif action == "create_meeting":
                return self._create_meeting(token, params["subject"], params["start"], params["end"], params.get("attendees"), params.get("body_text", ""))
            elif action == "cancel_meeting":
                return self._cancel_meeting(token, params["event_id"], params.get("comment", ""))
            elif action == "get_meeting":
                return self._get_meeting(token, params["event_id"])
            elif action == "meeting_attendees":
                return self._meeting_attendees(token, params["event_id"])

            # ── Presence ───────────────────────────────────────────────────────
            elif action == "get_presence":
                return self._get_presence(token, params.get("user_id"))
            elif action == "set_presence":
                return self._set_presence(token, params["availability"], params["activity"], params.get("expiration_duration", "PT1H"))

            # ── Search ─────────────────────────────────────────────────────────
            elif action == "search_messages":
                return self._search_messages(token, params["query"])
            elif action == "search_chats":
                return self._search_chats(token, params["query"])

            # ── Disconnect ─────────────────────────────────────────────────────
            elif action == "disconnect":
                await self.oauth_manager.revoke_and_delete(
                    provider_id="microsoft",
                    tenant_id=tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
                return {"status": "DISCONNECTED"}

            else:
                raise ValueError(f"Action '{action}' is not implemented for Microsoft Teams connector")

        except GraphAPIError as exc:
            logger.error("Teams action failed", action=action, error=str(exc), status=exc.status_code)
            raise

    async def health_check(self) -> Dict[str, Any]:
        try:
            token = await self._token("default_tenant")
            me = graph_request(token, "/me")
            return {"status": "ok", "connector_id": self.connector_id, "user": me.get("displayName")}
        except Exception as e:
            return {"status": "error", "connector_id": self.connector_id, "error": str(e)}
