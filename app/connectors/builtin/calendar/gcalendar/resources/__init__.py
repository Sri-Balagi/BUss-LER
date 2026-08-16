"""Google Calendar Resources — Package init"""
from app.connectors.builtin.calendar.gcalendar.resources.calendars_events_freebusy_watch_settings import (
    CalendarCalendarsResource,
    CalendarEventsResource,
    CalendarFreeBusyResource,
    CalendarWatchResource,
    CalendarSettingsResource,
)

__all__ = [
    "CalendarCalendarsResource",
    "CalendarEventsResource",
    "CalendarFreeBusyResource",
    "CalendarWatchResource",
    "CalendarSettingsResource",
]
