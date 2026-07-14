from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field

from app.domain.common.biz_object import BizObject


class APIKeyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class APIKey(BizObject):
    """
    Represents an API Key used for Gateway authentication.
    Raw keys are never stored, only their cryptographically secure hash.
    """
    
    name: str = Field(..., description="A friendly name for the API Key (e.g., 'Production Gateway Key').")
    key_hash: str = Field(..., description="The cryptographic hash of the actual API Key.")
    prefix: str = Field(..., description="The first 8 characters of the raw key, used for UI identification.")
    
    status: APIKeyStatus = Field(default=APIKeyStatus.ACTIVE, description="Operational status of the key.")
    scopes: List[str] = Field(default_factory=list, description="List of RBAC scopes/permissions granted to this key.")
    
    expires_at: Optional[datetime] = Field(default=None, description="When the key automatically expires.")
    last_used_at: Optional[datetime] = Field(default=None, description="Timestamp of last usage.")
    
    def is_valid(self) -> bool:
        """Determines if the key is currently valid for authentication."""
        if self.status != APIKeyStatus.ACTIVE:
            return False
        
        # We need timezone-aware datetime comparison. BizObject uses UTC.
        if self.expires_at is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            if now > self.expires_at:
                return False
                
        return True
