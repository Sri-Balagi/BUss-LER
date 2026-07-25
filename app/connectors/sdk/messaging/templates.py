"""SDK Messaging Template Framework."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class TemplateVariable(BaseModel):
    name: str
    value: str
    variable_type: str = "text"  # text, currency, date_time, media


class CanonicalTemplate(BaseModel):
    template_id: str
    name: str
    language: str = "en"
    category: str = "UTILITY"  # MARKETING, UTILITY, AUTHENTICATION
    header: str | None = None
    body: str
    footer: str | None = None
    variables: list[TemplateVariable] = Field(default_factory=list)
    buttons: list[dict[str, str]] = Field(default_factory=list)


class TemplateRenderer:
    """Renders CanonicalTemplate instances into vendor-specific payload structures."""

    @staticmethod
    def render_body(template: CanonicalTemplate) -> str:
        text = template.body
        for var in template.variables:
            text = text.replace(f"{{{{{var.name}}}}}", var.value)
        return text
