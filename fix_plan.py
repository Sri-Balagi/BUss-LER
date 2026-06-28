with open("tests/services/test_planning_engine.py", "r") as f:
    content = f.read()

# Fix mock dictionaries
content = content.replace(
    """        raw_json={
            "title": "Test Plan",
            "description": "Plan desc",
            "steps": [{"title": "Step 1", "description": "Step 1 desc", "status": "pending"}],
            "estimated_duration_minutes": 60,
            "confidence": 0.9,
            "status": "draft"
        },""",
    """        raw_json={
            "rationale": "Because testing is good",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Write tests",
                    "expected_outcome": "Tests pass"
                }
            ],
            "confidence": 0.9
        },""",
)

content = content.replace(
    """        raw_json={
            "title": "Test Plan",
            "description": "Plan desc",
            "steps": [],
            "estimated_duration_minutes": 60,
            "confidence": 0.9,
            "status": "draft"
        },""",
    """        raw_json={
            "rationale": "Because testing is good",
            "steps": [],
            "confidence": 0.9
        },""",
)

with open("tests/services/test_planning_engine.py", "w") as f:
    f.write(content)
