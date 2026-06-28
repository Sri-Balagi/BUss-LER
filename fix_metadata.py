with open("tests/services/test_intent_classifier.py", "r") as f:
    content = f.read()

content = content.replace("ClassifyMetadata", "AIResponseMetadata")
content = content.replace(
    """        metadata=AIResponseMetadata(
            provider="test",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=20
        )""",
    """        metadata=AIResponseMetadata(
            provider="test",
            model="test-model",
            latency_ms=10.0,
            prompt_tokens=10,
            completion_tokens=20
        )""",
)

content = content.replace(
    """        metadata=AIResponseMetadata(provider="test", model="test", prompt_tokens=10, completion_tokens=10)""",
    """        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0, prompt_tokens=10, completion_tokens=10)""",
)

content = content.replace(
    """        metadata=AIResponseMetadata(provider="test", model="test")""",
    """        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0)""",
)


with open("tests/services/test_intent_classifier.py", "w") as f:
    f.write(content)
