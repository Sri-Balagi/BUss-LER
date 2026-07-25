"""Transformation Pipeline for payload processing."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from app.connectors.canonical.base import CanonicalObject
from app.connectors.exceptions.errors import TransformationError


class ITransformStage(ABC):
    """A single stage in the transformation pipeline."""

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process data and pass to the next stage."""


class TransformationPipeline:
    """
    Pipeline executing transformation stages in sequence:
    Validate → Normalize → MapFields → Filter → Enrich → Serialize
    """

    def __init__(self, stages: list[ITransformStage] | None = None) -> None:
        self._stages = stages or []

    def add_stage(self, stage: ITransformStage) -> TransformationPipeline:
        self._stages.append(stage)
        return self

    async def run(self, raw_payload: dict[str, Any]) -> Any:
        current: Any = raw_payload
        for stage in self._stages:
            try:
                current = await stage.process(current)
            except Exception as e:
                raise TransformationError(
                    f"Transformation failed at stage {stage.__class__.__name__}: {e}"
                ) from e
        return current
