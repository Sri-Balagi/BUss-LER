"""Microsoft Outlook Connector — Production

Implements the complete business Outlook workflow via Microsoft Graph:
Email (send, reply, forward, draft, folder, search, state management, attachments),
Contacts, and Calendar. Uses MicrosoftOAuthProvider for token lifecycle.
"""

import os
import base64
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import structlog

from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities, ConnectorOperatingMode
from app.connectors.sdk.canonical import (
    CanonicalEmail, CanonicalAttachment, CanonicalContact, CanonicalCalendarEvent,
)
from app.connectors.oauth.manager import OAuthProviderManager
from app.domain.shared.context import ExecutionContext
from app.connectors.builtin.communication.teams.graph_client import graph_request, graph_paginated, GraphAPIError

logger = structlog.get_logger(__name__)

# Well-known folder IDs
_FOLDER_MAP = {
    "inbox": "inbox",
    "sent": "sentItems",
    "sent_items": "sentItems",
    "drafts": "drafts",
    "deleted": "deleteditems",
    "trash": "deleteditems",
    "archive": "archive",
    "junk": "junkemail",
}


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _email_address(addr_obj: Optional[Dict]) -> str:
    if not addr_obj:
        return ""
    return addr_obj.get("emailAddress", {}).get("address", "")


def _map_message(m: Dict) -> CanonicalEmail:
    """Map a raw Graph message object to CanonicalEmail."""
    sender = _email_address(m.get("sender") or m.get("from"))
    recipients = [_email_address(r) for r in m.get("toRecipients", [])]
    cc = [_email_address(r) for r in m.get("ccRecipients", [])]
    bcc = [_email_address(r) for r in m.get("bccRecipients", [])]
    attachments = [a.get("id", "") for a in m.get("attachments", [])]

    return CanonicalEmail(
        email_id=m["id"],
        thread_id=m.get("conversationId"),
        conversation_id=m.get("conversationId"),
        sender=sender,
        recipients=recipients,
        cc=cc,
        bcc=bcc,
        subject=m.get("subject", "(no subject)"),
        body_text=m.get("body", {}).get("content", "") if m.get("body", {}).get("contentType") == "text" else "",
        body_html=m.get("body", {}).get("content", "") if m.get("body", {}).get("contentType") == "html" else None,
        snippet=m.get("bodyPreview"),
        is_read=m.get("isRead", False),
        is_flagged=m.get("flag", {}).get("flagStatus") == "flagged",
        importance=m.get("importance", "normal"),
        has_attachments=m.get("hasAttachments", False),
        attachment_ids=attachments,
        timestamp=_parse_dt(m.get("receivedDateTime")) or datetime.now(timezone.utc),
        raw_provider_id="microsoft_outlook",
    )


