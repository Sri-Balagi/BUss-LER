import os
from typing import Any, Dict

class ConfigurationManager:
    def __init__(self, defaults: Dict[str, Any] = None):
        self._config = defaults or {}

    def get(self, key: str, default: Any = None) -> Any:
        # Check environment first
        env_val = os.environ.get(key.upper())
        if env_val is not None:
            return env_val
        # Check hierarchical dictionary via dot notation
        keys = key.split('.')
        val = self._config
        try:
            for k in keys:
                val = val[k]
            return val
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        keys = key.split('.')
        d = self._config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
