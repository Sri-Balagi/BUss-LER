"""Notification Framework for registering event templates and alerting rules."""

from pydantic import BaseModel, Field


class NotificationTemplateSpec(BaseModel):
    """Spec for event-driven notification templates."""

    template_id: str
    module_id: str
    event_name: str
    title_template: str
    body_template: str
    channels: list[str] = Field(default_factory=lambda: ["in_app", "email"])


class ModuleNotificationRegistry:
    """Registry managing module notification templates."""

    def __init__(self) -> None:
        self._templates: dict[str, NotificationTemplateSpec] = {}

    def register_template(self, template: NotificationTemplateSpec) -> None:
        """Register a notification template."""
        self._templates[template.template_id] = template

    def get_template_for_event(self, event_name: str) -> NotificationTemplateSpec | None:
        """Fetch template by event name."""
        for t in self._templates.values():
            if t.event_name == event_name:
                return t
        return None
