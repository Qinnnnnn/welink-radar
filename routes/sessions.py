"""Sessions route — list conversations with category tags."""

from fastapi import APIRouter, Request
from core.database import get_db
from clients.welink import get_sessions

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("")
async def list_sessions():
    """List all conversations with group tags and favorites."""
    db = get_db()

    # Get stored conversations
    convs = db.execute(
        "SELECT * FROM conversations ORDER BY updated_at DESC"
    ).fetchall()

    # Get group tags
    tags = db.execute(
        """SELECT gt.conversation_id, g.id as group_id, g.name as group_name, g.color, g.emoji
           FROM group_tags gt JOIN groups g ON gt.group_id = g.id"""
    ).fetchall()

    # Get favorites
    favs = db.execute("SELECT conversation_id FROM favorites").fetchall()
    fav_set = {f["conversation_id"] for f in favs}

    # Get all groups
    groups = db.execute("SELECT * FROM groups ORDER BY sort_order").fetchall()
    categories = [dict(g) for g in groups]

    # Build result
    result = []
    tag_map = {}
    for t in tags:
        cid = t["conversation_id"]
        if cid not in tag_map:
            tag_map[cid] = []
        tag_map[cid].append({"id": t["group_id"], "name": t["group_name"],
                              "color": t["color"], "emoji": t["emoji"]})

    for c in convs:
        conv = dict(c)
        conv["tags"] = tag_map.get(conv["conversation_id"], [])
        conv["is_favorite"] = conv["conversation_id"] in fav_set

        # Get last message time
        last_msg = db.execute(
            "SELECT send_time FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 1",
            (conv["conversation_id"],),
        ).fetchone()
        conv["last_message_time"] = last_msg["send_time"] if last_msg else None

        result.append(conv)

    return {"ok": True, "total": len(result), "groups": result, "categories": categories}
