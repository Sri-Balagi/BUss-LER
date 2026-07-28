from typing import Protocol, Any
from app.core.modules.ai.cognition import BusinessKnowledgeModel

class KnowledgePack(Protocol):
    """Protocol for a modular Knowledge Pack."""
    @classmethod
    def build(cls, module_name: str = "") -> Any:
        ...

class BaseReferenceProvider:
    """Base class for all Reference Providers that assembles Knowledge Packs."""
    
    ontology: type[Any] | None = None
    vocabulary: type[Any] | None = None
    objectives: type[Any] | None = None
    kpis: type[Any] | None = None
    processes: type[Any] | None = None
    constraints: type[Any] | None = None
    regulations: type[Any] | None = None
    personas: type[Any] | None = None
    decisions: type[Any] | None = None
    actions: type[Any] | None = None
    capability_definitions: type[Any] | None = None
    context_contributors: type[Any] | None = None
    policies: type[Any] | None = None
    state_transitions: type[Any] | None = None
    events: type[Any] | None = None
    temporal_patterns: type[Any] | None = None
    taxonomies: type[Any] | None = None

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module_id = f"bizos.modules.{module_name}.v1"

    def build(self) -> BusinessKnowledgeModel:
        model = BusinessKnowledgeModel(module_id=self.module_id)
        
        if self.ontology:
            model.ontology = self.ontology.build(self.module_name)
        if self.vocabulary:
            model.vocabulary = self.vocabulary.build(self.module_name)
        if self.objectives:
            model.objectives = self.objectives.build(self.module_name)
        if self.kpis:
            model.kpis = self.kpis.build(self.module_name)
        if self.processes:
            model.processes = self.processes.build(self.module_name)
        if self.constraints:
            model.constraints = self.constraints.build(self.module_name)
        if self.regulations:
            model.regulations = self.regulations.build(self.module_name)
        if self.personas:
            model.personas = self.personas.build(self.module_name)
        if self.decisions:
            model.decision_frameworks = self.decisions.build(self.module_name)
        if self.actions:
            model.action_definitions = self.actions.build(self.module_name)
        if self.capability_definitions:
            model.capability_definitions = self.capability_definitions.build(self.module_name)
        if self.context_contributors:
            model.context_contributors = self.context_contributors.build(self.module_name)
        if self.policies:
            model.policies = self.policies.build(self.module_name)
        if self.state_transitions:
            model.state_transitions = self.state_transitions.build(self.module_name)
        if self.events:
            model.events = self.events.build(self.module_name)
        if self.temporal_patterns:
            model.temporal_patterns = self.temporal_patterns.build(self.module_name)
        if self.taxonomies:
            model.taxonomies = self.taxonomies.build(self.module_name)
            
        return model
