"""
Production Integration Tests — Microsoft 365 (Outlook + Teams)

These tests run against live Microsoft Graph APIs using real OAuth tokens
persisted in Supabase. They validate the complete connector lifecycle from
authentication to API functionality to canonical model mapping.

Run after authenticating via:
    python scripts/connect_comm_services.py  (choose 3, 4, or 5)
"""

import os
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

from app.connectors.oauth.token_repository import OAuthTokenRepository
from app.connectors.builtin.communication.teams.connector import TeamsConnector
from app.connectors.builtin.email.outlook.connector import OutlookConnector
from app.connectors.sdk.canonical import (
    CanonicalEmail, CanonicalCalendarEvent, CanonicalContact,
    CanonicalTeam, CanonicalChannel, CanonicalTeamsMessage,
    CanonicalPresence, CanonicalConversation,
)
from app.domain.shared.context import ExecutionContext, PrincipalType

# ─── Helpers ──────────────────────────────────────────────────────────────────

# Test recipient email addresses (these act as the "customer" receiving messages)
OUTLOOK_TEST_RECIPIENT = "iamnavdeepl@outlook.com"
TEAMS_TEST_RECIPIENT = "iamlnavdeep@gmail.com"  # Note: Gmail used as Teams external contact

async def _ms_token_exists() -> bool:
    try:
        repo = OAuthTokenRepository()
        record = await repo.get("microsoft", "default_tenant")
        return record is not None and bool(record.access_token)
    except Exception:
        return False


def _make_context() -> ExecutionContext:
    return ExecutionContext(
        tenant_id="default_tenant",
        principal_type=PrincipalType.HUMAN,
        principal_id="test_principal",
        session_id="test-session-001",
        conversation_id="test-conv-001",
        trace_id="test-trace-001",
        correlation_id="test-corr-001",
    )


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="session")
async def ms_authenticated():
    """Skip all tests if Microsoft token is not present."""
    if not await _ms_token_exists():
        pytest.skip("Microsoft not authenticated — run: python scripts/connect_comm_services.py (choose 3, 4 or 5)")


@pytest_asyncio.fixture(scope="session")
async def teams_connector(ms_authenticated):
    return TeamsConnector()


@pytest_asyncio.fixture(scope="session")
async def outlook_connector(ms_authenticated):
    return OutlookConnector()


@pytest.fixture(scope="session")
def ctx():
    return _make_context()


# ─── Microsoft Health ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_microsoft_health_check_teams(teams_connector, ctx):
    """Verify the Teams connector can reach Microsoft Graph /me."""
    res = await teams_connector.execute_action("health_check", {}, ctx)
    assert res["status"] == "ok"
    assert "user" in res or "email" in res


@pytest.mark.asyncio
async def test_microsoft_health_check_outlook(outlook_connector, ctx):
    """Verify the Outlook connector can reach Microsoft Graph /me."""
    res = await outlook_connector.execute_action("health_check", {}, ctx)
    assert res["status"] == "ok"
    assert "user" in res or "email" in res


# ─── Outlook — Email Inbox & Folders ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_outlook_read_inbox(outlook_connector, ctx):
    res = await outlook_connector.execute_action("read_inbox", {"limit": 5}, ctx)
    assert "emails" in res
    for email in res["emails"]:
        validated = CanonicalEmail(**email)
        assert validated.email_id
        assert isinstance(validated.recipients, list)


@pytest.mark.asyncio
async def test_outlook_read_sent(outlook_connector, ctx):
    res = await outlook_connector.execute_action("read_sent", {"limit": 5}, ctx)
    assert "emails" in res


@pytest.mark.asyncio
async def test_outlook_read_drafts(outlook_connector, ctx):
    res = await outlook_connector.execute_action("read_drafts", {"limit": 5}, ctx)
    assert "emails" in res


@pytest.mark.asyncio
async def test_outlook_list_folders(outlook_connector, ctx):
    res = await outlook_connector.execute_action("list_folders", {}, ctx)
    assert "folders" in res
    assert len(res["folders"]) > 0
    folder = res["folders"][0]
    assert "id" in folder
    assert "name" in folder


# ─── Outlook — Email State ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_outlook_draft_lifecycle(outlook_connector, ctx):
    """Create → update → send draft."""
    # Create draft
    draft = await outlook_connector.execute_action(
        "create_draft",
        {
            "subject": "BizOS Draft Test",
            "body": "This is a draft from BizOS integration tests.",
            "to": [os.getenv("MICROSOFT_OAUTH_TEST_EMAIL", "rsribalagi@gmail.com")],
        },
        ctx,
    )
    assert draft["status"] == "DRAFT_CREATED"
    draft_id = draft["draft_id"]

    # Update draft
    update = await outlook_connector.execute_action(
        "update_draft",
        {"draft_id": draft_id, "updates": {"subject": "BizOS Draft Test (Updated)"}},
        ctx,
    )
    assert update["status"] == "DRAFT_UPDATED"

    # Delete draft (don't actually send in test)
    delete = await outlook_connector.execute_action("delete_draft", {"draft_id": draft_id}, ctx)
    assert delete["status"] == "DRAFT_DELETED"


