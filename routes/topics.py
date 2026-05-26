"""Topics routes — daily topic aggregation."""

import asyncio
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from services.topics import build_topics_for_date, list_topics, get_topic_detail
from datetime import datetime, timezone

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("")
async def get_topics(date: str = Query(default="")):
    """List topics for a date."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target_date = date or today
    topics = list_topics(target_date)
    return {"ok": True, "date": target_date, "topics": topics}


@router.get("/{topic_id}")
async def get_topic(topic_id: int):
    """Get topic detail with associated messages."""
    detail = get_topic_detail(topic_id)
    if not detail:
        return {"ok": False, "error": "Topic not found"}, 404
    return {"ok": True, **detail}


@router.post("/build")
async def build_topics(date: str = Query(default="")):
    """Build topics for a date using AI, with SSE progress."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target_date = date or today

    async def event_stream():
        async def progress_callback(data):
            pass  # Could send SSE events

        result = await build_topics_for_date(target_date, on_progress=progress_callback)
        import json
        yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
