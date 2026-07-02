class Evidence:
    def __init__(self, fact_id: str, description: str, source: str):
        self.fact_id = fact_id
        self.description = description
        self.source = source


class EvidenceStore:
    """
    First-class data store providing immutable facts for the reasoning graph to link to.
    """

    def __init__(self):
        self._evidence: dict[str, Evidence] = {}

    def add_evidence(self, evidence: Evidence):
        self._evidence[evidence.fact_id] = evidence

    def get_evidence(self, fact_id: str) -> Evidence:
        return self._evidence.get(fact_id)
