from enum import Enum, auto


class CapabilityPermission(Enum):
    """
    Declarative permissions for capability execution.
    """

    MEMORY_READ = auto()
    MEMORY_WRITE = auto()

    DB_READ = auto()
    DB_WRITE = auto()
    DB_DELETE = auto()

    FS_READ = auto()
    FS_WRITE = auto()
    FS_DELETE = auto()

    NETWORK_HTTP_GET = auto()
    NETWORK_HTTP_POST = auto()

    AI_INFERENCE = auto()
    AI_EMBEDDINGS = auto()

    EMAIL_READ = auto()
    EMAIL_SEND = auto()

    CALENDAR_READ = auto()
    CALENDAR_MODIFY = auto()
