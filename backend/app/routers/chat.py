"""AI chat — store concierge + admin Copilot. SSE streaming."""
from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .. import data
from ..ai.base import get_provider
from ..schemas import ChatRequest

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(req: ChatRequest):
    provider = get_provider()
    store = data.store_by_key(req.store) if req.store else None
    messages = [m.model_dump() for m in req.messages]

    if not req.stream:
        parts = []
        async for chunk in provider.stream_chat(req.surface, store, messages):
            parts.append(chunk)
        return {"reply": "".join(parts)}

    async def event_stream():
        async for chunk in provider.stream_chat(req.surface, store, messages):
            yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
