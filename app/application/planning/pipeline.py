import time
from typing import cast

from app.application.intelligence.kernel import EventRouter
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.pipeline import IIntelligencePipeline, PipelineContext, PipelineResult
from app.domain.intelligence.provider import ICapabilityRegistry
from app.domain.intelligence.telemetry import IntelligenceMetrics
from app.domain.planning.events import (
    PlanGenerated,
    PlanGenerationStarted,
    PlanValidationFailed,
    PlanValidationSucceeded,
)
from app.domain.planning.models import Goal, Plan, PlanningContext, PlanStatus
from app.domain.planning.provider import IPlanningProvider
from app.domain.planning.validator import IPlanValidator


class PlanningPipeline(IIntelligencePipeline):
    """
    Orchestrates the generation and validation of execution plans.
    """

    def __init__(
        self,
        registry: ICapabilityRegistry,
        validator: IPlanValidator,
        event_router: EventRouter,
    ):
        self._registry = registry
        self._validator = validator
        self._event_router = event_router

    async def execute(self, context: PipelineContext[Goal]) -> PipelineResult[Plan]:
        start_time = time.perf_counter()

        planning_context = cast(PlanningContext, context.execution_context)
        goal: Goal = context.payload

        # Publish PlanGenerationStarted event
        await self._event_router.publish(
            PlanGenerationStarted(
                goal_id=goal.goal_id,
                tenant_id=planning_context.tenant_id,
                correlation_id=planning_context.correlation_id,
            )
        )

        # Resolve Provider
        provider = cast(IPlanningProvider | None, self._registry.resolve_provider(CapabilityType.PLANNING))
        if not provider:
            raise RuntimeError("No available PLANNING provider found in capability registry.")

        # Initialize CognitiveTrace
        from app.domain.intelligence.trace import CognitiveTrace
        trace = CognitiveTrace()

        # Generate Plan
        plan = await provider.generate_plan(planning_context, goal, trace)

        # Validation
        plan.transition_status(PlanStatus.VALIDATING)
        validation_result = self._validator.validate_plan(planning_context, goal, plan, trace)

        if validation_result:
            plan.transition_status(PlanStatus.INVALID, errors=validation_result)
            await self._event_router.publish(
                PlanValidationFailed(
                    plan_id=plan.plan_id,
                    goal_id=goal.goal_id,
                    tenant_id=planning_context.tenant_id,
                    errors=validation_result,
                    correlation_id=planning_context.correlation_id,
                )
            )
        else:
            plan.transition_status(PlanStatus.VALIDATED)
            # Immutability applies logically here - the Plan model shouldn't mutate past VALIDATED
            await self._event_router.publish(
                PlanValidationSucceeded(
                    plan_id=plan.plan_id,
                    goal_id=goal.goal_id,
                    tenant_id=planning_context.tenant_id,
                    correlation_id=planning_context.correlation_id,
                )
            )
            await self._event_router.publish(
                PlanGenerated(
                    plan_id=plan.plan_id,
                    goal_id=goal.goal_id,
                    tenant_id=planning_context.tenant_id,
                    correlation_id=planning_context.correlation_id,
                )
            )
            
        from app.domain.planning.events import PolicyApplied, ConstraintEvaluated, ProcessEvaluated
        
        # Publish specific evaluation events from trace
        for policy in trace.evaluated_policies:
            await self._event_router.publish(PolicyApplied(
                plan_id=plan.plan_id,
                policy_id=policy.artifact_id,
                tenant_id=planning_context.tenant_id,
                correlation_id=planning_context.correlation_id
            ))
        for constraint in trace.evaluated_constraints:
            await self._event_router.publish(ConstraintEvaluated(
                plan_id=plan.plan_id,
                constraint_id=constraint.artifact_id,
                tenant_id=planning_context.tenant_id,
                correlation_id=planning_context.correlation_id,
                result=not validation_result
            ))
        for process in trace.evaluated_processes:
            await self._event_router.publish(ProcessEvaluated(
                plan_id=plan.plan_id,
                process_id=process.artifact_id,
                tenant_id=planning_context.tenant_id,
                correlation_id=planning_context.correlation_id
            ))

        duration = time.perf_counter() - start_time
        metrics = IntelligenceMetrics(
            duration_ms=duration * 1000,
            token_usage={},
            provider_metadata=provider.get_metadata().model_dump()
        )

        return PipelineResult(
            context=planning_context,
            payload=plan,
            metrics=metrics
        )
