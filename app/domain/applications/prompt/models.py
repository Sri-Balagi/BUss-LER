from typing import Any

from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    """Template for prompt construction."""
    id: str = Field(..., description="Unique identifier for the template")
    system_instruction: str = Field(..., description="System instructions")
    variable_schema: dict[str, Any] = Field(default_factory=dict, description="Schema for required variables")
