"""Rescan route — trigger history sync with SSE progress."""

import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.database import get_db
from services.stats_aggregator import sync_conversation_history
from datetime import datetime, timezone

router = APIRouter(prefix="/api/rescan", tags=["rescan"])


class RescanPayload(BaseModel):
    range: str = "week"
    anchorDate: str | None = None
    since: str | None = None
    until: str | None = None
    full: bool = False


@router.post("")
async def rescan(payload: RescanPayload):
    """Rescan history and stream progress via SSE."""
    db = get_db()
    convs = db.execute("SELECT * FROM conversations").fetchall()

    async def event_stream():
        total = len(convs)
        for conv in convs:
            c = dict(conv)
            is_group = c["type"] == "group"
            target = c["group_id"] if is_group else c["target_account"]
            if not target:
                continue

            yield f"data: {json.dumps({'type': 'sync_start', 'conversation_id': c['conversation_id'], 'name': c['name']}, ensure_ascii=False)}\n\n"

            try:
                result = await sync_conversation_history(
                    conversation_id=c["conversation_id"],
                    target=target,
                    is_group=is_group,
                    max_sync_days=365 if payload.full else 7,
                )
                yield f"data: {json.dumps({'type': 'sync_done', **result}, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'sync_error', 'conversation_id': c['conversation_id'], 'error': str(e)}, ensure_ascii=False)}\n\n"

            await asyncio.sleep(0.5)  # Rate limiting

        yield f"data: {json.dumps({'type': 'complete', 'total_conversations': total}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