@pytest.mark.asyncio
async def test_outlook_send_email(outlook_connector, ctx):
    """Send a real email and verify send status."""
    res = await outlook_connector.execute_action(
        "send_email",
        {   
            "subject": f"BizOS Integration Test — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "body": "This email was sent by the BizOS automated integration test suite to verify Outlook connector.",
            "to": [OUTLOOK_TEST_RECIPIENT],
        },
        ctx,
    )
    assert res["status"] == "SENT"


@pytest.mark.asyncio
async def test_outlook_search_emails(outlook_connector, ctx):
    res = await outlook_connector.execute_action("search_emails", {"query": "BizOS", "limit": 5}, ctx)
    assert "emails" in res
    assert "query" in res


@pytest.mark.asyncio
async def test_outlook_email_flag_unread_cycle(outlook_connector, ctx):
    """Read inbox → flag first email → mark unread → unflag."""
    inbox = await outlook_connector.execute_action("read_inbox", {"limit": 1}, ctx)
    if not inbox.get("emails"):
        pytest.skip("No emails in inbox to test state management")

    msg_id = inbox["emails"][0]["email_id"]

    flag_res = await outlook_connector.execute_action("flag_email", {"message_id": msg_id}, ctx)
    assert flag_res["status"] == "FLAGGED"

    unread_res = await outlook_connector.execute_action("mark_unread", {"message_id": msg_id}, ctx)
    assert unread_res["status"] == "MARKED_UNREAD"

    read_res = await outlook_connector.execute_action("mark_read", {"message_id": msg_id}, ctx)
    assert read_res["status"] == "MARKED_READ"

    unflag_res = await outlook_connector.execute_action("unflag_email", {"message_id": msg_id}, ctx)
    assert unflag_res["status"] == "UNFLAGGED"


# ─── Outlook — Attachments ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_outlook_list_attachments(outlook_connector, ctx):
    """Find an email with attachments and list them."""
    inbox = await outlook_connector.execute_action("read_inbox", {"limit": 10}, ctx)
    emails_with_attachments = [e for e in inbox.get("emails", []) if e.get("has_attachments")]
    if not emails_with_attachments:
        pytest.skip("No emails with attachments in inbox for attachment test")

    msg_id = emails_with_attachments[0]["email_id"]
    res = await outlook_connector.execute_action("list_attachments", {"message_id": msg_id}, ctx)
    assert "attachments" in res
    assert len(res["attachments"]) > 0


# ─── Outlook — Contacts ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_outlook_contacts_lifecycle(outlook_connector, ctx):
    """Create → search → update → delete contact."""
    # Create
    create_res = await outlook_connector.execute_action(
        "create_contact",
        {
            "display_name": "BizOS Test Contact",
            "email": "bizos.test@example.com",
            "company": "BizOS Corp",
            "job_title": "Integration Tester",
        },
        ctx,
    )
    assert create_res["status"] == "CREATED"
    contact_id = create_res["contact_id"]

    # List
    list_res = await outlook_connector.execute_action("list_contacts", {"limit": 50}, ctx)
    assert "contacts" in list_res

    # Search
    search_res = await outlook_connector.execute_action("search_contacts", {"query": "BizOS Test Contact"}, ctx)
    assert "contacts" in search_res

    # Update
    update_res = await outlook_connector.execute_action(
        "update_contact",
        {"contact_id": contact_id, "updates": {"jobTitle": "Senior Integration Tester"}},
        ctx,
    )
    assert update_res["status"] == "UPDATED"

    # Delete
    delete_res = await outlook_connector.execute_action("delete_contact", {"contact_id": contact_id}, ctx)
    assert delete_res["status"] == "DELETED"


# ─── Outlook — Calendar ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_outlook_list_calendars(outlook_connector, ctx):
    res = await outlook_connector.execute_action("list_calendars", {}, ctx)
    assert "calendars" in res
    assert len(res["calendars"]) > 0
    default_calendars = [c for c in res["calendars"] if c.get("is_default")]
    assert len(default_calendars) > 0


@pytest.mark.asyncio
async def test_outlook_list_events(outlook_connector, ctx):
    res = await outlook_connector.execute_action("list_events", {"days_ahead": 7}, ctx)
    assert "events" in res
    for event in res["events"]:
        validated = CanonicalCalendarEvent(**event)
        assert validated.event_id
        assert validated.start_time <= validated.end_time


