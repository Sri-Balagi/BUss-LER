import pytest
from app.connectors.builtin.communication.slack.connector import SlackConnector
from app.domain.shared.context import ExecutionContext
from app.infrastructure.persistence.postgres.supabase import SupabaseService

@pytest.fixture(autouse=True)
def reset_supabase():
    SupabaseService.reset()
    yield
    SupabaseService.reset()

@pytest.fixture
def slack_connector():
    return SlackConnector()

@pytest.fixture
def execution_context():
    return ExecutionContext(
        tenant_id="default_tenant",
        principal_id="test_principal",
        session_id="test_session",
        conversation_id="test_conversation",
        trace_id="test_trace",
        correlation_id="test_correlation"
    )

@pytest.mark.asyncio
async def test_slack_health_check(slack_connector):
    res = await slack_connector.health_check()
    # If the token is missing, this might fail or return error status, 
    # but we assume the token is present via the CLI flow.
    if res.get("status") == "error":
        pytest.skip("Slack not authenticated. Run CLI setup first.")
    
    assert res.get("status") == "ok"
    assert "team" in res

@pytest.mark.asyncio
async def test_slack_list_channels(slack_connector, execution_context):
    try:
        res = await slack_connector.execute_action("list_channels", {}, execution_context)
        assert "channels" in res
        assert isinstance(res["channels"], list)
    except Exception as e:
        if "No tokens found" in str(e):
            pytest.skip("Slack not authenticated")
        raise

@pytest.mark.asyncio
async def test_slack_send_and_read_message(slack_connector, execution_context):
    # First, list channels to find a suitable one (e.g., 'general' or the first available)
    try:
        channels_res = await slack_connector.execute_action("list_channels", {}, execution_context)
    except Exception as e:
        if "No tokens found" in str(e):
            pytest.skip("Slack not authenticated")
        raise
        
    channels = channels_res.get("channels", [])
    if not channels:
        pytest.skip("No channels available to send a message to")

    # Find a channel the bot is already a member of
    target_channel = next((c for c in channels if c.get("is_member")), None)
    
    if not target_channel:
        # If not a member of any, let's just pick the first one and try
        # Note: this will fail with not_in_channel unless the bot has chat:write.public
        # or the user manually invites the bot to the channel.
        target_channel = channels[0]

    channel_id = target_channel["id"]
    test_message = "Hello from BizOS Integration Test!"
    
    # Send message
    send_res = await slack_connector.execute_action(
        "send_message", 
        {"channel": channel_id, "text": test_message}, 
        execution_context
    )
    assert send_res.get("status") == "SENT"
    assert "message_id" in send_res
    
    msg_id = send_res["message_id"]
    
    # Read history and verify message
    read_res = await slack_connector.execute_action(
        "read_channel_history", 
        {"channel": channel_id, "limit": 5}, 
        execution_context
    )
    
    messages = read_res.get("messages", [])
    assert len(messages) > 0
    # The sent message should be recent
    found = any(m["message_id"] == msg_id and m["content"] == test_message for m in messages)
    assert found, "Sent message not found in channel history"

@pytest.mark.asyncio
async def test_slack_add_reaction(slack_connector, execution_context):
    try:
        channels_res = await slack_connector.execute_action("list_channels", {}, execution_context)
    except Exception:
        pytest.skip("Skipping")
    
    if not channels_res.get("channels"):
        pytest.skip("No channels")

    channels = channels_res["channels"]
    target_channel = next((c for c in channels if c.get("is_member")), None)
    
    if not target_channel:
        target_channel = channels[0]

    channel_id = target_channel["id"]
    
    send_res = await slack_connector.execute_action(
        "send_message", 
        {"channel": channel_id, "text": "React to this!"}, 
        execution_context
    )
    
    msg_id = send_res["message_id"]
    
    react_res = await slack_connector.execute_action(
        "add_reaction", 
        {"channel": channel_id, "timestamp": msg_id, "name": "thumbsup"}, 
        execution_context
    )
    assert react_res.get("status") == "SUCCESS"
