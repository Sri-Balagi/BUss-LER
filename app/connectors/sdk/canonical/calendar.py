"""Canonical Calendar Business SDK.

Providers:
  Google Calendar   → CanonicalCalendarEvent, CanonicalCalendar, CanonicalFreeBusy
  Microsoft Outlook → CanonicalCalendarEvent, CanonicalCalendar (future)
"""
try:
    from app.connectors.sdk.canonical import (  # noqa: F401
        CanonicalCalendarEvent,  # type: ignore
        CanonicalCalendar,       # type: ignore
        CanonicalFreeBusy,       # type: ignore
    )
except ImportError:
    pass
