from app.core.modules.ai.cognition import BusinessProcess, ProcessStage

class ProcessesPack:
    @classmethod
    def build(cls, module_name: str) -> list[BusinessProcess, ProcessStage]:
        return [

            BusinessProcess(
                artifact_id="proc_main",
                name="Assembly Line Production Run",
                description="End-to-end workflow for manufacturing.",
                stages=[
                    ProcessStage(stage_id="stage_1", name="Initiation", description="Start process", inputs=[], outputs=[]),
                    ProcessStage(stage_id="stage_2", name="Execution", description="Perform core logic", inputs=[], outputs=[]),
                    ProcessStage(stage_id="stage_3", name="Completion", description="Finalize and audit", inputs=[], outputs=[])
                ]
            )
    
        ]
