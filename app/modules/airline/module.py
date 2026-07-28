from app.core.modules.base import BusinessModule

class AirlineModule(BusinessModule):
    """Generated airline module."""
    
    def __init__(self):
        super().__init__()
        
    async def initialize(self, context) -> bool:
        return True
