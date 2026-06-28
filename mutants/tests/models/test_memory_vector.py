from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4


from app.models.enums import MemoryCategory, MemorySource
from app.models.memory_vector import MemoryVectorPayload, MemoryVectorPoint


def test_memory_vector_payload_valid():
    """Test valid instantiation of the Qdrant payload."""
    data = {
        "memory_id": uuid4(),
        "twin_id": uuid4(),
        "memory_category": MemoryCategory.OBSERVATION,
        "source": MemorySource.OBSERVATION,
    }

    data["importance"] = Decimal("0.75")
    data["created_at"] = datetime.now(timezone.utc)
    data["updated_at"] = datetime.now(timezone.utc)

    payload = MemoryVectorPayload(**data)
    assert payload.memory_category == MemoryCategory.OBSERVATION
    assert payload.importance == Decimal("0.75")


def test_memory_vector_point_valid():
    """Test valid instantiation of the Qdrant Point."""
    point_id = uuid4()
    payload = MemoryVectorPayload(
        memory_id=point_id,
        twin_id=uuid4(),
        memory_category=MemoryCategory.EVENT,
        source=MemorySource.OBSERVATION,
        importance=Decimal("0.50"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    vector = [0.1, 0.2, -0.3, 0.5]

    point = MemoryVectorPoint(
        id=point_id,
        vector=vector,
        payload=payload,
    )

    assert point.id == point_id
    assert point.vector == vector
    assert point.payload.importance == Decimal("0.50")
    assert point.score is None
