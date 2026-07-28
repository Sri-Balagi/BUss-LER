from app.core.modules.ai.cognition import BusinessProcess, ProcessStage

class ProcessesPack:
    @classmethod
    def build(cls, module_name: str) -> list[BusinessProcess]:
        return [
            BusinessProcess(
                artifact_id="proc_patient_triage",
                name="Emergency Department Patient Triage",
                description="Standard workflow for admitting and triaging a new emergency patient.",
                stages=[
                    ProcessStage(
                        stage_id="stage_registration",
                        name="Patient Registration",
                        description="Collect patient demographics and initial chief complaint.",
                        inputs=["Raw Patient Details"],
                        outputs=["ent_patient"]
                    ),
                    ProcessStage(
                        stage_id="stage_clinical_triage",
                        name="Clinical Triage Assessment",
                        description="Nurse evaluates vitals and assigns a priority level.",
                        inputs=["ent_patient", "Chief Complaint"],
                        outputs=["Triage Priority Score", "ent_medical_record"]
                    ),
                    ProcessStage(
                        stage_id="stage_bed_assignment",
                        name="Bed Assignment",
                        description="Assign a physical bed based on triage priority and availability.",
                        inputs=["Triage Priority Score", "ent_patient"],
                        outputs=["ent_hospital_bed"]
                    )
                ]
            )
        ]
