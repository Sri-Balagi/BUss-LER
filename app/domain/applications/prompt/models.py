from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PromptTemplate(BaseModel):
    """Template for prompt construction."""
    id: str = Field(..., description="Unique identifier for the template")
    system_instruction: str = Field(..., description="System instructions")
    variable_schema: Dict[str, Any] = Field(default_factory=dict, description="Schema for required variables")
