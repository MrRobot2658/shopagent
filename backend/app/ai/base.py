"""AI provider interface.

The rest of the app talks only to this abstraction, so swapping the mock for a
real model (Claude via Anthropic / Vercel AI Gateway) is a one-line change in
the factory below — no router edits.
"""
from __future__ import annotations

from typing import AsyncIterator, Protocol

from .. import config


class AIProvider(Protocol):
    async def stream_chat(self, surface: str, store: dict | None, messages: list[dict]) -> AsyncIterator[str]:
        """Yield response text chunks (token-ish) for a chat turn."""
        ...

    async def generate_content(self, kind: str, store: dict | None, language: str, params: dict) -> str:
        """Return generated marketing copy."""
        ...

    async def generate_image(self, store: dict | None, operation: str, scene: str, source: str | None) -> dict:
        """Return an image-generation result descriptor."""
        ...


def get_provider() -> AIProvider:
    if config.AI_PROVIDER == "claude":
        try:
            from .claude import ClaudeProvider

            return ClaudeProvider()
        except Exception as exc:  # missing key/sdk -> degrade to mock, don't crash
            print(f"[ai] claude provider unavailable ({exc}); falling back to mock")
    from .mock import MockProvider

    return MockProvider()
