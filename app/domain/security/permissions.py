from enum import Enum

class SystemPermission(str, Enum):
    """
    Centralized enumeration of all valid permissions in the system.
    Using an Enum prevents typos and provides compile-time consistency.
    """
    # System/Admin level
    SYSTEM_ADMIN = "system:admin"
    
    # Workflows
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_WRITE = "workflow:write"
    WORKFLOW_EXECUTE = "workflow:execute"
    
    # Agents
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_INVOKE = "agent:invoke"
    
    # Artifacts
    ARTIFACT_READ = "artifact:read"
    ARTIFACT_WRITE = "artifact:write"
    
    # Memory
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
