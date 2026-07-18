from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from enum import Enum
from typing import Optional, List, Dict, Any

from app.shared.enums import PrincipalType, ParticipantRole
class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

class SessionParticipant(BaseModel):
    """A participant (Human, Agent, System) in a session."""
    id: str
    type: PrincipalType
    role: ParticipantRole = ParticipantRole.CONTRIBUTOR
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Session(BaseModel):
    """
    Session abstraction to hold user interactions.
    May eventually contain multiple conversations and multiple agents.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    participants: List[SessionParticipant] = Field(default_factory=list)
    conversation_ids: List[str] = Field(default_factory=list)  # Future-proofing for multiple conversations
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode='before')
    @classmethod
    def handle_legacy_user_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "user_id" in data and "participants" not in data:
                data["participants"] = [
                    SessionParticipant(
                        id=data["user_id"],
                        type=PrincipalType.HUMAN,
                        role=ParticipantRole.OWNER
                    )
                ]
        return data

    @property
    def user_id(self) -> Optional[str]:
        """Backward compatibility for Wave 6/7 apps expecting user_id."""
        for p in self.participants:
            if p.type == PrincipalType.HUMAN:
                return p.id
        return None

    def add_conversation(self, conversation_id: str):
        if conversation_id not in self.conversation_ids:
            self.conversation_ids.append(conversation_id)

    def close(self):
        self.status = SessionStatus.CLOSED