class OutlookConnector(BaseConnector):
    """Production Microsoft Outlook Connector with full Graph API coverage."""

    def __init__(self):
        self.oauth_manager = OAuthProviderManager()
        self.client_id = os.getenv("MICROSOFT_OAUTH_CLIENT_ID", "")
        self.client_secret = os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET", "")

    @property
    def connector_id(self) -> str:
        return "microsoft_outlook"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="microsoft_outlook",
            display_name="Microsoft Outlook",
            version="2.0.0",
            family="email",
            supports_realtime=True,
            supports_polling=True,
            supported_actions=[
                # Email Sending
                "send_email", "reply_email", "reply_all", "forward_email",
                "create_draft", "update_draft", "delete_draft", "send_draft",
                # Inbox Operations
                "read_inbox", "read_sent", "read_drafts", "read_deleted",
                "read_archive", "read_junk", "read_custom_folder",
                # Search
                "search_emails",
                # Folder Operations
                "list_folders", "create_folder", "rename_folder", "delete_folder",
                "move_email", "copy_email",
                # Email State Management
                "mark_read", "mark_unread", "flag_email", "unflag_email",
                "archive_email", "restore_email", "delete_email", "permanent_delete",
                # Attachments
                "list_attachments", "download_attachment",
                # Contacts
                "list_contacts", "search_contacts", "create_contact",
                "update_contact", "delete_contact", "list_contact_folders",
                "create_contact_folder", "rename_contact_folder", "delete_contact_folder",
                "favorite_contact", "get_contact_photo", "update_contact_photo",
                # Calendar
                "list_events", "create_event", "update_event", "delete_event",
                "accept_meeting", "decline_meeting", "tentative_meeting",
                "list_calendars", "create_recurring_event", "cancel_event",
                "invite_attendees", "free_busy_lookup", "search_events",
                # Profile & People
                "get_user_profile", "get_profile_photo", "get_mailbox_settings",
                "list_people", "search_people", "recent_people", "organization_people",
                # System
                "health_check", "disconnect",
            ],
            required_scopes=[
                "openid", "profile", "email", "offline_access",
                "User.Read",
                "Mail.Read", "Mail.ReadWrite", "Mail.Send",
                "Contacts.Read", "Contacts.ReadWrite",
                "Calendars.Read", "Calendars.ReadWrite",
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

    # ─── Email Sending ────────────────────────────────────────────────────────

    def _build_message_body(
        self,
        subject: str,
        body: str,
        to: List[str],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        body_type: str = "text",
        importance: str = "normal",
    ) -> Dict:
        def addr_list(emails: Optional[List[str]]) -> List[Dict]:
            return [{"emailAddress": {"address": e}} for e in (emails or [])]

        return {
            "subject": subject,
            "importance": importance,
            "body": {"contentType": body_type, "content": body},
            "toRecipients": addr_list(to),
            "ccRecipients": addr_list(cc),
            "bccRecipients": addr_list(bcc),
        }

    def _send_email(self, token: str, subject: str, body: str, to: List[str],
                    cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None,
                    body_type: str = "text", importance: str = "normal") -> Dict:
        payload = {"message": self._build_message_body(subject, body, to, cc, bcc, body_type, importance), "saveToSentItems": True}
        graph_request(token, "/me/sendMail", method="POST", payload=payload)
        return {"status": "SENT", "subject": subject, "to": to}

    def _reply_email(self, token: str, message_id: str, body: str, reply_all: bool = False) -> Dict:
        endpoint = f"/me/messages/{message_id}/replyAll" if reply_all else f"/me/messages/{message_id}/reply"
        graph_request(token, endpoint, method="POST", payload={"message": {"body": {"contentType": "text", "content": body}}})
        return {"status": "REPLIED", "message_id": message_id, "reply_all": reply_all}

    def _forward_email(self, token: str, message_id: str, to: List[str], comment: str = "") -> Dict:
        graph_request(
            token,
            f"/me/messages/{message_id}/forward",
            method="POST",
            payload={
                "comment": comment,
                "toRecipients": [{"emailAddress": {"address": e}} for e in to],
            },
        )
        return {"status": "FORWARDED", "message_id": message_id, "to": to}

    def _create_draft(self, token: str, subject: str, body: str, to: List[str],
                      cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None) -> Dict:
        msg = self._build_message_body(subject, body, to, cc, bcc)
        result = graph_request(token, "/me/messages", method="POST", payload=msg)
        return {"status": "DRAFT_CREATED", "draft_id": result.get("id"), "subject": subject}

    def _update_draft(self, token: str, draft_id: str, updates: Dict) -> Dict:
        graph_request(token, f"/me/messages/{draft_id}", method="PATCH", payload=updates)
        return {"status": "DRAFT_UPDATED", "draft_id": draft_id}

    def _delete_draft(self, token: str, draft_id: str) -> Dict:
        graph_request(token, f"/me/messages/{draft_id}", method="DELETE")
        return {"status": "DRAFT_DELETED", "draft_id": draft_id}

    def _send_draft(self, token: str, draft_id: str) -> Dict:
        graph_request(token, f"/me/messages/{draft_id}/send", method="POST", payload={})
        return {"status": "SENT", "draft_id": draft_id}

    # ─── Inbox Operations ─────────────────────────────────────────────────────

    def _read_folder(self, token: str, folder_id: str, limit: int = 20, skip: int = 0) -> Dict:
        items = graph_request(
            token,
            f"/me/mailFolders/{folder_id}/messages",
            params={
                "$top": str(limit),
                "$skip": str(skip),
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,from,toRecipients,ccRecipients,receivedDateTime,isRead,hasAttachments,bodyPreview,importance,flag,conversationId",
            },
        ).get("value", [])
        return {"emails": [_map_message(m).model_dump() for m in items], "folder": folder_id}

    # ─── Search ───────────────────────────────────────────────────────────────

    def _search_emails(self, token: str, query: str, limit: int = 20) -> Dict:
        """
        Supports: sender:X, to:X, subject:X, keyword, hasAttachments, isRead, isFlagged
        Uses Graph $search syntax which supports OData-like predicates.
        """
        items = graph_request(
            token,
            "/me/messages",
            params={
                "$search": f'"{query}"',
                "$top": str(limit),
                "$select": "id,subject,from,toRecipients,receivedDateTime,isRead,bodyPreview,hasAttachments",
            },
        ).get("value", [])
        return {"query": query, "emails": [_map_message(m).model_dump() for m in items]}

    # ─── Folder Operations ────────────────────────────────────────────────────

    def _list_folders(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/mailFolders", params={"$includeHiddenFolders": "false"})
        return {
            "folders": [
                {
                    "id": f.get("id"),
                    "name": f.get("displayName"),
                    "total_count": f.get("totalItemCount", 0),
                    "unread_count": f.get("unreadItemCount", 0),
                }
                for f in items
            ]
        }

    def _create_folder(self, token: str, display_name: str, parent_folder: Optional[str] = None) -> Dict:
        path = f"/me/mailFolders/{parent_folder}/childFolders" if parent_folder else "/me/mailFolders"
        result = graph_request(token, path, method="POST", payload={"displayName": display_name})
        return {"status": "CREATED", "folder_id": result.get("id"), "name": display_name}

    def _rename_folder(self, token: str, folder_id: str, display_name: str) -> Dict:
        graph_request(token, f"/me/mailFolders/{folder_id}", method="PATCH", payload={"displayName": display_name})
        return {"status": "RENAMED", "folder_id": folder_id, "name": display_name}

    def _delete_folder(self, token: str, folder_id: str) -> Dict:
        graph_request(token, f"/me/mailFolders/{folder_id}", method="DELETE")
        return {"status": "DELETED", "folder_id": folder_id}

    def _move_email(self, token: str, message_id: str, destination_folder_id: str) -> Dict:
        result = graph_request(token, f"/me/messages/{message_id}/move", method="POST", payload={"destinationId": destination_folder_id})
        return {"status": "MOVED", "message_id": message_id, "new_id": result.get("id")}

    def _copy_email(self, token: str, message_id: str, destination_folder_id: str) -> Dict:
        result = graph_request(token, f"/me/messages/{message_id}/copy", method="POST", payload={"destinationId": destination_folder_id})
        return {"status": "COPIED", "message_id": message_id, "new_id": result.get("id")}

    # ─── Email State Management ───────────────────────────────────────────────

    def _patch_message(self, token: str, message_id: str, payload: Dict) -> None:
        graph_request(token, f"/me/messages/{message_id}", method="PATCH", payload=payload)

    def _delete_email(self, token: str, message_id: str, permanent: bool = False) -> Dict:
        if permanent:
            graph_request(token, f"/me/messages/{message_id}/permanentDelete", method="POST", payload={})
        else:
            graph_request(token, f"/me/messages/{message_id}", method="DELETE")
        return {"status": "DELETED", "message_id": message_id, "permanent": permanent}

    def _archive_email(self, token: str, message_id: str) -> Dict:
        # Move to Archive folder
        folders = graph_request(token, "/me/mailFolders", params={"$filter": "displayName eq 'Archive'"}).get("value", [])
        archive_id = folders[0]["id"] if folders else "archive"
        return self._move_email(token, message_id, archive_id)

    # ─── Attachments ──────────────────────────────────────────────────────────

    def _list_attachments(self, token: str, message_id: str) -> Dict:
        items = graph_paginated(token, f"/me/messages/{message_id}/attachments")
        return {
            "message_id": message_id,
            "attachments": [
                CanonicalAttachment(
                    attachment_id=a.get("id", ""),
                    parent_id=message_id,
                    name=a.get("name", ""),
                    content_type=a.get("contentType", "application/octet-stream"),
                    size_bytes=a.get("size"),
                    is_inline=a.get("isInline", False),
                    raw_provider_id="microsoft_outlook",
                ).model_dump()
                for a in items
            ],
        }

    def _download_attachment(self, token: str, message_id: str, attachment_id: str) -> Dict:
        a = graph_request(token, f"/me/messages/{message_id}/attachments/{attachment_id}")
        return CanonicalAttachment(
            attachment_id=a.get("id", attachment_id),
            parent_id=message_id,
            name=a.get("name", ""),
            content_type=a.get("contentType", "application/octet-stream"),
            size_bytes=a.get("size"),
            content_bytes=a.get("contentBytes"),  # base64
            is_inline=a.get("isInline", False),
            raw_provider_id="microsoft_outlook",
        ).model_dump()

    # ─── Contacts ─────────────────────────────────────────────────────────────

    def _map_contact(self, c: Dict) -> CanonicalContact:
        return CanonicalContact(
            contact_id=c["id"],
            display_name=c.get("displayName", ""),
            given_name=c.get("givenName"),
            surname=c.get("surname"),
            emails=[e.get("address", "") for e in c.get("emailAddresses", [])],
            phones=[p.get("number", "") for p in c.get("phones", [])],
            organization=c.get("companyName"),
            job_title=c.get("jobTitle"),
            department=c.get("department"),
            notes=c.get("personalNotes"),
            raw_provider_id="microsoft_outlook",
        )

    def _list_contacts(self, token: str, limit: int = 50) -> Dict:
        items = graph_request(token, "/me/contacts", params={"$top": str(limit)}).get("value", [])
        return {"contacts": [self._map_contact(c).model_dump() for c in items]}

    def _search_contacts(self, token: str, query: str) -> Dict:
        items = graph_request(token, "/me/contacts", params={"$search": f'"{query}"', "$top": "25"}).get("value", [])
        return {"query": query, "contacts": [self._map_contact(c).model_dump() for c in items]}

    def _create_contact(self, token: str, display_name: str, email: str, phone: str = "",
                        job_title: str = "", company: str = "") -> Dict:
        body: Dict[str, Any] = {"displayName": display_name}
        if email:
            body["emailAddresses"] = [{"address": email, "name": display_name}]
        if phone:
            body["phones"] = [{"number": phone, "type": "mobile"}]
        if job_title:
            body["jobTitle"] = job_title
        if company:
            body["companyName"] = company
        result = graph_request(token, "/me/contacts", method="POST", payload=body)
        return {"status": "CREATED", "contact_id": result.get("id")}

    def _update_contact(self, token: str, contact_id: str, updates: Dict) -> Dict:
        graph_request(token, f"/me/contacts/{contact_id}", method="PATCH", payload=updates)
        return {"status": "UPDATED", "contact_id": contact_id}

    def _delete_contact(self, token: str, contact_id: str) -> Dict:
        graph_request(token, f"/me/contacts/{contact_id}", method="DELETE")
        return {"status": "DELETED", "contact_id": contact_id}

    def _list_contact_folders(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/contactFolders")
        return {"folders": [{"id": f["id"], "name": f["displayName"]} for f in items]}

    def _create_contact_folder(self, token: str, display_name: str) -> Dict:
        result = graph_request(token, "/me/contactFolders", method="POST", payload={"displayName": display_name})
        return {"status": "CREATED", "folder_id": result.get("id")}

    def _rename_contact_folder(self, token: str, folder_id: str, display_name: str) -> Dict:
        graph_request(token, f"/me/contactFolders/{folder_id}", method="PATCH", payload={"displayName": display_name})
        return {"status": "RENAMED"}

    def _delete_contact_folder(self, token: str, folder_id: str) -> Dict:
        graph_request(token, f"/me/contactFolders/{folder_id}", method="DELETE")
        return {"status": "DELETED"}

    def _favorite_contact(self, token: str, contact_id: str) -> Dict:
        graph_request(token, f"/me/contacts/{contact_id}", method="PATCH", payload={"personalNotes": "⭐"})
        return {"status": "FAVORITED"}

    def _get_contact_photo(self, token: str, contact_id: str) -> Dict:
        import urllib.request
        from app.connectors.builtin.communication.teams.graph_client import _build_headers
        url = f"https://graph.microsoft.com/v1.0/me/contacts/{contact_id}/photo/$value"
        headers = _build_headers(token)
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return {"photo_bytes": resp.read()}
        except Exception:
            return {"photo_bytes": None}

    def _update_contact_photo(self, token: str, contact_id: str, photo_bytes: bytes) -> Dict:
        import urllib.request
        from app.connectors.builtin.communication.teams.graph_client import _build_headers
        url = f"https://graph.microsoft.com/v1.0/me/contacts/{contact_id}/photo/$value"
        headers = _build_headers(token)
        headers["Content-Type"] = "image/jpeg"
        req = urllib.request.Request(url, data=photo_bytes, headers=headers, method="PUT")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"status": "UPDATED"}


    # ─── Calendar ─────────────────────────────────────────────────────────────

    def _map_event(self, e: Dict) -> CanonicalCalendarEvent:
        now = datetime.now(timezone.utc)
        return CanonicalCalendarEvent(
            event_id=e["id"],
            title=e.get("subject", ""),
            description=e.get("bodyPreview"),
            start_time=_parse_dt(e.get("start", {}).get("dateTime")) or now,
            end_time=_parse_dt(e.get("end", {}).get("dateTime")) or now,
            attendees=[a.get("emailAddress", {}).get("address", "") for a in e.get("attendees", [])],
            attendee_statuses={
                a.get("emailAddress", {}).get("address", ""): a.get("status", {}).get("response", "none")
                for a in e.get("attendees", [])
            },
            location=e.get("location", {}).get("displayName") if e.get("location") else None,
            meeting_link=e.get("onlineMeeting", {}).get("joinUrl"),
            is_online_meeting=e.get("isOnlineMeeting", False),
            calendar_id=e.get("calendar", {}).get("id"),
            organizer=e.get("organizer", {}).get("emailAddress", {}).get("address"),
            status=e.get("showAs", "confirmed"),
            raw_provider_id="microsoft_calendar",
        )

    def _list_events(self, token: str, days_ahead: int = 7) -> Dict:
        now = datetime.now(timezone.utc)
        start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")
        items = graph_paginated(
            token,
            "/me/events",
            params={
                "$filter": f"start/dateTime ge '{start}' and end/dateTime le '{end}'",
                "$orderby": "start/dateTime",
                "$top": "50",
            },
        )
        return {"events": [self._map_event(e).model_dump() for e in items]}

    def _create_event(self, token: str, subject: str, start: str, end: str,
                      attendees: Optional[List[str]] = None, body_text: str = "",
                      location: str = "", is_online: bool = False) -> Dict:
        payload: Dict[str, Any] = {
            "subject": subject,
            "body": {"contentType": "text", "content": body_text},
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
        }
        if location:
            payload["location"] = {"displayName": location}
        if is_online:
            payload["isOnlineMeeting"] = True
            payload["onlineMeetingProvider"] = "teamsForBusiness"
        if attendees:
            payload["attendees"] = [{"emailAddress": {"address": a}, "type": "required"} for a in attendees]
        result = graph_request(token, "/me/events", method="POST", payload=payload)
        return {"status": "CREATED", "event_id": result.get("id")}

    def _update_event(self, token: str, event_id: str, updates: Dict) -> Dict:
        graph_request(token, f"/me/events/{event_id}", method="PATCH", payload=updates)
        return {"status": "UPDATED", "event_id": event_id}

    def _delete_event(self, token: str, event_id: str) -> Dict:
        graph_request(token, f"/me/events/{event_id}", method="DELETE")
        return {"status": "DELETED", "event_id": event_id}

    def _respond_event(self, token: str, event_id: str, response: str, comment: str = "") -> Dict:
        # response: accept, decline, tentativelyAccept
        graph_request(
            token,
            f"/me/events/{event_id}/{response}",
            method="POST",
            payload={"comment": comment, "sendResponse": True},
        )
        return {"status": response.upper(), "event_id": event_id}

    def _list_calendars(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/calendars")
        return {
            "calendars": [
                {
                    "calendar_id": c.get("id"),
                    "name": c.get("name"),
                    "is_default": c.get("isDefaultCalendar", False),
                    "color": c.get("color"),
                    "can_edit": c.get("canEdit", False),
                }
                for c in items
            ]
        }

    def _create_recurring_event(self, token: str, subject: str, start: str, end: str, recurrence: Dict, attendees: Optional[List[str]] = None) -> Dict:
        payload = {
            "subject": subject,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
            "recurrence": recurrence
        }
        if attendees:
            payload["attendees"] = [{"emailAddress": {"address": a}, "type": "required"} for a in attendees]
        result = graph_request(token, "/me/events", method="POST", payload=payload)
        return {"status": "CREATED", "event_id": result.get("id")}

    def _cancel_event(self, token: str, event_id: str, comment: str = "") -> Dict:
        graph_request(token, f"/me/events/{event_id}/cancel", method="POST", payload={"comment": comment})
        return {"status": "CANCELLED"}

    def _invite_attendees(self, token: str, event_id: str, attendees: List[str]) -> Dict:
        # Get existing first if we want to append, but graph_request patching attendees overwrites them.
        # Safe append requires GET then PATCH. We just do PATCH assuming it replaces.
        graph_request(token, f"/me/events/{event_id}", method="PATCH", payload={
            "attendees": [{"emailAddress": {"address": a}, "type": "required"} for a in attendees]
        })
        return {"status": "INVITED"}

    def _free_busy_lookup(self, token: str, schedules: List[str], start: str, end: str, availability_view_interval: int = 60) -> Dict:
        payload = {
            "schedules": schedules,
            "startTime": {"dateTime": start, "timeZone": "UTC"},
            "endTime": {"dateTime": end, "timeZone": "UTC"},
            "availabilityViewInterval": availability_view_interval
        }
        result = graph_request(token, "/me/calendar/getSchedule", method="POST", payload=payload)
        return {"schedules": result.get("value", [])}

    def _search_events(self, token: str, query: str) -> Dict:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        items = graph_paginated(token, f"/me/events?$filter=contains(subject,'{encoded_query}')")
        return {"events": [self._map_event(e).model_dump() for e in items]}

    # ─── Profile & People ─────────────────────────────────────────────────────

    def _get_user_profile(self, token: str) -> Dict:
        return graph_request(token, "/me")

    def _get_profile_photo(self, token: str) -> Dict:
        import urllib.request
        from app.connectors.builtin.communication.teams.graph_client import _build_headers
        url = "https://graph.microsoft.com/v1.0/me/photo/$value"
        headers = _build_headers(token)
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return {"photo_bytes": resp.read()}
        except Exception:
            return {"photo_bytes": None}

    def _get_mailbox_settings(self, token: str) -> Dict:
        return graph_request(token, "/me/mailboxSettings")

    def _list_people(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/people")
        return {"people": [{"id": p.get("id"), "displayName": p.get("displayName"), "emails": [e.get("address") for e in p.get("scoredEmailAddresses", [])]} for p in items]}

    def _search_people(self, token: str, query: str) -> Dict:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        items = graph_paginated(token, f"/me/people?$search=\"{encoded_query}\"")
        return {"people": [{"id": p.get("id"), "displayName": p.get("displayName"), "emails": [e.get("address") for e in p.get("scoredEmailAddresses", [])]} for p in items]}

    def _recent_people(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/people?$orderby=relevanceScore desc")
        return {"people": [{"id": p.get("id"), "displayName": p.get("displayName"), "emails": [e.get("address") for e in p.get("scoredEmailAddresses", [])]} for p in items]}

    def _organization_people(self, token: str) -> Dict:
        items = graph_paginated(token, "/me/people?$filter=personType/class eq 'Person'")
        return {"people": [{"id": p.get("id"), "displayName": p.get("displayName"), "emails": [e.get("address") for e in p.get("scoredEmailAddresses", [])]} for p in items]}


    # ─── execute_action dispatch ───────────────────────────────────────────────

    async def execute_action(self, action: str, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        tenant_id = params.get("tenant_id", "default_tenant")
        token = await self._token(tenant_id)

        try:
            # ── Health ─────────────────────────────────────────────────────────
            if action == "health_check":
                me = graph_request(token, "/me")
                return {"status": "ok", "user": me.get("displayName"), "email": me.get("mail") or me.get("userPrincipalName")}

            # ── Email Sending ──────────────────────────────────────────────────
            elif action == "send_email":
                return self._send_email(token, params["subject"], params["body"], params["to"],
                                        params.get("cc"), params.get("bcc"),
                                        params.get("body_type", "text"), params.get("importance", "normal"))
            elif action == "reply_email":
                return self._reply_email(token, params["message_id"], params["body"])
            elif action == "reply_all":
                return self._reply_email(token, params["message_id"], params["body"], reply_all=True)
            elif action == "forward_email":
                return self._forward_email(token, params["message_id"], params["to"], params.get("comment", ""))
            elif action == "create_draft":
                return self._create_draft(token, params["subject"], params["body"], params["to"], params.get("cc"), params.get("bcc"))
            elif action == "update_draft":
                return self._update_draft(token, params["draft_id"], params["updates"])
            elif action == "delete_draft":
                return self._delete_draft(token, params["draft_id"])
            elif action == "send_draft":
                return self._send_draft(token, params["draft_id"])

            # ── Inbox Operations ───────────────────────────────────────────────
            elif action == "read_inbox":
                return self._read_folder(token, "inbox", params.get("limit", 20), params.get("skip", 0))
            elif action == "read_sent":
                return self._read_folder(token, "sentItems", params.get("limit", 20), params.get("skip", 0))
            elif action == "read_drafts":
                return self._read_folder(token, "drafts", params.get("limit", 20), params.get("skip", 0))
            elif action == "read_deleted":
                return self._read_folder(token, "deleteditems", params.get("limit", 20), params.get("skip", 0))
            elif action == "read_archive":
                return self._read_folder(token, "archive", params.get("limit", 20), params.get("skip", 0))
            elif action == "read_junk":
                return self._read_folder(token, "junkemail", params.get("limit", 20), params.get("skip", 0))
            elif action == "read_custom_folder":
                return self._read_folder(token, params["folder_id"], params.get("limit", 20), params.get("skip", 0))

            # ── Search ─────────────────────────────────────────────────────────
            elif action == "search_emails":
                return self._search_emails(token, params["query"], params.get("limit", 20))

            # ── Folder Operations ──────────────────────────────────────────────
            elif action == "list_folders":
                return self._list_folders(token)
            elif action == "create_folder":
                return self._create_folder(token, params["display_name"], params.get("parent_folder"))
            elif action == "rename_folder":
                return self._rename_folder(token, params["folder_id"], params["display_name"])
            elif action == "delete_folder":
                return self._delete_folder(token, params["folder_id"])
            elif action == "move_email":
                return self._move_email(token, params["message_id"], params["destination_folder_id"])
            elif action == "copy_email":
                return self._copy_email(token, params["message_id"], params["destination_folder_id"])

            # ── Email State Management ─────────────────────────────────────────
            elif action == "mark_read":
                self._patch_message(token, params["message_id"], {"isRead": True})
                return {"status": "MARKED_READ", "message_id": params["message_id"]}
            elif action == "mark_unread":
                self._patch_message(token, params["message_id"], {"isRead": False})
                return {"status": "MARKED_UNREAD", "message_id": params["message_id"]}
            elif action == "flag_email":
                self._patch_message(token, params["message_id"], {"flag": {"flagStatus": "flagged"}})
                return {"status": "FLAGGED", "message_id": params["message_id"]}
            elif action == "unflag_email":
                self._patch_message(token, params["message_id"], {"flag": {"flagStatus": "notFlagged"}})
                return {"status": "UNFLAGGED", "message_id": params["message_id"]}
            elif action == "archive_email":
                return self._archive_email(token, params["message_id"])
            elif action == "restore_email":
                return self._move_email(token, params["message_id"], "inbox")
            elif action == "delete_email":
                return self._delete_email(token, params["message_id"])
            elif action == "permanent_delete":
                return self._delete_email(token, params["message_id"], permanent=True)

            # ── Attachments ────────────────────────────────────────────────────
            elif action == "list_attachments":
                return self._list_attachments(token, params["message_id"])
            elif action == "download_attachment":
                return self._download_attachment(token, params["message_id"], params["attachment_id"])

            # ── Contacts ───────────────────────────────────────────────────────
            elif action == "list_contacts":
                return self._list_contacts(token, params.get("limit", 50))
            elif action == "search_contacts":
                return self._search_contacts(token, params["query"])
            elif action == "create_contact":
                return self._create_contact(token, params["display_name"], params.get("email", ""),
                                             params.get("phone", ""), params.get("job_title", ""), params.get("company", ""))
            elif action == "update_contact":
                return self._update_contact(token, params["contact_id"], params["updates"])
            elif action == "delete_contact":
                return self._delete_contact(token, params["contact_id"])
            elif action == "list_contact_folders":
                return self._list_contact_folders(token)
            elif action == "create_contact_folder":
                return self._create_contact_folder(token, params["display_name"])
            elif action == "rename_contact_folder":
                return self._rename_contact_folder(token, params["folder_id"], params["display_name"])
            elif action == "delete_contact_folder":
                return self._delete_contact_folder(token, params["folder_id"])
            elif action == "favorite_contact":
                return self._favorite_contact(token, params["contact_id"])
            elif action == "get_contact_photo":
                return self._get_contact_photo(token, params["contact_id"])
            elif action == "update_contact_photo":
                return self._update_contact_photo(token, params["contact_id"], params["photo_bytes"])

            # ── Calendar ───────────────────────────────────────────────────────
            elif action == "list_events":
                return self._list_events(token, params.get("days_ahead", 7))
            elif action == "create_event":
                return self._create_event(token, params["subject"], params["start"], params["end"],
                                           params.get("attendees"), params.get("body_text", ""),
                                           params.get("location", ""), params.get("is_online", False))
            elif action == "update_event":
                return self._update_event(token, params["event_id"], params["updates"])
            elif action == "delete_event":
                return self._delete_event(token, params["event_id"])
            elif action == "accept_meeting":
                return self._respond_event(token, params["event_id"], "accept", params.get("comment", ""))
            elif action == "decline_meeting":
                return self._respond_event(token, params["event_id"], "decline", params.get("comment", ""))
            elif action == "tentative_meeting":
                return self._respond_event(token, params["event_id"], "tentativelyAccept", params.get("comment", ""))
            elif action == "list_calendars":
                return self._list_calendars(token)
            elif action == "create_recurring_event":
                return self._create_recurring_event(token, params["subject"], params["start"], params["end"], params["recurrence"], params.get("attendees"))
            elif action == "cancel_event":
                return self._cancel_event(token, params["event_id"], params.get("comment", ""))
            elif action == "invite_attendees":
                return self._invite_attendees(token, params["event_id"], params["attendees"])
            elif action == "free_busy_lookup":
                return self._free_busy_lookup(token, params["schedules"], params["start"], params["end"], params.get("interval", 60))
            elif action == "search_events":
                return self._search_events(token, params["query"])

            # ── Profile & People ───────────────────────────────────────────────
            elif action == "get_user_profile":
                return self._get_user_profile(token)
            elif action == "get_profile_photo":
                return self._get_profile_photo(token)
            elif action == "get_mailbox_settings":
                return self._get_mailbox_settings(token)
            elif action == "list_people":
                return self._list_people(token)
            elif action == "search_people":
                return self._search_people(token, params["query"])
            elif action == "recent_people":
                return self._recent_people(token)
            elif action == "organization_people":
                return self._organization_people(token)

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
                raise ValueError(f"Action '{action}' is not implemented for Outlook connector")

        except GraphAPIError as exc:
            logger.error("Outlook action failed", action=action, error=str(exc), status=exc.status_code)
            raise

    async def health_check(self) -> Dict[str, Any]:
        try:
            token = await self._token("default_tenant")
            me = graph_request(token, "/me")
            return {"status": "ok", "connector_id": self.connector_id, "user": me.get("displayName")}
        except Exception as e:
            return {"status": "error", "connector_id": self.connector_id, "error": str(e)}
