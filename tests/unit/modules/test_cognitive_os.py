"""Unit tests for BizOS Cognitive Operating System Architecture Core & Subsystems."""

import pytest

from app.core.modules.ai.cognition import (
    BusinessWorldModel,
    ClaudeAdapter,
    CognitiveContext,
    ExplainabilityTrace,
    GeminiAdapter,
    GPTAdapter,
    LocalModelAdapter,
    MemorySystem,
)
from app.modules.accounting.module import AccountingModule
from app.modules.crm.module import CRMModule
from app.modules.healthcare.module import HealthcareModule
from app.modules.inventory.module import InventoryModule
from app.modules.restaurant.module import RestaurantModule


def test_business_knowledge_models_across_all_modules():
    """Verify Subsystem 1 static BusinessKnowledgeModel declarations across all 5 reference modules."""
    restaurant = RestaurantModule()
    healthcare = HealthcareModule()
    crm = CRMModule()
    accounting = AccountingModule()
    inventory = InventoryModule()

    modules = [restaurant, healthcare, crm, accounting, inventory]

    for mod in modules:
        model = mod.get_knowledge_model()
        assert model is not None
        assert model.module_id == mod.manifest.module_id
        assert len(model.ontology.entities) >= 3
        assert len(model.vocabulary.terms) >= 2
        assert len(model.objectives) >= 2
        assert len(model.kpis) >= 1
        assert len(model.regulations) >= 1
        assert len(model.personas) >= 1
        assert len(model.decision_frameworks) >= 1
        assert len(model.action_definitions) >= 2
        assert len(model.capability_definitions) >= 2
        assert len(model.context_contributors) >= 2


def test_cognitive_runtime_state_and_memory():
    """Verify Subsystem 2 Cognitive Runtime components: World Model & Memory System."""
    world_model = BusinessWorldModel(
        tenant_id="tenant_test_01",
        active_entities={"active_tables": 12, "active_patients": 45},
        active_workflows=["proc_rest_dine"],
        current_kpi_values={"RevPASH": 22.50, "DSO": 38.0}
    )
    assert world_model.tenant_id == "tenant_test_01"
    assert world_model.active_entities["active_tables"] == 12

    memory_sys = MemorySystem(tenant_id="tenant_test_01")
    mem1 = memory_sys.add_memory("Customer VIP prefers booth seating.", memory_type="SEMANTIC")
    assert len(memory_sys.memories) == 1
    assert mem1.content == "Customer VIP prefers booth seating."


def test_explainability_trace():
    """Verify Subsystem 2 ExplainabilityTrace audit logging."""
    trace = ExplainabilityTrace(
        decision_title="Emergency Ward Bed Surge Reallocation",
        evidence_references=["Triage Acuity Level 1 count = 4", "ICU occupancy = 95%"],
        reasoning_steps=["Detected ESI-1 arrival spike", "Reallocated ward bed #402"],
        assumptions_made=["Elective surgery patient discharge on schedule"],
        confidence_level=0.98,
        evaluated_trade_offs=["Delayed elective surgery admission by 2 hours"],
        applied_regulations=["HIPAA Emergency Exemption"]
    )
    assert trace.confidence_level == 0.98
    assert len(trace.evidence_references) == 2


def test_model_adapters_structured_payload_rendering():
    """Verify Subsystem 3 Model Adapters translate structured context without hardcoded prompt builders."""
    restaurant = RestaurantModule()
    context = CognitiveContext(
        tenant_id="tenant_test_01",
        task_goal="Optimize menu price for ingredient inflation",
        active_persona=restaurant.get_knowledge_model().personas[0],
        assembled_context_data={"food_cost_pct": 34.5}
    )

    # Test GPT Adapter
    gpt_payload = GPTAdapter().render_model_payload(context)
    assert gpt_payload["model"] == "gpt-4o"
    assert "Executive Chef" in gpt_payload["messages"][0]["content"]

    # Test Claude Adapter
    claude_payload = ClaudeAdapter().render_model_payload(context)
    assert claude_payload["model"] == "claude-3-5-sonnet"

    # Test Gemini Adapter
    gemini_payload = GeminiAdapter().render_model_payload(context)
    assert gemini_payload["model"] == "gemini-1.5-pro"

    # Test Local Model Adapter
    local_payload = LocalModelAdapter().render_model_payload(context)
    assert local_payload["model"] == "llama-3-70b-instruct"
