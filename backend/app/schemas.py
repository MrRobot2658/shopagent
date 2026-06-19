"""Pydantic request/response models."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    # "store" -> shopper-facing concierge; "copilot" -> admin operator assistant.
    surface: Literal["store", "copilot"] = "store"
    store: Optional[str] = None  # store key or slug for context
    messages: list[ChatMessage] = Field(default_factory=list)
    stream: bool = True


class OrderItemIn(BaseModel):
    id: str
    qty: int = Field(default=1, ge=1)


class CheckoutRequest(BaseModel):
    store: str
    customer: Optional[str] = "Guest"
    country: str = "US"
    items: list[OrderItemIn]


class ContentRequest(BaseModel):
    kind: Literal["product_desc", "seo_blog", "social", "edm"] = "product_desc"
    store: Optional[str] = None
    language: str = "English"
    # free-form inputs: category, material, keywords, channel, ...
    params: dict = Field(default_factory=dict)


class ImageRequest(BaseModel):
    store: Optional[str] = None
    operation: Literal["bg_remove", "scene_swap", "upscale", "video"] = "scene_swap"
    scene: str = "雪天"
    source: Optional[str] = None  # filename / url placeholder
