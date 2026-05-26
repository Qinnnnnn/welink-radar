"""Group detail route — single conversation view."""

from fastapi import APIRouter, Query
from core.database import get_db
from services.message_store import list_messages_for_date, get_sync_state, list_all_synced_dates
from datetime import datetime, timezone

router = APIRouter(prefix="/api/group", tags=["group"])


@router.get("/{conv_id}")
async def get_group_detail(
    conv_id: str,
    date: str = Query(default=""),
    limit: int = Query(default=1000, le=5000),
):
    """Return group detail: daily stats, recent messages, history, sync state."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target_date = date or today

    db = get_db()

    # Conversation info
    conv = db.execute(
        "SELECT * FROM conversations WHERE conversation_id = ?",
        (conv_id,),
    ).fetchone()

    # Messages for the date
    messages = list_messages_for_date(conv_id, target_date, limit)

    # Daily stats
    stats = db.execute(
        "SELECT * FROM daily_stats WHERE conversation_id = ? AND date = ?",
        (conv_id, target_date),
    ).fetchone()

    # Sync state
    sync = get_sync_state(conv_id)

    # All synced dates
    synced_dates = list_all_synced_dates(conv_id)

    # Daily history (last 30 days)
    daily_history = db.execute(
        """SELECT date, total FROM daily_stats
           WHERE conversation_id = ? AND date <= ?
           ORDER BY date DESC LIMIT 30""",
        (conv_id, target_date),
    ).fetchall()

    # Tags
    tags = db.execute(
        """SELECT g.id, g.name, g.color, g.emoji
           FROM group_tags gt JOIN groups g ON gt.group_id = g.id
           WHERE gt.conversation_id = ?""",
        (conv_id,),
    ).fetchall()

    # Favorite status
    fav = db.execute(
        "SELECT 1 FROM favorites WHERE conversation_id = ?",
        (conv_id,),
    ).fetchone()

    return {
        "ok": True,
        "conversation_id": conv_id,
        "conversation": dict(conv) if conv else None,
        "date": target_date,
        "stats": dict(stats) if stats else None,
        "recent": messages,
        "daily_history": [dict(r) for r in daily_history],
        "synced_dates": synced_dates,
        "sync_state": sync,
        "tags": [dict(t) for t in tags],
        "is_favorite": fav is not None,
    }
