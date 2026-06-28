with open("tests/api/routers/test_context_endpoints.py", "r") as f:
    content = f.read()

content = content.replace(
    """        "metadata": {},
        "window": {"start_time": "2026-06-28T00:00:00Z", "end_time": "2026-06-28T23:59:59Z"},""",
    """        "metadata": {"policy_id": "planning"},
        "window": {"start_time": "2026-06-28T00:00:00Z", "end_time": "2026-06-28T23:59:59Z", "budget": 1000},""",
)

with open("tests/api/routers/test_context_endpoints.py", "w") as f:
    f.write(content)
