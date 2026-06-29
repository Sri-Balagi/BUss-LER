import uuid
from datetime import datetime, timezone

from app.interfaces.http.schemas.conversation import ConversationThread, ConversationTurn
from app.shared.enums import ConversationRole, ConversationStatus


def test_conversation_thread_validation():
    twin_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    thread = ConversationThread(
        id=thread_id,
        twin_id=twin_id,
        title="Strategy Session",
        created_at=now,
        updated_at=now,
    )

    assert thread.status == ConversationStatus.ACTIVE
    assert thread.twin_id == twin_id
    assert thread.title == "Strategy Session"


def test_conversation_turn_validation():
    thread_id = uuid.uuid4()
    turn_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    turn = ConversationTurn(
        id=turn_id,
        thread_id=thread_id,
        turn_index=0,
        role=ConversationRole.USER,
        content="What is my strategic goal?",
        created_at=now,
    )

    assert turn.thread_id == thread_id
    assert turn.role == ConversationRole.USER
    assert turn.content == "What is my strategic goal?"
