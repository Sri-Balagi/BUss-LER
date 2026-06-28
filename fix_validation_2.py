with open("tests/api/routers/test_context_endpoints.py", "r") as f:
    content = f.read()

# Fix list_context_history_success validation errors
content = content.replace(
    """    mock_result.model_dump.return_value = {
        "items": [],
        "total": 0,
        "page": 1,
        "size": 20
    }""",
    """    mock_result.model_dump.return_value = {
        "items": [],
        "total_count": 0,
        "limit": 20,
        "offset": 0
    }""",
)

# Fix get_context_lifecycle_success id field
content = content.replace(
    """    mock_record.model_dump.return_value = {
        "id": str(uuid4()),
        "context_id": str(context_id),""",
    """    mock_record.model_dump.return_value = {
        "id": str(context_id),
        "context_id": str(context_id),""",
)

# Fix test_get_context_lifecycle_success assertion
content = content.replace(
    """    assert response.json()["context_id"] == str(context_id)""",
    """    assert response.json()["id"] == str(context_id)""",
)

# Fix test_build_context_success assert
content = content.replace(
    """    mock_context.model_dump.return_value = {
        "id": str(uuid4()),
        "context_id": str(uuid4()),""",
    """    mock_context.model_dump.return_value = {
        "id": str(uuid4()),
        "context_id": str(uuid4()),""",
)


with open("tests/api/routers/test_context_endpoints.py", "w") as f:
    f.write(content)
