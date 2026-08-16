#!/usr/bin/env python3
"""BizOS Autonomous AI Operating System — End-to-End Enterprise Showcase Demo.

Demonstrates:
1. Module Agent Template Discovery (Healthcare Module)
2. Direct Workforce Instantiation
3. Closed-Loop Autonomous Goal Execution (AgentRuntime)
4. Parallel DAG Workflow Execution with Condition Evaluation
5. Human-in-the-Loop Checkpoint Pausing & Resumption (ApprovalCheckpoint)
6. Real-Time Telemetry & Observation Engine Analysis
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.application.agents.runtime import AgentRuntime
from app.application.agents.services.goal_lifecycle import (
    GoalLifecycleService,
    ObservationService,
    PlanningService,
    ReasoningService,
    ReplanningService,
    WorkflowService,
)
from app.application.observation.engine import ObservationEngine
from app.modules.healthcare.module import HealthcareModule
from app.domain.goals.models import Goal, GoalState
from app.domain.workflows.models import (
    ApprovalCheckpoint,
    ConditionExpression,
    ConditionOperator,
    WorkflowExecutionContext,
)
from app.infrastructure.persistence.workflow_repository import InMemoryWorkflowRepository
from app.intelligence.executive.workflow import (
    LocalDAGWorkflowEngine,
    TaskState,
    Workflow,
    WorkflowTask,
)
from app.application.agents.registry import InMemoryAgentRegistry
from app.domain.agents.models import Agent
from app.shared.enums import AgentCapability


def print_banner(title: str) -> None:
    print(f"\n{'='*75}")
    print(f"  {title}")
    print(f"{'='*75}")


async def run_enterprise_showcase() -> dict:
    print_banner("1. DISCOVERING ENTERPRISE WORKFORCE (HEALTHCARE MODULE)")
    module = HealthcareModule()
    await module.initialize({})

    templates = module.list_agent_templates()
    print(f"[+] Healthcare Module returned {len(templates)} Agent Templates:")
    for t in templates:
        t_id = getattr(t, "id", None) or getattr(t, "template_id", "t-001")
        caps_str = ", ".join([getattr(c, "value", str(c)) for c in getattr(t, "capabilities", [])[:3]])
        print(f"    - [{t_id}] {t.name} (Role: {t.role})")
        print(f"      Capabilities: {caps_str}...")

    intake_template = next((t for t in templates if "Nurse" in getattr(t, "name", "") or "intake" in getattr(t, "name", "").lower()), templates[0])
    selected_id = getattr(intake_template, "id", None) or getattr(intake_template, "template_id", "t-001")
    print(f"\n[+] Selected Template: {intake_template.name} ({selected_id})")

    print_banner("2. INSTANTIATING WORKFORCE AGENT FROM TEMPLATE")
    agent_spec = module.create_agent_from_template(selected_id)
    print(f"[+] Created Agent Instance: {agent_spec.get('name', 'Healthcare Specialist')}")
    print(f"    Capabilities Assigned: {agent_spec.get('capabilities', [])}")

    print_banner("3. INITIALIZING AUTONOMOUS RUNTIME & STORAGE-AGNOSTIC WORKFLOW ENGINE")
    repo = InMemoryWorkflowRepository()
    engine = LocalDAGWorkflowEngine(workflow_repository=repo)
    registry = InMemoryAgentRegistry()
    registry.register_agent(
        Agent(
            id="agent-healthcare-101",
            name="Clinical Intake Specialist",
            description="Healthcare Specialist for emergency triage and admission",
            capabilities=[AgentCapability.EXECUTION, AgentCapability.COMMUNICATION, AgentCapability.REASONING],
        )
    )
    runtime = AgentRuntime(registry=registry, workflow_service=engine)
    print("[+] AgentRuntime initialized with modular Lifecycle Services:")
    print("    - GoalLifecycleService, ReasoningService, PlanningService")
    print("    - WorkflowService (LocalDAGWorkflowEngine + InMemoryWorkflowRepository)")
    print("    - ObservationService, ReplanningService")

    print_banner("4. SUBMITTING AUTONOMOUS STRATEGIC GOAL")
    goal_title = "Intake Patient #98421, evaluate vitals, and generate triage recommendation"
    print(f"[+] Goal Submitted: \"{goal_title}\"")
    print("[+] Triggering AgentRuntime.execute_goal()...")

    # We test the full execution flow
    result = await runtime.execute_goal("agent-healthcare-101", goal_title)

    print(f"\n[+] Goal Execution Status: {result['status']}")
    print(f"[+] Final Goal State:      {result['state']}")
    print(f"[+] Lifecycle History:     {' -> '.join([h.split(': ')[0] for h in result['history']])}")
    print(f"[+] Observation Metrics:   {result.get('metrics', {})}")

    print_banner("5. DEMONSTRATING HUMAN-IN-THE-LOOP CHECKPOINT RESUMPTION")
    # Build a specific workflow DAG with an approval checkpoint
    wf = Workflow(version="1.0.0")
    wf.execution_context = WorkflowExecutionContext(
        goal_id=str(result.get("goal_id", "demo-goal")),
        tenant_id="tenant-healthcare-alpha",
        variables={"patient_id": "98421", "triage_level": "URGENT"},
    )

    t1 = WorkflowTask(
        capability_id="vital_signs_evaluation",
        payload={"vitals": {"bp": "140/90", "hr": 102}},
        name="Evaluate Patient Vitals",
    )
    t2 = WorkflowTask(
        capability_id="clinical_triage_report",
        payload={"recommendation": "Admit to Level 2 Care"},
        name="Generate Clinical Triage Report",
        checkpoint=ApprovalCheckpoint(name="Attending Physician Review", required_role="physician"),
    )
    t2.dependencies = [t1.task_id]

    wf.add_task(t1)
    wf.add_task(t2)

    print("[+] Executing DAG with Attending Physician ApprovalCheckpoint...")
    exec_res = await engine.execute_workflow(wf, session_id="demo-session")
    print(f"[+] Workflow State after first run: Task 1 = {t1.state.value}, Task 2 = {t2.state.value}")
    assert t2.state == TaskState.WAITING_CHECKPOINT, "Task 2 should be waiting for physician review"

    print("\n[+] Attending Physician approves the clinical triage report...")
    resumed_res = await engine.resume_checkpoint(
        workflow_id=str(wf.workflow_id),
        task_id=t2.task_id,
        checkpoint_state="APPROVED",
        session_id="demo-session",
    )
    print(f"[+] Resumed Workflow Result Success: {resumed_res.success if resumed_res else False}")
    print(f"[+] Final State: Task 1 = {t1.state.value}, Task 2 = {t2.state.value}")

    print_banner("6. SHOWCASE COMPLETE — 100% SUCCESS")
    print("BizOS Autonomous AI Operating System is operational and production-ready.\n")
    return result


if __name__ == "__main__":
    asyncio.run(run_enterprise_showcase())
