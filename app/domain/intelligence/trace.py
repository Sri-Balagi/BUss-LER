from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.modules.ai.cognition import BusinessPolicy, DomainConstraint, BusinessProcess


class CognitiveTrace(BaseModel):
    """
    Dedicated execution trace structure that accumulates evaluation telemetry during the runtime pipeline.
    Maintains the purity of the Plan artifact by capturing the 'why' and 'how' separately.
    """
    trace_id: UUID = Field(default_factory=uuid4)
    evaluated_policies: list[BusinessPolicy] = Field(default_factory=list)
    evaluated_constraints: list[DomainConstraint] = Field(default_factory=list)
    evaluated_processes: list[BusinessProcess] = Field(default_factory=list)

    def record_policy(self, policy: BusinessPolicy) -> None:
        if policy not in self.evaluated_policies:
            self.evaluated_policies.append(policy)

    def record_constraint(self, constraint: DomainConstraint) -> None:
        if constraint not in self.evaluated_constraints:
            self.evaluated_constraints.append(constraint)

    def record_process(self, process: BusinessProcess) -> None:
        if process not in self.evaluated_processes:
            self.evaluated_processes.append(process)
