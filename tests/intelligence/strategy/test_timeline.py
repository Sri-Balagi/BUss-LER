from app.intelligence.strategy.timeline.engine import StrategicTimelineEngine
from app.intelligence.strategy.objectives.models import ExecutiveObjective

def test_generate_timeline():
    engine = StrategicTimelineEngine()
    
    obj1 = ExecutiveObjective(objective_id="o1", description="Objective 1")
    obj2 = ExecutiveObjective(objective_id="o2", description="Objective 2")
    
    timeline = engine.generate_timeline([obj1, obj2])
    
    assert timeline.horizon_label == "Current Horizon"
    assert len(timeline.milestones) == 2
    assert timeline.milestones[0].milestone_id == "ms_o1"
    assert timeline.milestones[1].milestone_id == "ms_o2"
