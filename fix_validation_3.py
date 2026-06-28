with open("tests/api/routers/test_context_endpoints.py", "r") as f:
    content = f.read()

# Fix test_build_context_success validation
content = content.replace(
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
    """    mock_context.model_dump.return_value = {
        "id": str(uuid4()),
        "context_id": str(uuid4()),
        "twin_id": str(twin_id),
        "policy_id": "planning",
        "sections": [],
        "metadata": {},
        "window": {"start_time": "2026-06-28T00:00:00Z", "end_time": "2026-06-28T23:59:59Z"},
        "schema_version": "1.0",
        "status": "assembled",
        "is_partial": False,
        "created_at": "2026-06-28T00:00:00Z",
        "updated_at": "2026-06-28T00:00:00Z"
    }""",
)

# Fix test_list_context_history_success assertion
content = content.replace(
    """    assert response.json()["total"] == 0""",
    """    assert response.json()["total_count"] == 0""",
)

with open("tests/api/routers/test_context_endpoints.py", "w") as f:
    f.write(content)
