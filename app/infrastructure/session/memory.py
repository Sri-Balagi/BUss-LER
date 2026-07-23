from typing import Optional, Dict
from app.domain.session.repository import ISessionRepository
from app.domain.session.models import Session

class InMemorySessionRepository(ISessionRepository):
    """In-memory implementation of ISessionRepository for development."""
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    async def get_session(self, session_id: str, tenant_id: Optional[str] = None) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session and tenant_id and session.tenant_id != tenant_id:
            return None
        return session

    async def save_session(self, session: Session) -> None:
        self._sessions[session.session_id] = session
