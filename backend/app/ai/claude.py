"""Real Claude provider (optional).

Activated with AI_PROVIDER=claude and ANTHROPIC_API_KEY set. Requires the
`anthropic` package (uncomment it in requirements.txt). Falls back to mock via
the factory in base.py if the SDK or key is missing. Content/image generation
delegate to the mock templates for now — only chat is wired to the live model.
"""
from __future__ import annotations

from typing import AsyncIterator

from .. import config
from .mock import MockProvider

SYSTEM_PROMPTS = {
    "store": (
        "You are a friendly, concise e-commerce shopping concierge. Help with product "
        "recommendations, sizing, shipping, care, and returns. Use the store context provided."
    ),
    "copilot": (
        "你是 DTC 跨境电商后台的运营副驾（Copilot）。用简洁中文回答经营数据汇总、客户分层、"
        "AI 内容/修图、订单与物流等问题，并给出可执行建议。"
    ),
}


class ClaudeProvider(MockProvider):
    def __init__(self) -> None:
        import anthropic  # raises if not installed -> factory falls back to mock

        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        kwargs = {"api_key": config.ANTHROPIC_API_KEY}
        if config.ANTHROPIC_BASE_URL:
            kwargs["base_url"] = config.ANTHROPIC_BASE_URL
        self._client = anthropic.AsyncAnthropic(**kwargs)

    async def stream_chat(self, surface, store, messages) -> AsyncIterator[str]:
        system = SYSTEM_PROMPTS.get(surface, SYSTEM_PROMPTS["store"])
        if store:
            system += f"\n\nStore context: {store.get('name')} — {store.get('tagline')}."
        convo = [{"role": m["role"], "content": m["content"]} for m in messages if m["role"] != "system"]
        async with self._client.messages.stream(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=system,
            messages=convo or [{"role": "user", "content": "Hello"}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
