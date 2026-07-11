"""Goal Context Provider — fetches active goals for the twin."""



from datetime import datetime, timezone

from uuid import UUID, uuid4



import structlog



from app.intelligence.intake.situation.enterprise_context import ContextItem, ContextProvenance, ContextSection

from app.shared.enums import ContextPriority, ContextSource, GoalPriority

from app.application.context.providers.abstract import AbstractContextProvider



logger = structlog.get_logger(__name__)



_GOAL_PRIORITY_MAP = {

    "critical": ContextPriority.CRITICAL,

    "high": ContextPriority.HIGH,

    "medium": ContextPriority.MEDIUM,

    "low": ContextPriority.LOW,

}





class GoalContextProvider(AbstractContextProvider):

    """Retrieves active goals via GoalService."""



    def __init__(self, goal_service) -> None:

        self._goal_service = goal_service



    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:

        items = []

        try:

            goals = await self._goal_service.get_active_goals(ctx, twin_id)

            for goal in goals[: policy.max_goals]:

                content = (

                    f"Goal: {goal.title}\n"

                    f"Description: {goal.description or ''}\n"

                    f"Status: {goal.status.value}\n"

                    f"Priority: {goal.priority.value if hasattr(goal, 'priority') else 'medium'}"

                )

                token_est = len(content) // 4

                ctx_priority = _GOAL_PRIORITY_MAP.get(

                    getattr(goal, "priority", GoalPriority.MEDIUM).value

                    if hasattr(getattr(goal, "priority", None), "value")

                    else "medium",

                    ContextPriority.MEDIUM,

                )

                prov = ContextProvenance(

                    provider=ContextSource.GOAL,

                    service_name="GoalService",

                    retrieval_timestamp=datetime.now(timezone.utc),

                    confidence=1.0,

                    citations=[str(goal.id)],

                )

                items.append(

                    ContextItem(

                        item_id=uuid4(),

                        source=ContextSource.GOAL,

                        priority=ctx_priority,

                        content=content,

                        domain_object_id=goal.id,

                        token_estimate=token_est,

                        provenance=prov,

                    )

                )

        except Exception as exc:

            logger.warning("GoalContextProvider failed", error=str(exc))



        return ContextSection(

            section_id=uuid4(),

            source=ContextSource.GOAL,

            priority=ContextPriority.HIGH,

            items=items,

            token_estimate=sum(i.token_estimate for i in items),

            retrieved_at=datetime.now(timezone.utc),

        )



    async def health_check(self) -> dict:

        return {"goal_context_provider": "ok"}

