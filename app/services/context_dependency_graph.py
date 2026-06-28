"""Context Dependency Graph — Extension A.

Resolves provider execution order via topological sort (Kahn's algorithm).
Produces ExecutionPlan with batches of concurrently-safe providers.

The graph operates on ContextSource identifiers only — it is provider-agnostic.
Cycle detection happens at registration time to prevent deadlocks during assembly.
"""

from collections import deque
from typing import Dict, List, Set

from app.models.enterprise_context import ExecutionPlan, ProviderDependency
from app.models.enums import ContextSource
from app.models.exceptions import ContextDependencyCycleError


class ContextDependencyGraph:
    """Topological resolver for ContextProvider execution order.

    Usage:
        graph = ContextDependencyGraph()
        graph.register(ProviderDependency(provider=ContextSource.CONVERSATION,
                                           depends_on=[ContextSource.TWIN]))
        plan = graph.resolve([ContextSource.TWIN, ContextSource.CONVERSATION])
        # plan.batches → [[TWIN], [CONVERSATION]]
    """

    def __init__(self) -> None:
        # adjacency: source → set of sources it depends on
        self._dependencies: Dict[ContextSource, Set[ContextSource]] = {}

    def register(self, dependency: ProviderDependency) -> None:
        """Register a provider dependency.

        Raises:
            ContextDependencyCycleError: If registration creates a cycle.
        """
        if dependency.provider not in self._dependencies:
            self._dependencies[dependency.provider] = set()
        for dep in dependency.depends_on:
            self._dependencies[dependency.provider].add(dep)

        # Validate no cycle was introduced
        self._detect_cycle()

    def resolve(self, active_providers: List[ContextSource]) -> ExecutionPlan:
        """Produce an ExecutionPlan for the given set of active providers.

        Uses Kahn's algorithm to produce topologically sorted batches.
        Each batch contains providers that can run concurrently.

        Args:
            active_providers: The providers requested by the current ContextPolicy.

        Returns:
            ExecutionPlan with ordered batches of concurrently-safe providers.
        """
        # Build subgraph for only active providers
        active_set: Set[ContextSource] = set(active_providers)

        # in_degree: how many active dependencies each provider is waiting for
        in_degree: Dict[ContextSource, int] = {p: 0 for p in active_set}
        # dependents: for each provider, which providers depend on it
        dependents: Dict[ContextSource, List[ContextSource]] = {p: [] for p in active_set}

        for provider in active_set:
            deps = self._dependencies.get(provider, set())
            active_deps = deps & active_set  # only dependencies within active set
            in_degree[provider] = len(active_deps)
            for dep in active_deps:
                dependents[dep].append(provider)

        # Kahn's algorithm — build batches
        batches: List[List[ContextSource]] = []
        queue: deque[ContextSource] = deque(
            p for p in active_set if in_degree[p] == 0
        )

        while queue:
            # Everything currently in the queue can run concurrently
            batch = list(queue)
            batches.append(batch)
            queue.clear()

            for provider in batch:
                for dependent in dependents[provider]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        total_resolved = sum(len(b) for b in batches)
        if total_resolved < len(active_set):
            # Remaining providers could not be scheduled — there is a cycle
            unresolved = [p.value for p in active_set if in_degree[p] > 0]
            raise ContextDependencyCycleError(unresolved)

        return ExecutionPlan(batches=batches, total_providers=len(active_set))

    def _detect_cycle(self) -> None:
        """Full cycle detection across all registered providers.

        Raises:
            ContextDependencyCycleError: If a cycle is detected.
        """
        all_providers = list(self._dependencies.keys())
        if not all_providers:
            return

        visited: Dict[ContextSource, str] = {}  # "visiting" | "visited"

        def dfs(node: ContextSource, path: List[ContextSource]) -> None:
            if visited.get(node) == "visiting":
                cycle_start = path.index(node)
                raise ContextDependencyCycleError(
                    [p.value for p in path[cycle_start:]] + [node.value]
                )
            if visited.get(node) == "visited":
                return
            visited[node] = "visiting"
            for dep in self._dependencies.get(node, set()):
                dfs(dep, path + [node])
            visited[node] = "visited"

        for provider in all_providers:
            if provider not in visited:
                dfs(provider, [])


# =============================================================================
# Default dependency declarations for M4 providers
# =============================================================================

DEFAULT_DEPENDENCIES: List[ProviderDependency] = [
    # Conversation depends on Twin (need twin to scope the thread)
    ProviderDependency(
        provider=ContextSource.CONVERSATION,
        depends_on=[ContextSource.TWIN],
    ),
    # Business state is extracted from Twin state
    ProviderDependency(
        provider=ContextSource.BUSINESS_STATE,
        depends_on=[ContextSource.TWIN],
    ),
    # All other providers are independent
    ProviderDependency(provider=ContextSource.MEMORY, depends_on=[]),
    ProviderDependency(provider=ContextSource.INTENT, depends_on=[]),
    ProviderDependency(provider=ContextSource.GOAL, depends_on=[]),
    ProviderDependency(provider=ContextSource.PLAN, depends_on=[]),
    ProviderDependency(provider=ContextSource.RECOMMENDATION, depends_on=[]),
    ProviderDependency(provider=ContextSource.TWIN, depends_on=[]),
    ProviderDependency(provider=ContextSource.TRACE, depends_on=[]),
    ProviderDependency(provider=ContextSource.EXTERNAL, depends_on=[]),
]


def build_default_dependency_graph() -> ContextDependencyGraph:
    """Construct and return the default M4 dependency graph."""
    graph = ContextDependencyGraph()
    for dep in DEFAULT_DEPENDENCIES:
        graph.register(dep)
    return graph
