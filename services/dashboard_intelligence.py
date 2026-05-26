"""Dashboard intelligence service.

Generates heuristic intelligence signals from messages, links, and stats.
Mimics WeChat Radar's dashboard-intelligence.ts with regex-based scoring.
"""

import json
from datetime import datetime, timezone, timedelta
from core.database import get_db

# ── Heuristic patterns ────────────────────────────────────────────────────────

TOOL_KEYWORDS = ["工具", "平台", "系统", "部署", "发布", "上线", "优化", "加速"]
OPPORTUNITY_KEYWORDS = ["机会", "需求", "痛点", "问题", "求助", "帮忙", "谁有", "有没有"]
ACTION_KEYWORDS = ["@所有人", "请查收", "请回复", "截止", "DDL", "deadline", "务必", "尽快"]
QUESTION_PATTERNS = ["怎么", "如何", "什么", "？", "?"]


def build_dashboard_intelligence(date: str) -> dict:
    """Build a comprehensive intelligence summary for the dashboard.

    Returns signals across multiple categories:
    - must_read: high-priority items
    - opportunities: potential action items
    - signal_sources: who's talking about what
    - action_items: things requiring response
    - people_radar: top contributors
    - anomalies: unusual activity
    """
    db = get_db()
    since = date
    until = date

    # ── Load data ─────────────────────────────────────────────────────────
    messages = db.execute(
        """SELECT m.*, c.name as conversation_name
           FROM messages m
           LEFT JOIN conversations c ON m.conversation_id = c.conversation_id
           WHERE m.date = ?
           ORDER BY m.timestamp DESC
           LIMIT 500""",
        (date,),
    ).fetchall()

    links = db.execute(
        "SELECT * FROM message_links WHERE date = ? ORDER BY timestamp DESC LIMIT 200",
        (date,),
    ).fetchall()

    stats = db.execute(
        "SELECT * FROM daily_stats WHERE date = ?", (date,),
    ).fetchall()

    if not messages and not links:
        return {
            "date": date,
            "must_read": [],
            "opportunities": [],
            "signal_sources": [],
            "action_items": [],
            "people_radar": [],
            "anomalies": [],
            "summary": "暂无数据",
        }

    msg_list = [dict(r) for r in messages]
    link_list = [dict(r) for r in links]
    stat_list = [dict(r) for r in stats]

    # ── Must-read items ───────────────────────────────────────────────────
    must_read = _extract_must_read(msg_list, link_list)

    # ── Opportunities ─────────────────────────────────────────────────────
    opportunities = _extract_opportunities(msg_list)

    # ── Signal sources ────────────────────────────────────────────────────
    signal_sources = _extract_signal_sources(msg_list, stat_list)

    # ── Action items ──────────────────────────────────────────────────────
    action_items = _extract_action_items(msg_list)

    # ── People radar ──────────────────────────────────────────────────────
    people_radar = _extract_people_radar(msg_list, stat_list)

    # ── Anomalies ─────────────────────────────────────────────────────────
    anomalies = _detect_anomalies(msg_list, stat_list)

    return {
        "date": date,
        "must_read": must_read,
        "opportunities": opportunities,
        "signal_sources": signal_sources,
        "action_items": action_items,
        "people_radar": people_radar,
        "anomalies": anomalies,
        "summary": f"{len(msg_list)} 条消息, {len(link_list)} 个链接, {len(stat_list)} 个活跃群",
    }


def _extract_must_read(messages: list[dict], links: list[dict]) -> list[dict]:
    """Extract high-priority must-read items."""
    items = []

    # Messages with @all or high-importance keywords
    for m in messages:
        content = m.get("content", "")
        if m.get("is_at"):
            items.append({
                "type": "mention",
                "source": m.get("conversation_name", m["conversation_id"]),
                "sender": m["sender"],
                "content": content[:200],
                "time": m["send_time"],
            })

    # Links with high share count
    for l in links[:10]:
        items.append({
            "type": "link",
            "source": l["domain"],
            "title": l.get("title") or l["url"][:80],
            "url": l["url"],
        })

    return items[:10]


def _extract_opportunities(messages: list[dict]) -> list[dict]:
    """Extract potential opportunity signals."""
    opportunities = []
    for m in messages:
        content = m.get("content", "")
        if any(kw in content for kw in OPPORTUNITY_KEYWORDS):
            opportunities.append({
                "source": m.get("conversation_name", m["conversation_id"]),
                "sender": m["sender"],
                "content": content[:200],
                "keywords": [kw for kw in OPPORTUNITY_KEYWORDS if kw in content],
                "time": m["send_time"],
            })
    return opportunities[:10]


def _extract_signal_sources(messages: list[dict], stats: list[dict]) -> list[dict]:
    """Identify key signal sources (people/groups generating discussion)."""
    # Top conversations by message volume
    group_volume = {}
    for m in messages:
        cid = m["conversation_id"]
        name = m.get("conversation_name", cid)
        group_volume[name] = group_volume.get(name, 0) + 1

    return sorted(
        [{"name": k, "count": v} for k, v in group_volume.items()],
        key=lambda x: x["count"], reverse=True,
    )[:5]


def _extract_action_items(messages: list[dict]) -> list[dict]:
    """Extract items requiring action."""
    items = []
    for m in messages:
        content = m.get("content", "")
        if any(kw in content for kw in ACTION_KEYWORDS):
            items.append({
                "source": m.get("conversation_name", m["conversation_id"]),
                "content": content[:200],
                "trigger": [kw for kw in ACTION_KEYWORDS if kw in content][0],
                "time": m["send_time"],
            })
    return items[:10]


def _extract_people_radar(messages: list[dict], stats: list[dict]) -> list[dict]:
    """Identify the most active people."""
    sender_counts: dict[str, int] = {}
    sender_groups: dict[str, set] = {}

    for m in messages:
        s = m["sender"]
        sender_counts[s] = sender_counts.get(s, 0) + 1
        if s not in sender_groups:
            sender_groups[s] = set()
        sender_groups[s].add(m["conversation_id"])

    top = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return [
        {"sender": s, "message_count": c, "group_count": len(sender_groups.get(s, set()))}
        for s, c in top
    ]


def _detect_anomalies(messages: list[dict], stats: list[dict]) -> list[dict]:
    """Detect anomalous patterns."""
    anomalies = []

    # Check for groups with unusually high volume
    if stats:
        volumes = [s["total"] for s in stats]
        if volumes:
            avg_vol = sum(volumes) / len(volumes)
            for s in stats:
                if s["total"] > avg_vol * 3 and s["total"] > 20:
                    anomalies.append({
                        "type": "volume_spike",
                        "source": s["conversation_id"],
                        "detail": f"消息量 {s['total']}, 平均 {avg_vol:.0f}",
                    })

    # Check for tool/solution discussions
    tool_msgs = [m for m in messages if any(kw in (m.get("content") or "") for kw in TOOL_KEYWORDS)]
    if len(tool_msgs) > 5:
        anomalies.append({
            "type": "tool_discussion",
            "source": "多群",
            "detail": f"涉及工具/平台的讨论 {len(tool_msgs)} 条",
        })

    return anomalies[:5]
