with open("tests/api/routers/test_context_endpoints.py", "r") as f:
    content = f.read()

content = content.replace(
    """    assert "id" in response.json()""",
    """    assert "context_id" in response.json()""",
)

with open("tests/api/routers/test_context_endpoints.py", "w") as f:
    f.write(content)
