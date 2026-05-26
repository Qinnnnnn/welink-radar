"""Group tags route — favorites and category assignments."""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from core.database import get_db
import time

router = APIRouter(prefix="/api/group-tags", tags=["group-tags"])


class TagAction(BaseModel):
    conversation_id: str
    group_id: int | None = None
    action: str | None = None  # "add" | "remove"
    fav: bool | None = None


@router.get("")
async def get_tags(conversation_id: str = Query(...)):
    """Get group tag IDs and favorite status for a conversation."""
    db = get_db()
    tags = db.execute(
        "SELECT group_id FROM group_tags WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchall()
    fav = db.execute(
        "SELECT 1 FROM favorites WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    return {
        "ok": True,
        "group_ids": [t["group_id"] for t in tags],
        "is_favorite": fav is not None,
    }


@router.post("")
async def post_tags(payload: TagAction):
    """Add/remove tag or set favorite status."""
    db = get_db()
    now = int(time.time())

    if payload.fav is not None:
        if payload.fav:
            db.execute(
                "INSERT OR REPLACE INTO favorites (conversation_id, starred_at) VALUES (?, ?)",
                (payload.conversation_id, now),
            )
        else:
            db.execute(
                "DELETE FROM favorites WHERE conversation_id = ?",
                (payload.conversation_id,),
            )
        db.commit()
        return {"ok": True}

    if payload.action and payload.group_id:
        if payload.action == "add":
            db.execute(
                "INSERT OR IGNORE INTO group_tags (conversation_id, group_id) VALUES (?, ?)",
                (payload.conversation_id, payload.group_id),
            )
        elif payload.action == "remove":
            db.execute(
                "DELETE FROM group_tags WHERE conversation_id = ? AND group_id = ?",
                (payload.conversation_id, payload.group_id),
            )
        db.commit()
        return {"ok": True}

    return {"ok": False, "error": "Invalid payload"}