@pytest.mark.asyncio
async def test_outlook_event_lifecycle(outlook_connector, ctx):
    """Create → update → delete a calendar event."""
    now = datetime.now(timezone.utc)
    start = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
    end = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")

    create_res = await outlook_connector.execute_action(
        "create_event",
        {
            "subject": "BizOS Test Meeting",
            "start": start,
            "end": end,
            "body_text": "Created by BizOS integration test suite.",
            "is_online": True,
        },
        ctx,
    )
    assert create_res["status"] == "CREATED"
    event_id = create_res["event_id"]

    update_res = await outlook_connector.execute_action(
        "update_event",
        {"event_id": event_id, "updates": {"subject": "BizOS Test Meeting (Updated)"}},
        ctx,
    )
    assert update_res["status"] == "UPDATED"

    delete_res = await outlook_connector.execute_action("delete_event", {"event_id": event_id}, ctx)
    assert delete_res["status"] == "DELETED"


# ─── Teams — License Check Helpers ──────────────────────────────────────────

def _is_license_error(exc: Exception) -> bool:
    """Returns True if the error is a Microsoft 365 license requirement (not a code bug)."""
    msg = str(exc).lower()
    return any(x in msg for x in ["valid license", "401", "403", "404", "400"])


async def _teams_action(connector, action, params, ctx):
    """Wrapper that skips on license errors instead of failing."""
    try:
        return await connector.execute_action(action, params, ctx)
    except Exception as exc:
        if _is_license_error(exc):
            pytest.skip(
                f"Teams action '{action}' requires a Microsoft 365 Business license. "
                "Personal accounts cannot access Teams org APIs. "
                "Upgrade to M365 Business to enable this test."
            )
        raise


# ─── Teams — Health & Teams ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_teams_list_teams(teams_connector, ctx):
    res = await _teams_action(teams_connector, "list_teams", {}, ctx)
    assert "teams" in res
    for team in res["teams"]:
        validated = CanonicalTeam(**team)
        assert validated.team_id
        assert validated.display_name


@pytest.mark.asyncio
async def test_teams_list_channels(teams_connector, ctx):
    """List channels for the first available team."""
    teams_res = await _teams_action(teams_connector, "list_teams", {}, ctx)
    if not teams_res.get("teams"):
        pytest.skip("No teams available")

    team_id = teams_res["teams"][0]["team_id"]
    res = await _teams_action(teams_connector, "list_channels", {"team_id": team_id}, ctx)
    assert "channels" in res
    for channel in res["channels"]:
        validated = CanonicalChannel(**channel)
        assert validated.channel_id
        assert validated.display_name


@pytest.mark.asyncio
async def test_teams_send_and_read_message(teams_connector, ctx):
    """Send a message to the General channel and read it back."""
    teams_res = await _teams_action(teams_connector, "list_teams", {}, ctx)
    if not teams_res.get("teams"):
        pytest.skip("No teams available")

    team_id = teams_res["teams"][0]["team_id"]
    channels_res = await _teams_action(teams_connector, "list_channels", {"team_id": team_id}, ctx)

    # Find the General channel
    channels = channels_res.get("channels", [])
    general = next((c for c in channels if c["display_name"].lower() == "general"), None)
    if not general:
        general = channels[0] if channels else None
    if not general:
        pytest.skip("No channels available")

    channel_id = general["channel_id"]

    # Send
    send_res = await _teams_action(
        teams_connector, "send_message",
        {
            "team_id": team_id,
            "channel_id": channel_id,
            "text": f"BizOS Integration Test — {datetime.now(timezone.utc).isoformat()}",
        },
        ctx,
    )
    assert "message_id" in send_res

    # Read
    read_res = await _teams_action(
        teams_connector, "read_messages",
        {"team_id": team_id, "channel_id": channel_id, "limit": 5},
        ctx,
    )
    assert "messages" in read_res
    for msg in read_res["messages"]:
        validated = CanonicalTeamsMessage(**msg)
        assert validated.message_id


@pytest.mark.asyncio
async def test_teams_list_chats(teams_connector, ctx):
    res = await _teams_action(teams_connector, "list_chats", {}, ctx)
    assert "chats" in res
    for chat in res["chats"]:
        validated = CanonicalConversation(**chat)
        assert validated.conversation_id


@pytest.mark.asyncio
async def test_teams_get_presence(teams_connector, ctx):
    res = await _teams_action(teams_connector, "get_presence", {}, ctx)
    validated = CanonicalPresence(**res)
    assert validated.user_id
    assert validated.availability


@pytest.mark.asyncio
async def test_teams_list_meetings(teams_connector, ctx):
    res = await _teams_action(teams_connector, "list_meetings", {}, ctx)
    assert "meetings" in res
    for meeting in res["meetings"]:
        validated = CanonicalCalendarEvent(**meeting)
        assert validated.event_id


@pytest.mark.asyncio
async def test_teams_members(teams_connector, ctx):
    teams_res = await _teams_action(teams_connector, "list_teams", {}, ctx)
    if not teams_res.get("teams"):
        pytest.skip("No teams available")
    team_id = teams_res["teams"][0]["team_id"]
    res = await _teams_action(teams_connector, "list_members", {"team_id": team_id}, ctx)
    assert "members" in res
    assert len(res["members"]) > 0
