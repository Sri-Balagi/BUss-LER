from enum import Enum
from typing import Optional

from pydantic import Field

from app.domain.common.biz_object import BizObject


class TenantStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class TenantTier(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class Tenant(BizObject):
    """
    Represents an isolated organizational boundary in BizOS.
    All data, workflows, and configurations belong to a Tenant.
    """
    
    name: str = Field(..., description="The name of the tenant or organization.")
    status: TenantStatus = Field(default=TenantStatus.ACTIVE, description="Current operational status.")
    tier: TenantTier = Field(default=TenantTier.FREE, description="Billing and feature tier.")
    
    contact_email: Optional[str] = Field(default=None, description="Primary contact email for the tenant.")
    
    # Override tenant_id from BizObject since a Tenant IS the tenant.
    @property
    def tenant_uuid(self):
        return self.id
