from typing import List
from uuid import UUID

from app.domain.planning.models import Plan
from app.domain.planning.validator import IPlanValidator


class DefaultPlanValidator(IPlanValidator):
    """
    Default validation implementation for Plans.
    Validates duplicates, orphans, and cyclic dependencies.
    """
    
    def validate_plan(self, plan: Plan) -> List[str]:
        errors = []
        
        # 1. Check for duplicates
        step_ids = []
        for step in plan.steps:
            if step.step_id in step_ids:
                errors.append(f"Duplicate step ID found: {step.step_id}")
            else:
                step_ids.append(step.step_id)
                
        # 2. Check for orphans / invalid prerequisites
        valid_step_ids = set(step_ids)
        for dep in plan.dependencies:
            if dep.step_id not in valid_step_ids:
                errors.append(f"Dependency references non-existent step_id: {dep.step_id}")
            if dep.depends_on_step_id not in valid_step_ids:
                errors.append(f"Dependency references non-existent depends_on_step_id: {dep.depends_on_step_id}")
                
        # 3. Check for cycles
        if not errors:
            cycle_error = self._detect_cycle(plan)
            if cycle_error:
                errors.append(cycle_error)
                
        return errors
        
    def _detect_cycle(self, plan: Plan) -> str | None:
        """Detects cyclic dependencies in the plan graph using DFS."""
        # Build adjacency list (node -> list of nodes it depends on)
        graph: dict[UUID, list[UUID]] = {step.step_id: [] for step in plan.steps}
        for dep in plan.dependencies:
            if dep.step_id in graph:
                graph[dep.step_id].append(dep.depends_on_step_id)
                
        visited = set()
        recursion_stack = set()
        
        def is_cyclic(node_id: UUID) -> bool:
            visited.add(node_id)
            recursion_stack.add(node_id)
            
            for neighbor in graph.get(node_id, []):
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True
                    
            recursion_stack.remove(node_id)
            return False
            
        for node in graph:
            if node not in visited:
                if is_cyclic(node):
                    return f"Cyclic dependency detected involving step {node}"
                    
        return None
