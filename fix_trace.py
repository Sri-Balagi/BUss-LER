with open("tests/services/test_intent_classifier.py", "r") as f:
    content = f.read()

content = content.replace(
    """    mock_trace_result.trace = MagicMock()""",
    """    mock_trace_result.trace = None""",
)

with open("tests/services/test_intent_classifier.py", "w") as f:
    f.write(content)
