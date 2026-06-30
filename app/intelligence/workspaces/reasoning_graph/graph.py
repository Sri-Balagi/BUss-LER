from typing import Any, Dict, List


class ReasoningNode:
    def __init__(self, node_id: str, content: Any, node_type: str):
        self.node_id = node_id
        self.content = content
        self.node_type = node_type # e.g. "Hypothesis", "Evidence", "Decision"

class ExecutiveReasoningGraph:
    """
    Stores a non-linear graph of hypotheses, evidence, alternative strategies, and confidence evolution.
    """
    def __init__(self):
        self.nodes: dict[str, ReasoningNode] = {}
        self.edges: list[tuple[str, str, str]] = [] # from, to, relationship

    def add_node(self, node: ReasoningNode):
        self.nodes[node.node_id] = node

    def add_edge(self, from_id: str, to_id: str, relationship: str):
        self.edges.append((from_id, to_id, relationship))
