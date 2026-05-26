"""AI Classify route — heuristic group classification."""

from fastapi import APIRouter
from pydantic import BaseModel
from core.database import get_db
from services.group_classifier import classify_conversation_heuristic

router = APIRouter(prefix="/api/ai-classify", tags=["ai-classify"])


class ClassifyPick(BaseModel):
    conversation_id: str
    group_id: int


class ClassifyPayload(BaseModel):
    picks: list[ClassifyPick]


@router.get("")
async def get_classify():
    """Get unclassified conversations with heuristic suggestions."""
    db = get_db()

    # Conversations without tags
    convs = db.execute(
        """SELECT c.* FROM conversations c
           WHERE c.conversation_id NOT IN (SELECT DISTINCT conversation_id FROM group_tags)
           ORDER BY c.updated_at DESC"""
    ).fetchall()

    groups = db.execute("SELECT * FROM groups ORDER BY sort_order").fetchall()
    group_list = [dict(g) for g in groups]

    suggestions = []
    for c in convs:
        conv = dict(c)
        heuristic = classify_conversation_heuristic(conv["name"], "")
        if heuristic:
            group_row = db.execute(
                "SELECT id FROM groups WHERE name = ?", (heuristic,)
            ).fetchone()
            group_id = group_row["id"] if group_row else None
        else:
            group_id = None

        suggestions.append({
            "conversation_id": conv["conversation_id"],
            "name": conv["name"],
            "type": conv["type"],
            "suggested_group": heuristic,
            "suggested_group_id": group_id,
        })

    return {"ok": True, "groups": group_list, "suggestions": suggestions}


@router.post("")
async def post_classify(payload: ClassifyPayload):
    """Apply group tags to conversations."""
    db = get_db()
    applied = 0
    for pick in payload.picks:
        try:
            db.execute(
                "INSERT OR IGNORE INTO group_tags (conversation_id, group_id) VALUES (?, ?)",
                (pick.conversation_id, pick.group_id),
            )
            if db.changes > 0:
                applied += 1
        except Exception:
            pass
    db.commit()
    return {"ok": True, "applied": applied}
