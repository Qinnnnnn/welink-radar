"""Link intelligence service.

Aggregates links from message_links per date, classifies articles vs tools,
and optionally enriches titles via AI.
"""

import json
import logging
import time
from core.database import get_db
from core.config import read_config

logger = logging.getLogger(__name__)


async def get_daily_link_intelligence(date: str, refresh: bool = False) -> dict:
    """Get aggregated link intelligence for a date.

    Returns articles, tools, and raw links grouped by canonical URL.
    """
    db = get_db()

    # Check cache first (unless refreshing)
    if not refresh:
        cache_row = db.execute(
            """SELECT payload FROM link_intelligence_cache
               WHERE date = ? AND version = 'v1'
               ORDER BY generated_at DESC LIMIT 1""",
            (date,),
        ).fetchone()
        if cache_row:
            try:
                return json.loads(cache_row["payload"])
            except json.JSONDecodeError:
                pass

    # Build fresh intelligence
    rows = db.execute(
        """SELECT * FROM message_links WHERE date = ? ORDER BY timestamp DESC""",
        (date,),
    ).fetchall()

    if not rows:
        result = {"date": date, "articles": [], "tools": [], "raw": []}
        _cache_result(date, result)
        return result

    # Aggregate by canonical_url
    aggregated: dict[str, dict] = {}
    for r in rows:
        row = dict(r)
        canonical = row["canonical_url"]
        if canonical not in aggregated:
            aggregated[canonical] = {
                "canonical_url": canonical,
                "title": row.get("title"),
                "description": row.get("description"),
                "domain": row["domain"],
                "source": row.get("raw_kind", "unknown"),
                "count": 0,
                "group_count": 0,
                "last_seen": row["send_time"],
                "groups": set(),
                "sample_content": None,
            }
        agg = aggregated[canonical]
        agg["count"] += 1
        agg["groups"].add(row["conversation_id"])
        if not agg["sample_content"]:
            agg["sample_content"] = row.get("url", "")

    # Convert sets and split by category
    articles = []
    tools = []
    raw = []
    for item in aggregated.values():
        entry = {
            "canonical_url": item["canonical_url"],
            "title": item["title"],
            "description": item["description"],
            "domain": item["domain"],
            "source": item["source"],
            "count": item["count"],
            "group_count": len(item["groups"]),
            "last_seen": item["last_seen"],
            "sample_content": item["sample_content"],
        }
        if item["source"] == "article":
            articles.append(entry)
        elif item["source"] == "tool":
            tools.append(entry)
        else:
            raw.append(entry)

    # Sort by count descending
    articles.sort(key=lambda x: x["count"], reverse=True)
    tools.sort(key=lambda x: x["count"], reverse=True)
    raw.sort(key=lambda x: x["count"], reverse=True)

    result = {"date": date, "articles": articles, "tools": tools, "raw": raw}
    _cache_result(date, result)
    return result


def clear_daily_link_intelligence(date: str) -> None:
    """Clear cached link intelligence for a date."""
    db = get_db()
    db.execute("DELETE FROM link_intelligence_cache WHERE date = ?", (date,))
    db.commit()


def _cache_result(date: str, result: dict) -> None:
    """Cache link intelligence result."""
    db = get_db()
    now = int(time.time())
    db.execute(
        """INSERT OR REPLACE INTO link_intelligence_cache (date, version, payload, generated_at)
           VALUES (?, 'v1', ?, ?)""",
        (date, json.dumps(result, ensure_ascii=False), now),
    )
    db.commit()
