from typing import List, Optional
from pydantic import BaseModel, Field

class ResearchResult(BaseModel):
    findings: str = Field(..., description="The main body of the research findings.")
    sources: List[str] = Field(default_factory=list, description="List of sources consulted.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the research completeness.")

class ReasoningResult(BaseModel):
    observations: List[str] = Field(..., description="Key observations from the data.")
    assumptions: List[str] = Field(..., description="Assumptions made during reasoning.")
    recommendations: List[str] = Field(..., description="Actionable recommendations.")
    risks: List[str] = Field(..., description="Identified risks.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score.")

class PlannerResult(BaseModel):
    plan_steps: List[str] = Field(..., description="List of agent capabilities to invoke in order.")
    objective_summary: str = Field(..., description="A short summary of the understood goal.")
