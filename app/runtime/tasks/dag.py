from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.runtime.core.exceptions import ExecutionError
from app.runtime.tasks.models import ITask


class DAGValidationError(ExecutionError):
    """Raised when the DAG is invalid (cycles, missing dependencies)."""
    pass

class GraphMetadata(BaseModel):
    """Metadata characteristics of the Task DAG."""
    node_count: int
    edge_count: int
    depth: int
    max_parallelism: int

class TaskDAG(BaseModel):
    """
    Directed Acyclic Graph of Tasks.
    Validates dependencies and provides topological layers for execution.
    """
    tasks: dict[UUID, ITask] = Field(default_factory=dict)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def add_task(self, task: ITask) -> None:
        """Adds a task to the DAG. Does not validate until explicitly requested."""
        if task.task_id in self.tasks:
            raise DAGValidationError(f"Task {task.task_id} already exists in DAG.")
        self.tasks[task.task_id] = task

    def validate(self) -> None:
        """
        Validates the DAG:
        1. Checks for missing dependencies.
        2. Detects cycles using DFS.
        """
        self._check_missing_dependencies()
        self._check_for_cycles()

    def _check_missing_dependencies(self) -> None:
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id not in self.tasks:
                    raise DAGValidationError(f"Task {task_id} depends on missing task {dep_id}.")

    def _check_for_cycles(self) -> None:
        visited: set[UUID] = set()
        path: set[UUID] = set()

        def dfs(node_id: UUID) -> None:
            if node_id in path:
                raise DAGValidationError(f"Cycle detected involving task {node_id}.")
            if node_id in visited:
                return

            path.add(node_id)
            task = self.tasks[node_id]
            for dep_id in task.dependencies:
                dfs(dep_id)

            path.remove(node_id)
            visited.add(node_id)

        for task_id in self.tasks:
            dfs(task_id)

    def get_topological_layers(self) -> list[set[UUID]]:
        """
        Returns the tasks grouped by topological execution layers.
        Layer 0 can be executed immediately.
        Layer N depends on Layer N-1.
        """
        self.validate()

        in_degree: dict[UUID, int] = {task_id: 0 for task_id in self.tasks}
        graph: dict[UUID, list[UUID]] = {task_id: [] for task_id in self.tasks}

        # Build graph edges (Dependency -> Dependent)
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                graph[dep_id].append(task_id)
                in_degree[task_id] += 1

        layers = []
        # Find all nodes with 0 in-degree
        current_layer = {node for node, degree in in_degree.items() if degree == 0}

        while current_layer:
            layers.append(current_layer)
            next_layer = set()

            for node in current_layer:
                for dependent in graph[node]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_layer.add(dependent)

            current_layer = next_layer

        return layers

    def get_metadata(self) -> GraphMetadata:
        """Computes structural characteristics of the DAG."""
        layers = self.get_topological_layers()
        node_count = len(self.tasks)
        edge_count = sum(len(task.dependencies) for task in self.tasks.values())
        depth = len(layers)
        max_parallelism = max((len(layer) for layer in layers), default=0)

        return GraphMetadata(
            node_count=node_count,
            edge_count=edge_count,
            depth=depth,
            max_parallelism=max_parallelism
        )
