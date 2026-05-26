"""Mentions route."""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from services.mention_index import list_mentions, count_mentions, mark_mentions_seen
from core.database import get_db

router = APIRouter(prefix="/api/mentions", tags=["mentions"])


class MarkSeenPayload(BaseModel):
    conversation_id: str | None = None


@router.get("")
async def get_mentions(limit: int = Query(default=1000, le=5000)):
    """List recent @mentions enriched with conversation names."""
    mentions = list_mentions(limit=limit)

    # Enrich with conversation names
    db = get_db()
    for m in mentions:
        conv = db.execute(
            "SELECT name FROM conversations WHERE conversation_id = ?",
            (m["conversation_id"],),
        ).fetchone()
        m["conversation_name"] = conv["name"] if conv else m["conversation_id"]

    total = count_mentions()
    return {"ok": True, "total": total, "items": mentions}


@router.post("")
async def mark_seen(payload: MarkSeenPayload):
    """Mark mentions as seen."""
    count = mark_mentions_seen(payload.conversation_id)
    return {"ok": True, "marked": count}
