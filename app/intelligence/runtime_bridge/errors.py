class RuntimeIntegrationError(Exception):
    """Base exception for deterministic propagation of runtime failures back to intelligence."""
    def __init__(self, message: str, component: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message

class RuntimeWarning(Warning):
    """Non-fatal anomalies detected during runtime execution."""
    pass
