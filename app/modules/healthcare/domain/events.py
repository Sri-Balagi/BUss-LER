"""Healthcare Domain Events."""

from uuid import UUID

from app.shared.events.models import DomainEvent


class PatientAdmittedEvent(DomainEvent):
    """Event emitted when a patient is admitted to a hospital bed/ward."""

    patient_id: UUID
    bed_id: UUID
    ward_name: str
    tenant_id: str | None = None


class AppointmentBookedEvent(DomainEvent):
    """Event emitted when a doctor consultation is scheduled."""

    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    tenant_id: str | None = None


class LabResultDeliveredEvent(DomainEvent):
    """Event emitted when lab results are ready."""

    lab_order_id: UUID
    patient_id: UUID
    test_name: str
    tenant_id: str | None = None


class PrescriptionIssuedEvent(DomainEvent):
    """Event emitted when a doctor issues a prescription."""

    prescription_id: UUID
    patient_id: UUID
    doctor_id: UUID
    tenant_id: str | None = None
