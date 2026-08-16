"""Healthcare Domain entities and value objects leveraging Shared Domain Kernel models."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.modules.kernel.kernel_models import Customer, Money


class TriageLevel(str, Enum):
    IMMEDIATE = "IMMEDIATE"    # Resuscitation (Red)
    EMERGENT = "EMERGENT"      # Emergency (Orange)
    URGENT = "URGENT"          # Urgent (Yellow)
    SEMI_URGENT = "SEMI_URGENT"# Less Urgent (Green)
    NON_URGENT = "NON_URGENT"  # Non Urgent (Blue)


class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CHECKED_IN = "CHECKED_IN"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class BedStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    CLEANING = "CLEANING"
    MAINTENANCE = "MAINTENANCE"


class DoctorProfile(BaseModel):
    """Healthcare provider or physician profile."""

    doctor_id: UUID = Field(default_factory=uuid4)
    name: str
    specialty: str
    license_number: str
    consultation_fee: Money
    is_active: bool = True


class PatientRecord(BaseModel):
    """Patient Electronic Health Record (EHR) aggregate root."""

    patient_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    demographic: Customer  # Reuses Shared Domain Kernel Customer model
    medical_record_number: str
    blood_type: str | None = None
    allergies: list[str] = Field(default_factory=list)
    chronic_conditions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Appointment(BaseModel):
    """Patient appointment entity."""

    appointment_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    patient_id: UUID
    doctor_id: UUID
    appointment_time: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason_for_visit: str
    consultation_fee: Money


class Prescription(BaseModel):
    """Medical prescription issued by a physician."""

    prescription_id: UUID = Field(default_factory=uuid4)
    patient_id: UUID
    doctor_id: UUID
    medications: list[dict[str, Any]] = Field(default_factory=list)  # [{"name": "Amoxicillin", "dosage": "500mg", "frequency": "TDS"}]
    issued_at: datetime = Field(default_factory=datetime.utcnow)


class BedWard(BaseModel):
    """Hospital bed unit within a ward."""

    bed_id: UUID = Field(default_factory=uuid4)
    ward_name: str
    bed_number: str
    status: BedStatus = BedStatus.AVAILABLE
    assigned_patient_id: UUID | None = None


class LabOrder(BaseModel):
    """Diagnostic laboratory test order."""

    lab_order_id: UUID = Field(default_factory=uuid4)
    patient_id: UUID
    test_name: str
    status: str = "ORDERED"  # ORDERED, SAMPLE_COLLECTED, PROCESSING, COMPLETED
    results: str | None = None
    ordered_at: datetime = Field(default_factory=datetime.utcnow)


class HospitalAnalytics(BaseModel):
    """Metric container for Hospital Bed Occupancy & Triage analysis."""

    total_beds: int
    occupied_beds: int
    occupancy_rate_percent: float
    target_occupancy_rate_percent: float = 85.0
    average_triage_wait_minutes: float = 12.0
    recommendation: str | None = None
