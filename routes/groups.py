"""Groups CRUD — manage user-defined group categories."""

import time
from fastapi import APIRouter, Query
from pydantic import BaseModel
from core.database import get_db

router = APIRouter(prefix="/api/groups", tags=["groups"])


class CreateGroupPayload(BaseModel):
    name: str
    color: str
    emoji: str | None = None


@router.get("")
async def list_groups():
    """List all group categories."""
    db = get_db()
    rows = db.execute("SELECT * FROM groups ORDER BY sort_order").fetchall()
    return {"ok": True, "groups": [dict(r) for r in rows]}


@router.post("")
async def create_group(payload: CreateGroupPayload):
    """Create a new group category."""
    db = get_db()
    now = int(time.time())
    cursor = db.execute(
        """INSERT INTO groups (name, color, emoji, sort_order, created_at)
           VALUES (?, ?, ?, (SELECT COALESCE(MAX(sort_order), 0) + 1 FROM groups), ?)""",
        (payload.name, payload.color, payload.emoji, now),
    )
    db.commit()
    return {"ok": True, "id": cursor.lastrowid}


@router.delete("")
async def delete_group(id: int = Query(...)):
    """Delete a group category."""
    db = get_db()
    db.execute("DELETE FROM group_tags WHERE group_id = ?", (id,))
    db.execute("DELETE FROM groups WHERE id = ?", (id,))
    db.commit()
    return {"ok": True}
