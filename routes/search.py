"""Global search route."""

from fastapi import APIRouter, Query
from core.database import get_db

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
async def search(q: str = Query(min_length=2)):
    """Search conversations, messages, and links."""
    db = get_db()
    results = []
    pattern = f"%{q}%"

    # Search conversations
    convs = db.execute(
        "SELECT conversation_id, name, type FROM conversations WHERE name LIKE ? LIMIT 5",
        (pattern,),
    ).fetchall()
    for c in convs:
        results.append({
            "type": "conversation",
            "id": c["conversation_id"],
            "title": c["name"],
            "subtitle": c["type"],
        })

    # Search messages
    msgs = db.execute(
        """SELECT m.conversation_id, c.name as conversation_name,
                  m.sender, m.content, m.send_time, m.msg_id
           FROM messages m
           LEFT JOIN conversations c ON m.conversation_id = c.conversation_id
           WHERE m.content LIKE ?
           ORDER BY m.timestamp DESC LIMIT 10""",
        (pattern,),
    ).fetchall()
    for m in msgs:
        results.append({
            "type": "message",
            "id": f"{m['conversation_id']}_{m['msg_id']}",
            "title": f"{m['sender']}: {m['content'][:80]}",
            "subtitle": m.get("conversation_name", m["conversation_id"]),
        })

    # Search link titles
    links = db.execute(
        "SELECT canonical_url, title, domain FROM message_links WHERE title LIKE ? LIMIT 5",
        (pattern,),
    ).fetchall()
    for l in links:
        results.append({
            "type": "link",
            "id": l["canonical_url"],
            "title": l["title"] or l["canonical_url"][:80],
            "subtitle": l["domain"],
        })

    return {"ok": True, "results": results}
