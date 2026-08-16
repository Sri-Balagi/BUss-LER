from pathlib import Path

from app.intelligence.capabilities import ICapability


def test_icapability_exists():
    """Verify ICapability file exists at correct path and is importable."""
    assert ICapability is not None
    assert ICapability.__name__ == "ICapability"


def test_icapability_path_exists():
    """Architecture test: verify the capability package exists."""
    path = (
        Path(__file__).parent.parent.parent.parent
        / "app"
        / "intelligence"
        / "capabilities"
        / "__init__.py"
    )
    assert path.exists()
