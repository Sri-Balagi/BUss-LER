with open("app/application/di.py") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.strip() == "# Planning":
        skip = True
        new_lines.append(line)
        new_lines.append("""
    from app.application.planning.planning_engine import PlanningEngine
    from app.infrastructure.persistence.postgres.repositories.plan_repository import PlanRepository
    from app.application.planning.plan_service import PlanService
    from app.application.planning.context_builder import ContextBuilder as PlanContextBuilder

    def build_plan_repo(c: "Container") -> PlanRepository:
        return PlanRepository(client=c.resolve(AsyncClient))
    container.register_factory(PlanRepository, build_plan_repo)
    container.register_factory(PlanService, lambda c: PlanService(
        repository=c.resolve(PlanRepository),
        event_bus=c.resolve(EventBus)
    ))

    from app.infrastructure.vectorstore.qdrant import QdrantService
    container.register_factory(PlanContextBuilder, lambda c: PlanContextBuilder(
        goal_service=c.resolve(GoalService),
        memory_service=c.resolve(QdrantService)
    ))

    container.register_factory(PlanningEngine, lambda c: PlanningEngine(
        ai_kernel=c.resolve(AbstractAIKernel),
        plan_repository=c.resolve(PlanRepository),
        context_builder=c.resolve(PlanContextBuilder),
        goal_service=c.resolve(GoalService),
        trace_service=c.resolve(CognitiveTraceService),
        event_bus=c.resolve(EventBus)
    ))

    # Recommendation
    from app.application.recommendation.recommendation_engine import RecommendationEngine
    from app.infrastructure.persistence.postgres.repositories.recommendation_repository import RecommendationRepository
    from app.application.recommendation.recommendation_service import RecommendationService

    def build_rec_repo(c: "Container") -> RecommendationRepository:
        return RecommendationRepository(client=c.resolve(AsyncClient))
    container.register_factory(RecommendationRepository, build_rec_repo)
    container.register_factory(RecommendationService, lambda c: RecommendationService(
        repository=c.resolve(RecommendationRepository),
        event_bus=c.resolve(EventBus)
    ))
    container.register_factory(RecommendationEngine, lambda c: RecommendationEngine(
        ai_kernel=c.resolve(AbstractAIKernel),
        repository=c.resolve(RecommendationRepository),
        context_builder=c.resolve(PlanContextBuilder),
        trace_service=c.resolve(CognitiveTraceService),
        event_bus=c.resolve(EventBus)
    ))
""")
    elif line.strip() == "# Context Engine":
        skip = False

    if not skip:
        new_lines.append(line)

with open("app/application/di.py", "w") as f:
    f.writelines(new_lines)
