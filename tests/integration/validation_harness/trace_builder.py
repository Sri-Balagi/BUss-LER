from typing import Any
from .models import ValidationTrace

class ValidationTraceBuilder:
    def __init__(self, scenario_id: str):
        self.trace = ValidationTrace(scenario_id=scenario_id)
        
    def capture_event(self, event: Any):
        self.trace.events.append(event)
        
    def set_error(self, error: str):
        self.trace.errors.append(error)
        self.trace.final_outcome = "Failed"
        
    def finalize(self, duration: float) -> ValidationTrace:
        self.trace.execution_duration = duration
        if not self.trace.errors and self.trace.final_outcome == "Unknown":
            self.trace.final_outcome = "Completed"
        return self.trace
