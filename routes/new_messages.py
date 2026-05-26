"""New messages SSE stream — polls welink-cli for new messages."""

import json
import asyncio
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from clients.welink import get_history_messages
from core.database import get_db

router = APIRouter(prefix="/api/new-messages", tags=["new-messages"])


@router.get("")
async def new_messages(interval: int = Query(default=5000, ge=2000)):
    """Stream new messages via SSE."""
    async def event_stream():
        db = get_db()
        # Get all conversations
        convs = db.execute("SELECT * FROM conversations").fetchall()

        while True:
            new_items = []
            for conv in convs:
                c = dict(conv)
                is_group = c["type"] == "group"
                target = c["group_id"] if is_group else c["target_account"]
                if not target:
                    continue

                try:
                    result = await get_history_messages(
                        target=target, count=5, direction=1, is_group=is_group
                    )
                    messages = result.get("respData", {}).get("chatInfo", [])
                    for m in messages:
                        # Check if already stored
                        existing = db.execute(
                            "SELECT 1 FROM messages WHERE conversation_id = ? AND msg_id = ?",
                            (c["conversation_id"], m["msgId"]),
                        ).fetchone()
                        if not existing:
                            new_items.append({
                                "conversation_id": c["conversation_id"],
                                "conversation_name": c["name"],
                                "sender": m.get("sender", ""),
                                "content": (m.get("content", "") or "")[:200],
                                "time": m.get("serverSendTime", 0),
                            })
                except Exception:
                    pass

            if new_items:
                yield f"data: {json.dumps({'type': 'messages', 'count': len(new_items), 'items': new_items}, ensure_ascii=False)}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

            await asyncio.sleep(interval / 1000)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
