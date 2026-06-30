from enum import Enum

from pydantic import BaseModel


class KPIStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    MISSING = "MISSING"

class KPIAssessment(BaseModel):
    """Structured assessment of a specific business KPI."""
    kpi_id: str
    current_value: float
    target_value: float
    status: KPIStatus
    deviation_percentage: float
