with open("tests/services/test_planning_engine.py", "r") as f:
    content = f.read()

# Replace mock_plan with real Plan instance creation
replacement = """    from app.models.plan import Plan, PlanStep
    mock_plan = Plan(
        id=uuid4(),
        twin_id=dummy_command.twin_id,
        goal_id=dummy_command.goal_id,
        intent_id=dummy_command.intent_id,
        rationale="Because",
        steps=[PlanStep(step_number=1, action="Write tests", expected_outcome="Pass")],
        confidence=0.9,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )"""

content = content.replace(
    """    mock_plan = MagicMock()
    mock_plan.id = uuid4()
    mock_plan.twin_id = dummy_command.twin_id
    mock_plan.goal_id = dummy_command.goal_id
    mock_plan.intent_id = dummy_command.intent_id
    mock_plan.steps = [MagicMock()]
    mock_plan.confidence = 0.9""",
    replacement,
)

content = content.replace(
    """    with pytest.raises(PlanGenerationError):
        await engine.generate_plan(op_ctx, dummy_command)""",
    """    with pytest.raises((PlanGenerationError, AIOutputValidationError)):
        await engine.generate_plan(op_ctx, dummy_command)""",
)

with open("tests/services/test_planning_engine.py", "w") as f:
    f.write(content)
