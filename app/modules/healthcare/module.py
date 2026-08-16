"""Healthcare & Hospital Business Module implementation extending VerticalModule."""

from app.core.modules.ai.cognition import BusinessKnowledgeModel
from app.core.modules.ai.knowledge import ModuleKnowledgePack
from app.core.modules.base import VerticalModule
from app.core.modules.discovery.discovery import ModuleCapabilityDescriptor
from app.core.modules.extension_points.extension_points import ModuleExtensionPoint
from app.core.modules.models import ModuleContext
from app.core.modules.services.ui_metadata import UINavigationItem
from app.modules.healthcare.ai.cognition import HEALTHCARE_KNOWLEDGE_MODEL
from app.modules.healthcare.ai.knowledge import HEALTHCARE_KNOWLEDGE_PACK
from app.modules.healthcare.application.services import (
    AppointmentService,
    HospitalAnalyticsService,
    PatientEHRService,
    PrescriptionService,
    WardBedService,
)
from app.modules.healthcare.manifest import HEALTHCARE_MANIFEST


class HealthcareModule(VerticalModule):
    """Canonical Healthcare & Hospital Business Module for BizOS Ecosystem."""

    def __init__(self) -> None:
        super().__init__(HEALTHCARE_MANIFEST)
        self.patient_service = PatientEHRService()
        self.appointment_service = AppointmentService()
        self.bed_service = WardBedService()
        self.prescription_service = PrescriptionService()
        self.analytics_service = HospitalAnalyticsService()

    async def initialize(self, context: ModuleContext) -> bool:
        """Initialize healthcare services, platform capabilities, extension points, and UI metadata."""
        await super().initialize(context)
        return True

    def get_knowledge_model(self) -> BusinessKnowledgeModel:
        """Expose Subsystem 1 BusinessKnowledgeModel declaration."""
        return HEALTHCARE_KNOWLEDGE_MODEL

    def get_ai_knowledge_pack(self) -> ModuleKnowledgePack:
        """Expose legacy AI knowledge pack for backward compatibility."""
        return HEALTHCARE_KNOWLEDGE_PACK


    def get_extension_points(self) -> list[ModuleExtensionPoint]:
        """Expose extension points for third-party modules to extend healthcare functionality."""
        return [
            ModuleExtensionPoint(
                point_id="bizos.modules.healthcare.patient_admission_hook",
                module_id=self.manifest.module_id,
                name="Patient Admission Interceptor Hook",
                description="Allows insurance, billing, or triage modules to enrich patient admissions."
            )
        ]

    def get_capabilities(self) -> list[ModuleCapabilityDescriptor]:
        """Expose runtime capability descriptors for AI agents."""
        return [
            ModuleCapabilityDescriptor(
                capability_id="healthcare_patient_ehr",
                module_id=self.manifest.module_id,
                name="Patient Electronic Health Record (EHR)",
                description="Registers and retrieves patient EHR and medical history.",
                category="healthcare"
            ),
            ModuleCapabilityDescriptor(
                capability_id="healthcare_bed_occupancy_analysis",
                module_id=self.manifest.module_id,
                name="Hospital Bed Occupancy & Capacity Analytics",
                description="Calculates ward bed occupancy rate and emergency capacity recommendations.",
                category="analytics"
            )
        ]

    def get_ui_navigation(self) -> list[UINavigationItem]:
        """Expose declarative UI navigation menu items."""
        return [
            UINavigationItem(item_id="health_patients", label="Patient EHR Records", icon="users", route="/healthcare/patients", order=1),
            UINavigationItem(item_id="health_appointments", label="Doctor Consultations", icon="calendar", route="/healthcare/appointments", order=2),
            UINavigationItem(item_id="health_beds", label="Ward Bed Management", icon="activity", route="/healthcare/beds", order=3)
        ]
