from typing import Dict, Any
from app.runtime.capabilities.adapters.base import IResourceAdapter
from app.runtime.capabilities.models.request import CapabilityRequest

class MockFilesystemAdapter(IResourceAdapter):
    def __init__(self):
        self.connected = False
        self.initialized = False
        
    async def initialize(self) -> None:
        self.initialized = True
        
    async def connect(self) -> None:
        self.connected = True
        
    async def execute(self, request: CapabilityRequest) -> Dict[str, Any]:
        if not self.connected:
            raise RuntimeError("Adapter not connected")
        if request.operation == "read":
            return {"data": "file_contents_mock"}
        raise ValueError(f"Unsupported operation {request.operation}")
        
    async def disconnect(self) -> None:
        self.connected = False
        
    async def cleanup(self) -> None:
        self.initialized = False

class MockDatabaseAdapter(IResourceAdapter):
    def __init__(self):
        self.connected = False
        self.initialized = False
        self.query_count = 0
        
    async def initialize(self) -> None:
        self.initialized = True
        
    async def connect(self) -> None:
        self.connected = True
        
    async def execute(self, request: CapabilityRequest) -> Dict[str, Any]:
        if not self.connected:
            raise RuntimeError("Adapter not connected")
        self.query_count += 1
        if request.operation == "query":
            return {"rows": [{"id": 1, "name": "mock"}]}
        raise ValueError(f"Unsupported operation {request.operation}")
        
    async def disconnect(self) -> None:
        self.connected = False
        
    async def cleanup(self) -> None:
        self.initialized = False

class MockNetworkAdapter(IResourceAdapter):
    def __init__(self):
        self.connected = False
        self.initialized = False
        
    async def initialize(self) -> None:
        self.initialized = True
        
    async def connect(self) -> None:
        self.connected = True
        
    async def execute(self, request: CapabilityRequest) -> Dict[str, Any]:
        if not self.connected:
            raise RuntimeError("Adapter not connected")
        if request.operation == "get":
            return {"status": 200, "body": "mock_response"}
        if request.operation == "fail":
            raise ConnectionError("Mock network failure")
        raise ValueError(f"Unsupported operation {request.operation}")
        
    async def disconnect(self) -> None:
        self.connected = False
        
    async def cleanup(self) -> None:
        self.initialized = False
