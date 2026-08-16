from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    findings: str = Field(..., description="The main body of the research findings.")
    sources: list[str] = Field(default_factory=list, description="List of sources consulted.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the research completeness.")

class ReasoningResult(BaseModel):
    observations: list[str] = Field(..., description="Key observations from the data.")
    assumptions: list[str] = Field(..., description="Assumptions made during reasoning.")
    recommendations: list[str] = Field(..., description="Actionable recommendations.")
    risks: list[str] = Field(..., description="Identified risks.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score.")

class PlannerResult(BaseModel):
    plan_steps: list[str] = Field(..., description="List of agent capabilities to invoke in order.")
    objective_summary: str = Field(..., description="A short summary of the understood goal.")

class PlannerCandidatePlans(BaseModel):
    candidates: list[PlannerResult] = Field(..., description="List of candidate plans.")
