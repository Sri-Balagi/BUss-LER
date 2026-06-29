from app.intelligence.workspaces.blackboard.blackboard import ExecutiveBlackboard, Hypothesis
from app.intelligence.workspaces.evidence.evidence_store import EvidenceStore, Evidence
from app.intelligence.workspaces.reasoning_graph.graph import ExecutiveReasoningGraph, ReasoningNode
from app.intelligence.workspaces.world_model.world_model import BusinessWorldModel, Belief
from app.intelligence.workspaces.repository.knowledge import ExecutiveKnowledgeRepository, StrategicKnowledge

def test_executive_blackboard():
    blackboard = ExecutiveBlackboard()
    received = []
    
    def handler(hypothesis: Hypothesis):
        received.append(hypothesis.description)
        
    blackboard.subscribe("hypotheses", handler)
    blackboard.post_hypothesis(Hypothesis("Market is expanding"))
    
    assert len(received) == 1
    assert received[0] == "Market is expanding"

def test_evidence_store():
    store = EvidenceStore()
    ev = Evidence("f1", "Q3 Sales up 20%", "Salesforce")
    store.add_evidence(ev)
    
    retrieved = store.get_evidence("f1")
    assert retrieved is not None
    assert retrieved.description == "Q3 Sales up 20%"

def test_reasoning_graph():
    graph = ExecutiveReasoningGraph()
    n1 = ReasoningNode("n1", "Reduce costs", "Goal")
    n2 = ReasoningNode("n2", "Layoffs", "Strategy")
    
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_edge("n1", "n2", "fulfilled_by")
    
    assert "n1" in graph.nodes
    assert len(graph.edges) == 1

def test_world_model():
    model = BusinessWorldModel()
    belief = Belief("sentiment", "declining", 0.8)
    model.update_belief(belief)
    
    retrieved = model.get_belief("sentiment")
    assert retrieved.value == "declining"
    assert retrieved.confidence == 0.8

def test_knowledge_repository():
    repo = ExecutiveKnowledgeRepository()
    knowledge = StrategicKnowledge("k1", "Never launch in Q4 without prep", "Heuristic")
    repo.store_knowledge(knowledge)
    
    retrieved = repo.retrieve_knowledge("k1")
    assert retrieved.content == "Never launch in Q4 without prep"
