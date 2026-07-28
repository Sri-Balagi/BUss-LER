"""BizOS Cognitive Operating System Architecture Core SDK.

Enforces strict separation of static domain cognition (BusinessKnowledgeModel)
from runtime state (BusinessWorldModel), memory systems, reasoning engines,
planning engines, decision evaluation, execution guardrails, explainability traces,
and model-agnostic LLM adapters.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.agents.models import AgentTemplate
from app.shared.enums import AgentCapability

# ============================================================================
# SUBSYSTEM 1 — BUSINESS MODULE SDK (STATIC DECLARATIVE DOMAIN COGNITION)
# ============================================================================

class KnowledgeArtifact(BaseModel):
    """Universal base meta-model for all top-level declarative business knowledge."""
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    
    # Provenance
    source: str | None = None
    authority: str | None = None
    evidence: list[str] = Field(default_factory=list)
    external_references: list[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    knowledge_confidence: float = 1.0
    
    # Universal Extensibility
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    version: str = "1.0"


class DomainEntitySpec(KnowledgeArtifact):
    """Declarative specification of a domain entity."""
    attributes: list[str] = Field(default_factory=list)
    is_aggregate_root: bool = False


class KnowledgeRelationship(BaseModel):
    """Value Object representing a structural semantic edge between artifacts."""
    source_id: str
    target_id: str
    relationship_type: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DomainOntology(BaseModel):
    """Declarative domain ontology specification taught by a business module."""
    entities: list[DomainEntitySpec] = Field(default_factory=list)
    relationships: list[KnowledgeRelationship] = Field(default_factory=list)
    aggregates: list[str] = Field(default_factory=list)


class SemanticTerm(KnowledgeArtifact):
    """Domain terminology definition taught by a module."""
    formula: str | None = None


class SemanticVocabulary(BaseModel):
    """Declarative vocabulary package."""
    terms: list[SemanticTerm] = Field(default_factory=list)


class BusinessObjective(KnowledgeArtifact):
    """Domain business objective and success criteria."""
    target_metrics: list[str] = Field(default_factory=list)
    priority_weight: float = 1.0


class KPIDefinition(KnowledgeArtifact):
    """Declarative KPI definition detailing meaning and business interpretation."""
    formula: str
    unit_of_measure: str | None = None


class ProcessStage(BaseModel):
    """Value Object representing a stage in a business process workflow."""
    stage_id: str
    name: str
    description: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)


class BusinessProcess(KnowledgeArtifact):
    """Declarative workflow process specification."""
    stages: list[ProcessStage] = Field(default_factory=list)


class DomainConstraint(KnowledgeArtifact):
    """Immutable domain constraint or operational guardrail."""
    constraint_category: str
    rule_description: str


class Regulation(KnowledgeArtifact):
    """Regulatory or industry compliance specification."""
    requirements: list[str] = Field(default_factory=list)
    compliance_scope: str


class AIPersona(KnowledgeArtifact):
    """Expert executive perspective taught by a module."""
    perspective_description: str
    core_priorities: list[str] = Field(default_factory=list)


class DecisionFactor(BaseModel):
    """Value Object representing an evaluative factor in decision making."""
    factor_name: str
    importance_weight: float = 1.0
    evaluation_criteria: str


class DecisionFramework(KnowledgeArtifact):
    """Multi-variable evaluation framework taught by a module."""
    decision_goal: str
    factors: list[DecisionFactor] = Field(default_factory=list)
    trade_off_considerations: list[str] = Field(default_factory=list)


class ActionDefinition(KnowledgeArtifact):
    """Executable domain action specification."""
    preconditions: list[str] = Field(default_factory=list)
    required_permissions: list[str] = Field(default_factory=list)
    expected_effects: list[str] = Field(default_factory=list)
    potential_side_effects: list[str] = Field(default_factory=list)
    rollback_strategy: str | None = None
    risk_category: str | None = None
    risk_weight: float = 1.0


class CapabilityDefinition(KnowledgeArtifact):
    """Machine-readable capability graph node declaration."""
    category: str
    dependent_capabilities: list[str] = Field(default_factory=list)


class ContextContributorSpec(BaseModel):
    """Value Object representing specification of dynamic context contributed by a module."""
    contributor_id: str
    name: str
    provided_context_keys: list[str] = Field(default_factory=list)


class BusinessPolicy(KnowledgeArtifact):
    """Declarative business policy."""
    governance_scope: str
    policy_statements: list[str] = Field(default_factory=list)


class StateTransitionModel(KnowledgeArtifact):
    """Declarative generic lifecycle transitions."""
    entity_reference: str
    from_state: str
    to_state: str
    trigger_events: list[str] = Field(default_factory=list)


class DomainEvent(KnowledgeArtifact):
    """Declarative event structure definition."""
    payload_schema_keys: list[str] = Field(default_factory=list)


class TemporalPattern(KnowledgeArtifact):
    """Declarative representation of seasonality or operational time horizons."""
    pattern_schedule: str
    impact_description: str


class ClassificationTaxonomy(KnowledgeArtifact):
    """Generic hierarchical taxonomy defined by the module."""
    category_tree: dict[str, Any] = Field(default_factory=dict)


class BusinessKnowledgeModel(BaseModel):
    """Top-level static, immutable Business Knowledge Model exposed by a Business Module."""
    module_id: str
    ontology: DomainOntology = Field(default_factory=DomainOntology)
    vocabulary: SemanticVocabulary = Field(default_factory=SemanticVocabulary)
    objectives: list[BusinessObjective] = Field(default_factory=list)
    kpis: list[KPIDefinition] = Field(default_factory=list)
    processes: list[BusinessProcess] = Field(default_factory=list)
    constraints: list[DomainConstraint] = Field(default_factory=list)
    regulations: list[Regulation] = Field(default_factory=list)
    personas: list[AIPersona] = Field(default_factory=list)
    decision_frameworks: list[DecisionFramework] = Field(default_factory=list)
    action_definitions: list[ActionDefinition] = Field(default_factory=list)
    capability_definitions: list[CapabilityDefinition] = Field(default_factory=list)
    context_contributors: list[ContextContributorSpec] = Field(default_factory=list)
    policies: list[BusinessPolicy] = Field(default_factory=list)
    state_transitions: list[StateTransitionModel] = Field(default_factory=list)
    events: list[DomainEvent] = Field(default_factory=list)
    temporal_patterns: list[TemporalPattern] = Field(default_factory=list)
    taxonomies: list[ClassificationTaxonomy] = Field(default_factory=list)
    agent_templates: list[AgentTemplate] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# SUBSYSTEM 2 — COGNITIVE RUNTIME ENGINE (STATE, REASONING, EXPLAINABILITY)
# ============================================================================

class BusinessWorldModel(BaseModel):
    """Subsystem 2.1 — Dynamic runtime business state graph populated by platform telemetry."""
    tenant_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_entities: dict[str, Any] = Field(default_factory=dict)
    active_workflows: list[str] = Field(default_factory=list)
    current_kpi_values: dict[str, float] = Field(default_factory=dict)
    active_threats_and_risks: list[str] = Field(default_factory=list)


class MemoryEntry(BaseModel):
    """Episodic or semantic memory item stored in MemorySystem."""
    entry_id: UUID = Field(default_factory=uuid4)
    memory_type: str
    content: str
    relevance_score: float = 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemorySystem(BaseModel):
    """Subsystem 2.1 — Runtime memory store for long-term and working memory."""
    tenant_id: str
    memories: list[MemoryEntry] = Field(default_factory=list)

    def add_memory(self, content: str, memory_type: str = "EPISODIC") -> MemoryEntry:
        entry = MemoryEntry(content=content, memory_type=memory_type)
        self.memories.append(entry)
        return entry


class CognitiveContext(BaseModel):
    """Subsystem 2.2 — Structured operational context object generated by ContextAssemblyEngine."""
    tenant_id: str
    task_goal: str
    active_persona: AIPersona | None = None
    assembled_knowledge: list[BusinessKnowledgeModel] = Field(default_factory=list)
    world_state: BusinessWorldModel | None = None
    relevant_memories: list[MemoryEntry] = Field(default_factory=list)
    assembled_context_data: dict[str, Any] = Field(default_factory=dict)


class ReasoningResult(BaseModel):
    """Subsystem 2.3 — Outcome of Cognition & Reasoning Engine evaluation."""
    reasoning_type: str
    findings: list[str] = Field(default_factory=list)
    causal_chain: list[str] = Field(default_factory=list)
    confidence_score: float = 0.95


class PlanStep(BaseModel):
    """Step in an autonomous execution plan."""
    step_id: int
    action_id: str
    description: str
    preconditions: list[str] = Field(default_factory=list)
    rollback_action: str | None = None


class ExecutionPlan(BaseModel):
    """Subsystem 2.4 — Generated multi-step execution plan."""
    goal: str
    steps: list[PlanStep] = Field(default_factory=list)
    estimated_risk: str = "LOW"


class ExplainabilityTrace(BaseModel):
    """Subsystem 2.5 — Full audit trace explaining AI decisions for compliance."""
    trace_id: UUID = Field(default_factory=uuid4)
    decision_title: str
    evidence_references: list[str] = Field(default_factory=list)
    reasoning_steps: list[str] = Field(default_factory=list)
    assumptions_made: list[str] = Field(default_factory=list)
    confidence_level: float = 0.95
    evaluated_trade_offs: list[str] = Field(default_factory=list)
    applied_regulations: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SUBSYSTEM 3 — MODEL ADAPTER LAYER (MODEL-AGNOSTIC LLM TRANSLATION)
# ============================================================================

class BaseModelAdapter(ABC):
    """Subsystem 3 — Model-agnostic API adapter interface for LLMs and reasoning backends."""

    @abstractmethod
    def render_model_payload(self, context: CognitiveContext) -> dict[str, Any]:
        """Translate structured CognitiveContext into model-native API payloads."""
        pass


class GPTAdapter(BaseModelAdapter):
    """Adapter for OpenAI GPT-4 / GPT-5 Structured Outputs and Function Calling."""

    def render_model_payload(self, context: CognitiveContext) -> dict[str, Any]:
        persona_str = context.active_persona.name if context.active_persona else "Business AI Advisor"
        return {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": f"You are acting as {persona_str}. Perform task: {context.task_goal}"},
                {"role": "user", "content": f"Structured Context Data: {context.assembled_context_data}"}
            ],
            "temperature": 0.2
        }


class ClaudeAdapter(BaseModelAdapter):
    """Adapter for Anthropic Claude Tool Use API."""

    def render_model_payload(self, context: CognitiveContext) -> dict[str, Any]:
        return {
            "model": "claude-3-5-sonnet",
            "system": f"Role: {context.active_persona.name if context.active_persona else 'Advisor'}",
            "messages": [{"role": "user", "content": f"Goal: {context.task_goal}"}]
        }


class GeminiAdapter(BaseModelAdapter):
    """Adapter for Google Gemini API."""

    def render_model_payload(self, context: CognitiveContext) -> dict[str, Any]:
        return {
            "model": "gemini-1.5-pro",
            "contents": [{"role": "user", "parts": [{"text": f"Task: {context.task_goal}"}]}]
        }


class LocalModelAdapter(BaseModelAdapter):
    """Adapter for local open-weights LLMs via vLLM / Ollama."""

    def render_model_payload(self, context: CognitiveContext) -> dict[str, Any]:
        return {
            "model": "llama-3-70b-instruct",
            "prompt": f"Task: {context.task_goal}"
        }
