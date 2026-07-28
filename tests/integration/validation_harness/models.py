from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from app.domain.planning.models import Goal

@dataclass
class ValidationScenario:
    module_name: str
    scenario_id: str
    category: str
    description: str
    initial_business_context: Dict[str, Any]
    memory_seed: Dict[str, Any]
    digital_twin_seed: Dict[str, Any]
    input_request: Goal
    expected_outcome: str

@dataclass
class ValidationTrace:
    scenario_id: str = ""
    retrieval_results: Dict[str, Any] = field(default_factory=dict)
    planning_results: Dict[str, Any] = field(default_factory=dict)
    reasoning_results: Dict[str, Any] = field(default_factory=dict)
    workflow_results: Dict[str, Any] = field(default_factory=dict)
    memory_results: Dict[str, Any] = field(default_factory=dict)
    digital_twin_results: Dict[str, Any] = field(default_factory=dict)
    multi_agent_results: Dict[str, Any] = field(default_factory=dict)
    events: List[Any] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_duration: float = 0.0
    final_outcome: str = "Unknown"
