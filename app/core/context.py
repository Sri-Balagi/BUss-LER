import uuid
from datetime import UTC, datetime

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel


class OperationContext(DomainBaseModel):
    """
    Encapsulates operational metadata passed across system layers.
    Enables distributed tracing, audit logging, and cleaner service signatures.
    """

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    twin_id: uuid.UUID | None = Field(default=None)
    user_id: uuid.UUID | None = Field(default=None)
    provider: str | None = Field(default=None)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def bind_to_logger(self, logger):
        """Returns a logger bound with this context."""
        return logger.bind(
            request_id=self.request_id,
            correlation_id=self.correlation_id,
            twin_id=str(self.twin_id) if self.twin_id else None,
            user_id=str(self.user_id) if self.user_id else None,
        )
