from abc import ABC, abstractmethod

from app.domain.session.models import Session


class ISessionRepository(ABC):
    @abstractmethod
    async def get_session(self, session_id: str, tenant_id: str | None = None) -> Session | None:
        pass

    @abstractmethod
    async def save_session(self, session: Session) -> None:
        pass
