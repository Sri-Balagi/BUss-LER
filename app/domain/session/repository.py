from abc import ABC, abstractmethod
from typing import Optional
from app.domain.session.models import Session

class ISessionRepository(ABC):
    @abstractmethod
    async def get_session(self, session_id: str, tenant_id: Optional[str] = None) -> Optional[Session]:
        pass

    @abstractmethod
    async def save_session(self, session: Session) -> None:
        pass
