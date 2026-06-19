"""AI chat — store concierge + admin Copilot. SSE streaming."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from .. import data
from ..ai.base import get_provider
from ..auth import current_user
from ..schemas import ChatRequest

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(req: ChatRequest, user=Depends(current_user)):
    # Store concierge is public; the admin Copilot requires login.
    if req.surface == "copilot" and not user:
        raise HTTPException(status_code=401, detail="Copilot 需要登录")
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
