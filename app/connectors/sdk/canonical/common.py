from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CanonicalUser(BaseModel):
    """Normalized user/principal object across all providers."""
    user_id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_provider_id: str = "system"


class CanonicalPage(BaseModel):
    """Generic paginated result wrapper."""
    items: List[Any]
    next_page_token: Optional[str] = None
    total_count: Optional[int] = None
    has_more: bool = False


class AssociationType(str, Enum):
    CONTACT_TO_COMPANY = "CONTACT_TO_COMPANY"
    DEAL_TO_COMPANY = "DEAL_TO_COMPANY"
    DEAL_TO_CONTACT = "DEAL_TO_CONTACT"
    DEAL_TO_PRODUCT = "DEAL_TO_PRODUCT"
    NOTE_TO_CONTACT = "NOTE_TO_CONTACT"
    NOTE_TO_DEAL = "NOTE_TO_DEAL"
    TASK_TO_CONTACT = "TASK_TO_CONTACT"
    TASK_TO_DEAL = "TASK_TO_DEAL"
    GENERIC = "GENERIC"


class CanonicalAssociation(BaseModel):
    """Provider-agnostic relationship binding between any two business entities."""
    association_id: str
    provider: str
    from_resource_type: str                      # "contact", "deal", "note", "task"
    from_resource_id: str
    to_resource_type: str                        # "company", "contact", "product"
    to_resource_id: str
    association_type: AssociationType = AssociationType.GENERIC
    metadata: Dict[str, Any] = Field(default_factory=dict)
