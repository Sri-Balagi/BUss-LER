from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Dict, Any
from app.shared.enums import PrincipalType

class ExecutionContext(BaseModel):
    """
    The canonical execution object across BizOS.
    This context is immutable and encapsulates all request and tenant tracing.
    """
    model_config = ConfigDict(frozen=True)

    tenant_id: str
    principal_type: PrincipalType = PrincipalType.HUMAN
    principal_id: str
    session_id: str
    conversation_id: str
    trace_id: str
    correlation_id: str
    approval_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    application_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    memory_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @model_validator(mode='before')
    @classmethod
    def handle_legacy_user_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "user_id" in data and "principal_id" not in data:
                data["principal_id"] = data["user_id"]
                data["principal_type"] = PrincipalType.HUMAN
                # Do not delete user_id as pydantic might complain if it's passed but not expected
                # wait, if it's not a field, extra='ignore' handles it, but since config is frozen maybe it rejects extra?
                # Actually, pydantic BaseModel by default ignores extra unless extra='forbid' is used.
        return data

    @property
    def user_id(self) -> Optional[str]:
        """Backward compatibility for Wave 6/7 apps expecting user_id."""
        if self.principal_type == PrincipalType.HUMAN:
            return self.principal_id
        return None
