with open("tests/api/routers/test_context_endpoints.py", "r") as f:
    content = f.read()

content = content.replace(
    'mocker.patch.object(mock_context_repo, "get_by_id", return_value=mock_record)',
    "mock_context_repo.get_by_id_result = mock_record",
)

with open("tests/api/routers/test_context_endpoints.py", "w") as f:
    f.write(content)
