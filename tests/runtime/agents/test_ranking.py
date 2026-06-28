import pytest
from app.runtime.agents.health import AgentHealth
from app.runtime.agents.specification import AgentSpecification
from app.runtime.agents.ranking import HealthRankingStrategy, CostRankingStrategy, CompositeRankingStrategy
from app.runtime.agents.capability import Capability
from app.runtime.agents.registry import ResolutionContext

def test_health_ranking_strategy():
    strategy = HealthRankingStrategy()
    spec = AgentSpecification(identity="dummy", capabilities=["test"])
    context = ResolutionContext(requested_capability=Capability(capability_id="test"))
    
    # Healthy
    health1 = AgentHealth(success_rate=1.0, recent_failures=0)
    score1 = strategy.score(spec, health1, context)
    assert score1.overall_score == 1.0
    
    # Unhealthy with penalty
    health2 = AgentHealth(success_rate=0.8, recent_failures=2)
    score2 = strategy.score(spec, health2, context)
    assert score2.overall_score == pytest.approx(0.6) # 0.8 - 0.2
    
    # Cooldown (score 0)
    health3 = AgentHealth(success_rate=0.0, in_cooldown=True)
    score3 = strategy.score(spec, health3, context)
    assert score3.overall_score == 0.0

def test_composite_ranking_strategy():
    strategy = CompositeRankingStrategy([HealthRankingStrategy(), CostRankingStrategy()])
    spec = AgentSpecification(identity="dummy", capabilities=["test"])
    context = ResolutionContext(requested_capability=Capability(capability_id="test"))
    
    health = AgentHealth(success_rate=1.0)
    
    score = strategy.score(spec, health, context)
    # Health: 1.0, Cost: 1.0 -> Composite avg: 1.0
    assert score.overall_score == 1.0
    assert score.health_contribution == 1.0
    assert score.cost_contribution == 1.0
