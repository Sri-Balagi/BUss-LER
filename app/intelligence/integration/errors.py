class IntelligenceError(Exception):
    """Base exception for deterministic propagation of failures inside the Intelligence Layer."""
    def __init__(self, message: str, layer: str):
        super().__init__(f"[{layer}] {message}")
        self.layer = layer
        self.message = message

class IntelligenceWarning(Warning):
    """Non-fatal anomalies detected during the intelligence pipeline execution."""
    pass
