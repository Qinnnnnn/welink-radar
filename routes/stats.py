"""Dashboard stats route."""

import time
from fastapi import APIRouter, Query
from core.database import get_db
from services.dashboard_intelligence import build_dashboard_intelligence
from services.message_store import list_cached_stats_range
from services.mention_index import count_mentions_between
from services.group_classifier import effective_group_ids
from core.config import read_config

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_stats(
    range: str = Query(default="week"),
    date: str = Query(default=""),
):
    """Return dashboard analytics for a date range."""
    from datetime import datetime, timezone, timedelta

    # Determine date window
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    anchor = date or today

    if range == "day":
        since = until = anchor
        days = 1
    elif range == "week":
        since = (datetime.strptime(anchor, "%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d")
        until = anchor
        days = 7
    elif range == "month":
        since = (datetime.strptime(anchor, "%Y-%m-%d") - timedelta(days=29)).strftime("%Y-%m-%d")
        until = anchor
        days = 30
    else:
        since = (datetime.strptime(anchor, "%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d")
        until = anchor
        days = 7

    db = get_db()

    # Stats for the range
    stats = list_cached_stats_range(since, until)

    # Trend data
    trend = []
    total_messages = 0
    active_groups_set = set()
    for s in stats:
        if s["date"] >= since and s["date"] <= until:
            trend.append({"date": s["date"], "total": s["total"]})
            total_messages += s["total"]
            active_groups_set.add(s["conversation_id"])

    trend.sort(key=lambda x: x["date"])

    # Peak and average
    trend_values = [t["total"] for t in trend]
    peak = max(trend, key=lambda t: t["total"]) if trend else {"date": "", "total": 0}
    avg = sum(trend_values) / len(trend_values) if trend_values else 0.0

    # Total conversations in DB
    total_convs = db.execute("SELECT COUNT(*) as cnt FROM conversations").fetchone()["cnt"]
    silent_groups = max(0, total_convs - len(active_groups_set))

    # Mentions count
    import datetime as dt_mod
    since_ts = int(dt_mod.datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    until_ts = int(dt_mod.datetime.strptime(until, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400
    total_mentions = count_mentions_between(since_ts, until_ts)

    # Category stats
    groups = db.execute("SELECT * FROM groups ORDER BY sort_order").fetchall()
    tag_counts = {}
    for g in groups:
        tag_counts[g["name"]] = db.execute(
            "SELECT COUNT(DISTINCT conversation_id) as cnt FROM group_tags WHERE group_id = ?",
            (g["id"],),
        ).fetchone()["cnt"]

    categories = [
        {"name": g["name"], "color": g["color"], "emoji": g["emoji"], "count": tag_counts.get(g["name"], 0)}
        for g in groups
    ]

    # Intelligence
    intelligence = build_dashboard_intelligence(anchor)

    # Sidebar groups
    sidebar_groups = [
        {"id": g["id"], "name": g["name"], "color": g["color"], "emoji": g["emoji"]}
        for g in groups
    ]

    return {
        "range": range,
        "date": anchor,
        "days": days,
        "active_groups": len(active_groups_set),
        "total_messages": total_messages,
        "total_mentions": total_mentions,
        "silent_groups": silent_groups,
        "trend": trend,
        "trend_peak": peak,
        "trend_avg": round(avg, 1),
        "categories": categories,
        "intelligence": intelligence,
        "sidebar_groups": sidebar_groups,
    }
