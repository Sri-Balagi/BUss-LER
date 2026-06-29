from app.intelligence.strategy.conflict.engine import ObjectiveConflictResolver
from app.intelligence.strategy.conflict.models import ConflictType
from app.intelligence.strategy.objectives.models import ExecutiveObjective

def test_detect_conflicts():
    engine = ObjectiveConflictResolver()
    
    obj1 = ExecutiveObjective(objective_id="1", description="Grow revenue significantly")
    obj2 = ExecutiveObjective(objective_id="2", description="Reduce costs across the board")
    
    conflicts = engine.detect_conflicts([obj1, obj2], [])
    
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == ConflictType.MUTUALLY_EXCLUSIVE
    assert "1" in conflicts[0].involved_objective_ids
    assert "2" in conflicts[0].involved_objective_ids

def test_no_conflicts():
    engine = ObjectiveConflictResolver()
    obj1 = ExecutiveObjective(objective_id="1", description="Improve satisfaction")
    conflicts = engine.detect_conflicts([obj1], [])
    
    assert len(conflicts) == 0
