from app.intelligence.strategy.goals.engine import GoalManagementEngine
from app.intelligence.strategy.goals.models import GoalStatus
from app.intelligence.strategy.objectives.models import ExecutiveObjective

def test_derive_goals():
    engine = GoalManagementEngine()
    objective = ExecutiveObjective(
        objective_id="obj1",
        description="Expand market",
        success_criteria=["Launch in EU", "Launch in Asia"]
    )
    
    collection = engine.derive_goals(objective)
    
    assert collection.objective_id == "obj1"
    assert len(collection.goals) == 2
    assert collection.goals[0].status == GoalStatus.PENDING

def test_activate_and_complete_goal():
    engine = GoalManagementEngine()
    objective = ExecutiveObjective(
        objective_id="obj1",
        description="Expand market",
        success_criteria=["Launch in EU"]
    )
    
    collection = engine.derive_goals(objective)
    goal = collection.goals[0]
    
    assert goal.status == GoalStatus.PENDING
    
    activated = engine.activate_goal(goal)
    assert activated.status == GoalStatus.ACTIVE
    
    completed = engine.complete_goal(goal)
    assert completed.status == GoalStatus.COMPLETED
