from typing import Optional
import importlib
from app.reference_library.types import ReferenceProvider

def get_provider(module_name: str) -> Optional[ReferenceProvider]:
    try:
        module = importlib.import_module(f"app.reference_library.providers.{module_name}")
        return getattr(module, "Provider")(module_name)
    except (ImportError, AttributeError):
        return None
