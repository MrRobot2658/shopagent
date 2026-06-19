"""AI content + image generation."""
from __future__ import annotations

from fastapi import APIRouter

from .. import data
from ..ai.base import get_provider
from ..schemas import ContentRequest, ImageRequest

router = APIRouter(prefix="/api/ai", tags=["ai-gen"])


@router.post("/content")
async def generate_content(req: ContentRequest):
    provider = get_provider()
    store = data.store_by_key(req.store) if req.store else None
    text = await provider.generate_content(req.kind, store, req.language, req.params)
    return {"kind": req.kind, "language": req.language, "content": text}


@router.post("/image")
async def generate_image(req: ImageRequest):
    provider = get_provider()
    store = data.store_by_key(req.store) if req.store else None
    result = await provider.generate_image(store, req.operation, req.scene, req.source)
    return result
