from enum import StrEnum


class AgentPermission(StrEnum):
    """
    Declarative permissions for an agent.
    Enforced by the AgentContext and higher-level security boundaries.
    """

    READ_MEMORY = "READ_MEMORY"
    WRITE_MEMORY = "WRITE_MEMORY"
    EXECUTE_TOOL = "EXECUTE_TOOL"
    MODIFY_GOALS = "MODIFY_GOALS"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
