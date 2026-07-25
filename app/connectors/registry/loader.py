"""
Connector Loader — discovers and registers connector packages automatically.

The loader scans ``app/connectors/builtin/`` and any paths declared in
``BIZOS_CONNECTOR_PATHS`` environment variable. Each package must contain
a ``manifest.py`` module that exposes a ``MANIFEST`` variable of type
``ConnectorManifest``.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
from pathlib import Path

from app.connectors.exceptions.errors import ConnectorLoadError
from app.connectors.registry.manifest import ConnectorManifest
from app.connectors.registry.registry import ConnectorRegistry

logger = logging.getLogger(__name__)

_BUILTIN_PATH = Path(__file__).parent.parent / "builtin"
_MANIFEST_MODULE = "manifest"
_MANIFEST_ATTR = "MANIFEST"


class ConnectorLoader:
    """
    Discovers connector packages and registers their manifests.

    Discovery rules:
    1. Scans ``app/connectors/builtin/`` by default.
    2. Scans additional paths from ``BIZOS_CONNECTOR_PATHS`` env var
       (colon-separated list of directories).
    3. Each package must have a ``manifest.py`` file with a ``MANIFEST``
       attribute of type ``ConnectorManifest``.

    Usage::

        loader = ConnectorLoader(registry)
        loaded = loader.load_all()
    """

    def __init__(self, registry: ConnectorRegistry) -> None:
        self._registry = registry

    def load_all(self) -> list[str]:
        """
        Discover and register all available connectors.

        Returns:
            List of successfully registered connector IDs.
        """
        search_paths = self._get_search_paths()
        loaded: list[str] = []

        for path in search_paths:
            connector_ids = self._scan_directory(path)
            loaded.extend(connector_ids)

        logger.info(
            "ConnectorLoader: loaded %d connector(s) from %d path(s)",
            len(loaded),
            len(search_paths),
        )
        return loaded

    def load_one(self, connector_dir: Path) -> str:
        """
        Load and register a single connector from the given directory.

        Returns:
            The registered connector ID.

        Raises:
            ConnectorLoadError: If the connector cannot be loaded.
        """
        manifest = self._load_manifest(connector_dir)
        self._registry.register(manifest, overwrite=True)
        return manifest.id

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_search_paths(self) -> list[Path]:
        paths: list[Path] = []

        if _BUILTIN_PATH.exists():
            paths.append(_BUILTIN_PATH)

        extra = os.environ.get("BIZOS_CONNECTOR_PATHS", "")
        if extra:
            for raw in extra.split(":"):
                p = Path(raw.strip())
                if p.exists() and p.is_dir():
                    paths.append(p)
                else:
                    logger.warning(
                        "BIZOS_CONNECTOR_PATHS contains invalid path: %s", raw
                    )

        return paths

    def _scan_directory(self, directory: Path) -> list[str]:
        """Scan a directory recursively for connector packages."""
        loaded: list[str] = []
        if not directory.is_dir():
            return loaded

        for manifest_path in directory.rglob("manifest.py"):
            child = manifest_path.parent
            if child.name.startswith("_"):
                continue
            try:
                connector_id = self.load_one(child)
                loaded.append(connector_id)
            except Exception as e:
                logger.error(
                    "Failed to load connector from %s: %s", child, e
                )
        return loaded

    def _load_manifest(self, connector_dir: Path) -> ConnectorManifest:
        """Import the manifest module and extract the MANIFEST object."""
        manifest_path = connector_dir / f"{_MANIFEST_MODULE}.py"
        if not manifest_path.exists():
            raise ConnectorLoadError(
                f"No manifest.py found in {connector_dir}",
                connector_id=connector_dir.name,
            )

        module_name = f"bizos_connector_{connector_dir.name}_manifest"
        spec = importlib.util.spec_from_file_location(module_name, manifest_path)
        if spec is None or spec.loader is None:
            raise ConnectorLoadError(
                f"Cannot create module spec for {manifest_path}",
                connector_id=connector_dir.name,
            )

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise ConnectorLoadError(
                f"Error executing manifest module at {manifest_path}: {e}",
                connector_id=connector_dir.name,
            ) from e

        manifest = getattr(module, _MANIFEST_ATTR, None)
        if manifest is None:
            raise ConnectorLoadError(
                f"manifest.py at {manifest_path} must define a MANIFEST attribute",
                connector_id=connector_dir.name,
            )

        if not isinstance(manifest, ConnectorManifest):
            raise ConnectorLoadError(
                f"MANIFEST in {manifest_path} must be a ConnectorManifest instance",
                connector_id=connector_dir.name,
            )

        return manifest
