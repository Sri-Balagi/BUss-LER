
from app.domain.session.models import Session
from app.domain.session.repository import ISessionRepository


class InMemorySessionRepository(ISessionRepository):
    """In-memory implementation of ISessionRepository for development."""
    def __init__(self):
        self._sessions: dict[str, Session] = {}

    async def get_session(self, session_id: str, tenant_id: str | None = None) -> Session | None:
        session = self._sessions.get(session_id)
        if session and tenant_id and session.tenant_id != tenant_id:
            return None
        return session

    async def save_session(self, session: Session) -> None:
        self._sessions[session.session_id] = session
