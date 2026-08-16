"""Unit tests for Healthcare & Hospital Business Module."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.modules.kernel.kernel_models import Customer, Money
from app.core.modules.manager import ModuleManager
from app.core.modules.models import ModuleContext
from app.core.modules.registry import ModuleRegistry
from app.modules.healthcare.domain.models import BedStatus, BedWard, PatientRecord, Prescription
from app.modules.healthcare.module import HealthcareModule


@pytest.mark.asyncio
async def test_healthcare_module_full_lifecycle():
    module = HealthcareModule()
    registry = ModuleRegistry()
    manager = ModuleManager(registry=registry)
    ctx = ModuleContext(tenant_id="hospital_tenant_01")

    # Install & Initialize
    assert await manager.install_module(module, ctx) is True
    assert await manager.initialize_module(module.manifest.module_id, ctx) is True
    assert await manager.enable_module(module.manifest.module_id, ctx) is True

    # Test Patient Registration
    patient_id = uuid4()
    customer_profile = Customer(
        customer_id=patient_id,
        tenant_id="hospital_tenant_01",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    patient_record = PatientRecord(
        patient_id=patient_id,
        tenant_id="hospital_tenant_01",
        demographic=customer_profile,
        medical_record_number="MRN-2026-9901",
        blood_type="O+",
        allergies=["Penicillin"]
    )
    registered = await module.patient_service.register_patient(patient_record)
    assert registered.medical_record_number == "MRN-2026-9901"

    retrieved = await module.patient_service.get_patient(patient_id)
    assert retrieved is not None
    assert retrieved.demographic.first_name == "John"

    # Test Doctor Appointment Scheduling
    doctor_id = uuid4()
    app = await module.appointment_service.schedule_appointment(
        tenant_id="hospital_tenant_01",
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_time=datetime.utcnow(),
        reason="Annual Cardiology Checkup",
        fee_amount=Money(amount=Decimal("150.00"))
    )
    assert app.consultation_fee.amount == Decimal("150.00")

    # Test Ward Bed Admission
    bed_id = uuid4()
    bed = BedWard(bed_id=bed_id, ward_name="ICU Unit 1", bed_number="BED-102", status=BedStatus.AVAILABLE)
    await module.bed_service.add_bed(bed)

    admitted_bed = await module.bed_service.admit_patient(bed_id, patient_id, tenant_id="hospital_tenant_01")
    assert admitted_bed.status == BedStatus.OCCUPIED
    assert admitted_bed.assigned_patient_id == patient_id

    # Test Prescription Issuing
    prescription = Prescription(
        patient_id=patient_id,
        doctor_id=doctor_id,
        medications=[{"name": "Lisinopril", "dosage": "10mg", "frequency": "OD"}]
    )
    issued = await module.prescription_service.issue_prescription(prescription)
    assert issued.patient_id == patient_id

    # Test Bed Occupancy Analytics
    analytics = module.analytics_service.calculate_bed_occupancy(total_beds=100, occupied_beds=90, target_occupancy=85.0)
    assert analytics.occupancy_rate_percent == 90.0
    assert "Bed occupancy rate (90.0%) exceeds safety threshold" in analytics.recommendation

    # Verify Declarative Business Knowledge Model (Subsystem 1)
    km = module.get_knowledge_model()
    assert km is not None
    assert len(km.vocabulary.terms) >= 2
    assert len(km.decision_frameworks) >= 1

    # Verify AI Knowledge Pack (Backward Compatibility)
    ai_pack = module.get_ai_knowledge_pack()
    assert len(ai_pack.vocabularies) >= 2


    # Verify Extension Points & Capabilities
    assert len(module.get_extension_points()) >= 1
    assert len(module.get_capabilities()) >= 2
    assert len(module.get_ui_navigation()) >= 3
