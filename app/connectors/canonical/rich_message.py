"""Rich messaging component models (Buttons, QuickReplies, Cards, Carousels, Menus)."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from app.connectors.canonical.base import CanonicalObject


class CanonicalButton(BaseModel):
    button_id: str
    title: str
    button_type: str = "reply"  # reply, url, phone_number, postback
    payload: str | None = None
    url: str | None = None


class CanonicalQuickReply(BaseModel):
    reply_id: str
    title: str
    payload: str
    icon_url: str | None = None


class CanonicalCard(BaseModel):
    title: str
    subtitle: str | None = None
    image_url: str | None = None
    buttons: list[CanonicalButton] = Field(default_factory=list)


class CanonicalCarousel(CanonicalObject):
    cards: list[CanonicalCard] = Field(default_factory=list)


class CanonicalMenuOption(BaseModel):
    option_id: str
    title: str
    description: str | None = None
    payload: str


class CanonicalMenu(CanonicalObject):
    title: str
    options: list[CanonicalMenuOption] = Field(default_factory=list)


class CanonicalRichMessage(CanonicalObject):
    text: str | None = None
    cards: list[CanonicalCard] = Field(default_factory=list)
    quick_replies: list[CanonicalQuickReply] = Field(default_factory=list)
    menu: CanonicalMenu | None = None
