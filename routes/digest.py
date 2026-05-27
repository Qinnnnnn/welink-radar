"""Daily digest API routes."""

from fastapi import APIRouter, Query
from services.daily_digest import build_daily_digest, get_unclosed_items, _collect_all_messages, _run_ai_analysis, _today_utc, _ts_to_time

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("")
async def api_digest(date: str = Query(default="", description="YYYY-MM-DD, default today UTC")):
    """Return the full daily digest."""
    d = date or None
    return await build_daily_digest(d)


@router.get("/overview")
async def api_overview(date: str = Query(default="", description="YYYY-MM-DD, default today UTC")):
    """Return fast overview + attention (no AI)."""
    d = date or _today_utc()
    collected = await _collect_all_messages(d)
    strong = collected["strong_mentions"]
    weak = collected["weak_mentions"]

    def _fmt(m):
        return {
            "content": m.get("content", ""),
            "sender": m.get("sender", ""),
            "conv_name": m.get("_conv_name", ""),
            "conv_type": m.get("_conv_type", ""),
            "time": _ts_to_time(m.get("serverSendTime", 0)),
            "msg_id": m.get("msgId", 0),
        }

    return {
        "date": d,
        "overview": {
            "group_chats": len(collected["groups"]),
            "private_chats": len(collected["privates"]),
            "total_messages": len(collected["all_messages"]),
            "attention_count": len(strong) + len(weak),
            "strong_count": len(strong),
            "weak_count": len(weak),
        },
        "attention": {
            "strong": [_fmt(m) for m in strong],
            "weak": [_fmt(m) for m in weak],
        },
    }


@router.get("/analysis")
async def api_analysis(date: str = Query(default="", description="YYYY-MM-DD, default today UTC")):
    """Return AI analysis only (topics, unclosed, closed)."""
    d = date or _today_utc()
    collected = await _collect_all_messages(d)
    return await _run_ai_analysis(collected)


@router.get("/unclosed")
async def api_unclosed(date: str = Query(default="", description="YYYY-MM-DD, default today UTC")):
    """Return only the unclosed items."""
    d = date or None
    return await get_unclosed_items(d)
