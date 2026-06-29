import uuid
from app.intelligence.strategy.objectives.models import ExecutiveObjective
from app.intelligence.strategy.goals.models import Goal, GoalStatus, GoalCollection

class GoalManagementEngine:
    """
    Derives tactical goals from strategic objectives and maintains their hierarchy.
    Does not execute goals.
    """
    
    def derive_goals(self, objective: ExecutiveObjective) -> GoalCollection:
        goals = []
        for criteria in objective.success_criteria:
            goal = Goal(
                goal_id=str(uuid.uuid4()),
                objective_id=objective.objective_id,
                description=f"Achieve: {criteria}",
                status=GoalStatus.PENDING
            )
            goals.append(goal)
            
        return GoalCollection(
            objective_id=objective.objective_id,
            goals=goals
        )
        
    def activate_goal(self, goal: Goal) -> Goal:
        goal.status = GoalStatus.ACTIVE
        return goal
        
    def complete_goal(self, goal: Goal) -> Goal:
        goal.status = GoalStatus.COMPLETED
        return goal
