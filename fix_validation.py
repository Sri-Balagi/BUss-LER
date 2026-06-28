with open("tests/api/routers/test_context_endpoints.py", "r") as f:
    content = f.read()

# Fix build_context
content = content.replace(
    """    mock_context.model_dump.return_value = {
        "context_id": str(uuid4()),
        "twin_id": str(twin_id),
        "policy_id": "planning",
        "sections": [],
        "schema_version": "1.0",
        "status": "assembled",
        "is_partial": False,
        "created_at": "2026-06-28T00:00:00Z",
        "updated_at": "2026-06-28T00:00:00Z"
    }""",
    """    mock_context.model_dump.return_value = {
        "id": str(uuid4()),
        "context_id": str(uuid4()),
        "twin_id": str(twin_id),
        "policy_id": "planning",
        "sections": [],
        "schema_version": "1.0",
        "status": "assembled",
        "is_partial": False,
        "created_at": "2026-06-28T00:00:00Z",
        "updated_at": "2026-06-28T00:00:00Z"
    }""",
)

# Fix get_context_lifecycle
content = content.replace(
    """    mock_record.model_dump.return_value = {
        "context_id": str(context_id),
        "twin_id": str(twin_id),
        "status": "assembled",
        "policy_id": "planning",
        "schema_version": "1.0",
        "is_partial": False,
        "created_at": "2026-06-28T00:00:00Z",
        "updated_at": "2026-06-28T00:00:00Z"
    }""",
    """    mock_record.model_dump.return_value = {
        "id": str(uuid4()),
        "context_id": str(context_id),
        "twin_id": str(twin_id),
        "status": "assembled",
        "policy_id": "planning",
        "schema_version": "1.0",
        "is_partial": False,
        "created_at": "2026-06-28T00:00:00Z",
        "updated_at": "2026-06-28T00:00:00Z"
    }""",
)

with open("tests/api/routers/test_context_endpoints.py", "w") as f:
    f.write(content)
