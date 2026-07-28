"""Healthcare Application Services implementing hospital & clinical workflows."""

import logging
from datetime import datetime
from uuid import UUID

from app.core.modules.kernel.kernel_models import Money
from app.modules.healthcare.domain.events import (
    AppointmentBookedEvent,
    PatientAdmittedEvent,
    PrescriptionIssuedEvent,
)
from app.modules.healthcare.domain.models import (
    Appointment,
    BedStatus,
    BedWard,
    HospitalAnalytics,
    PatientRecord,
    Prescription,
)
from app.shared.events.bus import EventBus

logger = logging.getLogger(__name__)


class PatientEHRService:
    """Service managing Patient Electronic Health Records (EHR)."""

    def __init__(self) -> None:
        self._patients: dict[UUID, PatientRecord] = {}

    async def register_patient(self, record: PatientRecord) -> PatientRecord:
        """Register new patient record."""
        self._patients[record.patient_id] = record
        logger.info(f"Registered patient {record.patient_id} MRN={record.medical_record_number}")
        return record

    async def get_patient(self, patient_id: UUID) -> PatientRecord | None:
        """Retrieve patient EHR."""
        return self._patients.get(patient_id)


class AppointmentService:
    """Service scheduling doctor appointments and consultations."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._appointments: dict[UUID, Appointment] = {}
        self._event_bus = event_bus

    async def schedule_appointment(
        self,
        tenant_id: str,
        patient_id: UUID,
        doctor_id: UUID,
        appointment_time: datetime,
        reason: str,
        fee_amount: Money
    ) -> Appointment:
        """Schedule a doctor consultation."""
        app = Appointment(
            tenant_id=tenant_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_time=appointment_time,
            reason_for_visit=reason,
            consultation_fee=fee_amount
        )
        self._appointments[app.appointment_id] = app
        logger.info(f"Scheduled appointment {app.appointment_id} for patient {patient_id}")

        if self._event_bus:
            self._event_bus.publish(
                AppointmentBookedEvent(
                    correlation_id=str(app.appointment_id),
                    appointment_id=app.appointment_id,
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    tenant_id=tenant_id
                )
            )

        return app


class WardBedService:
    """Service managing hospital bed occupancy and patient admissions."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._beds: dict[UUID, BedWard] = {}
        self._event_bus = event_bus

    async def add_bed(self, bed: BedWard) -> None:
        """Add bed unit to ward."""
        self._beds[bed.bed_id] = bed

    async def admit_patient(self, bed_id: UUID, patient_id: UUID, tenant_id: str = "default") -> BedWard:
        """Admit patient to an available ward bed."""
        bed = self._beds.get(bed_id)
        if not bed:
            raise ValueError(f"Bed {bed_id} not found")
        if bed.status != BedStatus.AVAILABLE:
            raise ValueError(f"Bed {bed_id} is not available (current status={bed.status})")

        bed.status = BedStatus.OCCUPIED
        bed.assigned_patient_id = patient_id
        logger.info(f"Admitted patient {patient_id} to bed {bed.bed_number} ({bed.ward_name})")

        if self._event_bus:
            self._event_bus.publish(
                PatientAdmittedEvent(
                    correlation_id=str(patient_id),
                    patient_id=patient_id,
                    bed_id=bed_id,
                    ward_name=bed.ward_name,
                    tenant_id=tenant_id
                )
            )

        return bed


class PrescriptionService:
    """Service issuing and fulfilling medical prescriptions."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._prescriptions: dict[UUID, Prescription] = {}
        self._event_bus = event_bus

    async def issue_prescription(self, prescription: Prescription, tenant_id: str = "default") -> Prescription:
        """Issue new prescription."""
        self._prescriptions[prescription.prescription_id] = prescription
        logger.info(f"Issued prescription {prescription.prescription_id} for patient {prescription.patient_id}")

        if self._event_bus:
            self._event_bus.publish(
                PrescriptionIssuedEvent(
                    correlation_id=str(prescription.prescription_id),
                    prescription_id=prescription.prescription_id,
                    patient_id=prescription.patient_id,
                    doctor_id=prescription.doctor_id,
                    tenant_id=tenant_id
                )
            )

        return prescription


class HospitalAnalyticsService:
    """Service computing Bed Occupancy Rate and Triage metrics."""

    @staticmethod
    def calculate_bed_occupancy(total_beds: int, occupied_beds: int, target_occupancy: float = 85.0) -> HospitalAnalytics:
        """Calculate hospital bed occupancy percentage and generate AI recommendations."""
        rate = (occupied_beds / total_beds * 100.0) if total_beds > 0 else 0.0
        rec = None
        if rate > target_occupancy:
            rec = f"Bed occupancy rate ({rate:.1f}%) exceeds safety threshold ({target_occupancy:.1f}%). Recommend expediting discharge planning or opening overflow ward."

        return HospitalAnalytics(
            total_beds=total_beds,
            occupied_beds=occupied_beds,
            occupancy_rate_percent=round(rate, 2),
            target_occupancy_rate_percent=target_occupancy,
            recommendation=rec
        )
