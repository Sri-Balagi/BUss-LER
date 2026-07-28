"""Manifest definition for Healthcare & Hospital Business Module."""

from app.core.modules.models import (
    MarketplaceMetadata,
    ModuleCapabilities,
    ModuleCategory,
    ModuleManifest,
    ModuleType,
)

HEALTHCARE_MANIFEST = ModuleManifest(
    module_id="bizos.modules.healthcare.v1",
    name="Healthcare & Hospital Management",
    description="Enterprise Healthcare & Hospital Module for BizOS supporting Patient EHR, Appointments, Prescriptions, Bed Wards, Lab Orders, Triage, and AI Occupancy optimization.",
    version="1.0.0",
    module_type=ModuleType.VERTICAL,
    category=ModuleCategory.HEALTHCARE,
    author="BizOS Core Engineering Team",
    dependencies=[],
    required_connectors=["ehr_system", "lab_lims", "medical_billing"],
    supported_languages=["en", "es", "fr"],
    supported_regions=["US", "EU", "GLOBAL"],
    capabilities=ModuleCapabilities(
        domain_entities=["PatientRecord", "DoctorProfile", "Appointment", "Prescription", "BedWard", "LabOrder", "TriageRecord"],
        commands=["ScheduleAppointment", "CreatePatientRecord", "IssuePrescription", "AdmitPatientToBed"],
        queries=["GetPatientEHR", "GetAvailableBeds", "GetLabOrderResults"],
        events_published=["PatientAdmitted", "AppointmentBooked", "LabResultDelivered", "PrescriptionIssued"],
        events_subscribed=["PaymentReceived", "LabSampleCollected"],
        permissions=["healthcare:patient:read", "healthcare:patient:write", "healthcare:triage:manage"],
        ai_vocabularies=["Bed Occupancy Rate", "Triage Severity Index", "Average Length of Stay"],
        provided_contracts=["IHealthcareProvider"]
    ),
    marketplace=MarketplaceMetadata(
        publisher="BizOS Official",
        website="https://bizos.ai/modules/healthcare",
        support_email="healthcare-support@bizos.ai",
        license="Enterprise-Proprietary",
        min_bizos_version="1.0.0",
        price_model="subscription",
        tags=["healthcare", "hospital", "ehr", "patient", "medical", "clinic"]
    ),
    configuration_schema={
        "emergency_triage_alert_minutes": {"type": "integer", "default": 15},
        "auto_notify_patient_sms": {"type": "boolean", "default": True},
        "target_bed_occupancy_percent": {"type": "number", "default": 85.0}
    }
)
