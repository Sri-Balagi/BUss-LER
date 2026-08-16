"""Google Calendar — Calendar & Events Resource Handlers"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class CalendarCalendarsResource:
    """Manages calendars and ACL for Google Calendar API v3."""

    def __init__(self, service: Any) -> None:
        self._calendars = service.calendars()
        self._calendar_list = service.calendarList()
        self._acl = service.acl()

    async def list_calendars(
        self,
        page_token: Optional[str] = None,
        show_deleted: bool = False,
        show_hidden: bool = False,
        min_access_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all calendars accessible to the user."""
        kwargs: Dict[str, Any] = {
            "showDeleted": show_deleted,
            "showHidden": show_hidden,
        }
        if page_token:
            kwargs["pageToken"] = page_token
        if min_access_role:
            kwargs["minAccessRole"] = min_access_role
        return self._calendar_list.list(**kwargs).execute()

    async def get_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """Get a specific calendar by ID."""
        return self._calendars.get(calendarId=calendar_id).execute()

    async def create_calendar(
        self,
        summary: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        time_zone: str = "UTC",
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"summary": summary, "timeZone": time_zone}
        if description:
            body["description"] = description
        if location:
            body["location"] = location
        return self._calendars.insert(body=body).execute()

    async def update_calendar(
        self,
        calendar_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if summary:
            body["summary"] = summary
        if description:
            body["description"] = description
        if location:
            body["location"] = location
        if time_zone:
            body["timeZone"] = time_zone
        return self._calendars.patch(calendarId=calendar_id, body=body).execute()

    async def delete_calendar(self, calendar_id: str) -> Dict[str, Any]:
        self._calendars.delete(calendarId=calendar_id).execute()
        return {"status": "DELETED", "calendar_id": calendar_id}

    async def clear_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """Delete all events from a calendar (primary calendar only)."""
        self._calendars.clear(calendarId=calendar_id).execute()
        return {"status": "CLEARED", "calendar_id": calendar_id}

    # ── ACL ──────────────────────────────────────────────────────────────────

    async def list_acl(
        self, calendar_id: str, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "calendarId": calendar_id,
            "fields": "nextPageToken,items(id,role,scope)",
        }
        if page_token:
            kwargs["pageToken"] = page_token
        return self._acl.list(**kwargs).execute()

    async def create_acl(
        self,
        calendar_id: str,
        role: str,
        scope_type: str,
        scope_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Grant calendar access. role: 'owner','writer','reader','freeBusyReader'."""
        body: Dict[str, Any] = {"role": role, "scope": {"type": scope_type}}
        if scope_value:
            body["scope"]["value"] = scope_value
        return self._acl.insert(calendarId=calendar_id, body=body).execute()

    async def delete_acl(self, calendar_id: str, rule_id: str) -> Dict[str, Any]:
        self._acl.delete(calendarId=calendar_id, ruleId=rule_id).execute()
        return {"status": "DELETED", "rule_id": rule_id}


class CalendarEventsResource:
    """Manages events for Google Calendar API v3."""

    def __init__(self, service: Any) -> None:
        self._events = service.events()

    async def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
        max_results: int = 250,
        order_by: str = "startTime",
        single_events: bool = True,
        show_deleted: bool = False,
        sync_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List calendar events with full filtering support."""
        kwargs: Dict[str, Any] = {
            "calendarId": calendar_id,
            "maxResults": min(max_results, 2500),
            "singleEvents": single_events,
            "showDeleted": show_deleted,
        }
        if not sync_token:
            # time bounds only allowed without syncToken
            kwargs["orderBy"] = order_by
            if time_min:
                kwargs["timeMin"] = time_min
            if time_max:
                kwargs["timeMax"] = time_max
        if query:
            kwargs["q"] = query
        if page_token:
            kwargs["pageToken"] = page_token
        if sync_token:
            kwargs["syncToken"] = sync_token
        return self._events.list(**kwargs).execute()

    async def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        return self._events.get(calendarId=calendar_id, eventId=event_id).execute()

    async def create_event(
        self,
        calendar_id: str,
        summary: str,
        start: Dict[str, str],
        end: Dict[str, str],
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
        recurrence: Optional[List[str]] = None,
        conference_data: Optional[Dict[str, Any]] = None,
        reminders: Optional[Dict[str, Any]] = None,
        visibility: str = "default",
        status: str = "confirmed",
        attachments: Optional[List[Dict[str, Any]]] = None,
        send_updates: str = "all",
    ) -> Dict[str, Any]:
        """Create a calendar event with full metadata.

        Args:
            start/end: {"dateTime": "2026-01-01T10:00:00", "timeZone": "Asia/Kolkata"}
                    or {"date": "2026-01-01"} for all-day events.
            conference_data: Pass {"createRequest": {"requestId": "...", "conferenceSolutionKey": {"type": "hangoutsMeet"}}}
                             to auto-create a Google Meet link.
        """
        body: Dict[str, Any] = {
            "summary": summary,
            "start": start,
            "end": end,
            "status": status,
            "visibility": visibility,
        }
        if description:
            body["description"] = description
        if location:
            body["location"] = location
        if attendees:
            body["attendees"] = attendees
        if recurrence:
            body["recurrence"] = recurrence
        if conference_data:
            body["conferenceData"] = conference_data
        if reminders:
            body["reminders"] = reminders
        if attachments:
            body["attachments"] = attachments

        kwargs: Dict[str, Any] = {
            "calendarId": calendar_id,
            "body": body,
            "sendUpdates": send_updates,
        }
        if conference_data:
            kwargs["conferenceDataVersion"] = 1

        return self._events.insert(**kwargs).execute()

    async def create_event_with_meet(
        self,
        calendar_id: str,
        summary: str,
        start: Dict[str, str],
        end: Dict[str, str],
        attendees: Optional[List[Dict[str, str]]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convenience method: create event and auto-generate a Google Meet link."""
        import uuid
        conference_data = {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }
        return await self.create_event(
            calendar_id=calendar_id,
            summary=summary,
            start=start,
            end=end,
            attendees=attendees,
            description=description,
            conference_data=conference_data,
        )

    async def update_event(
        self,
        calendar_id: str,
        event_id: str,
        updates: Dict[str, Any],
        send_updates: str = "all",
    ) -> Dict[str, Any]:
        """Patch an existing event with partial updates."""
        return self._events.patch(
            calendarId=calendar_id,
            eventId=event_id,
            body=updates,
            sendUpdates=send_updates,
        ).execute()

    async def delete_event(
        self,
        calendar_id: str,
        event_id: str,
        send_updates: str = "all",
    ) -> Dict[str, Any]:
        self._events.delete(
            calendarId=calendar_id, eventId=event_id, sendUpdates=send_updates
        ).execute()
        return {"status": "DELETED", "event_id": event_id}

    async def move_event(
        self,
        calendar_id: str,
        event_id: str,
        destination_calendar_id: str,
    ) -> Dict[str, Any]:
        """Move an event to a different calendar."""
        return self._events.move(
            calendarId=calendar_id,
            eventId=event_id,
            destination=destination_calendar_id,
        ).execute()

    async def import_event(
        self, calendar_id: str, event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Import an iCal-compatible event."""
        return self._events.import_(calendarId=calendar_id, body=event_data).execute()

    async def list_instances(
        self,
        calendar_id: str,
        event_id: str,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        page_token: Optional[str] = None,
        max_results: int = 250,
    ) -> Dict[str, Any]:
        """List instances of a recurring event."""
        kwargs: Dict[str, Any] = {
            "calendarId": calendar_id,
            "eventId": event_id,
            "maxResults": min(max_results, 2500),
        }
        if time_min:
            kwargs["timeMin"] = time_min
        if time_max:
            kwargs["timeMax"] = time_max
        if page_token:
            kwargs["pageToken"] = page_token
        return self._events.instances(**kwargs).execute()

    async def quick_add_event(
        self, calendar_id: str, text: str
    ) -> Dict[str, Any]:
        """Create an event from a natural language text string."""
        return self._events.quickAdd(calendarId=calendar_id, text=text).execute()


class CalendarFreeBusyResource:
    """Free/busy query for availability checking."""

    def __init__(self, service: Any) -> None:
        self._freebusy = service.freebusy()

    async def query(
        self,
        time_min: str,
        time_max: str,
        calendar_ids: List[str],
        time_zone: str = "UTC",
        group_expansion_max: int = 100,
        calendar_expansion_max: int = 50,
    ) -> Dict[str, Any]:
        """Query free/busy information for calendars in a time range."""
        items = [{"id": cid} for cid in calendar_ids]
        return self._freebusy.query(body={
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": time_zone,
            "groupExpansionMax": group_expansion_max,
            "calendarExpansionMax": calendar_expansion_max,
            "items": items,
        }).execute()


class CalendarWatchResource:
    """Push notifications for calendar changes."""

    def __init__(self, service: Any) -> None:
        self._events = service.events()
        self._calendar_list = service.calendarList()

    async def watch_events(
        self,
        calendar_id: str,
        channel_id: str,
        webhook_url: str,
        expiration_ms: Optional[int] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Subscribe to push notifications for a calendar's events."""
        body: Dict[str, Any] = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
        }
        if expiration_ms:
            body["expiration"] = str(expiration_ms)
        if token:
            body["token"] = token
        return self._events.watch(calendarId=calendar_id, body=body).execute()

    async def watch_calendar_list(
        self,
        channel_id: str,
        webhook_url: str,
    ) -> Dict[str, Any]:
        """Subscribe to notifications for the user's calendar list."""
        return self._calendar_list.watch(body={
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
        }).execute()


class CalendarSettingsResource:
    """User calendar settings."""

    def __init__(self, service: Any) -> None:
        self._settings = service.settings()

    async def list_settings(self) -> Dict[str, Any]:
        return self._settings.list(
            fields="items(id,value,kind,etag)"
        ).execute()

    async def get_setting(self, setting_id: str) -> Dict[str, Any]:
        """Get a specific setting (e.g. 'timezone', 'locale', 'dateFieldOrder')."""
        return self._settings.get(setting=setting_id).execute()
