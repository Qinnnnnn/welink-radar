"""Daily digest service.

Orchestrates message collection from welink-cli, computes overview stats,
extracts @mentions (strong/weak), and invokes nga for AI-powered topic
detection and unclosed-item tracking.

All welink-cli / nga calls go through the client modules — flip
_MOCK_ENABLED = False in each client to switch to real CLI.
"""

import json
import asyncio
from datetime import datetime, timezone
from typing import Any

from clients.welink import get_sessions, get_history_messages
from clients.nga import run_prompt

# ── Constants ──────────────────────────────────────────────────────────────────

_MY_ACCOUNT = "q00510847"  # Current user's welink account

# ── Helpers ────────────────────────────────────────────────────────────────────


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _ts_to_time(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%H:%M")


# ── Message collection ─────────────────────────────────────────────────────────


async def _collect_all_messages(date: str) -> dict[str, Any]:
    """Fetch sessions and all messages for the given date.

    Returns:
        {
            "groups": [...],
            "privates": [...],
            "all_messages": [...],
            "strong_mentions": [...],
            "weak_mentions": [...],
        }
    """
    sessions_resp = await get_sessions(limit=50)
    conversations = sessions_resp.get("conversation_info", [])

    groups: list[dict] = []
    privates: list[dict] = []

    for conv in conversations:
        if conv["recent_conversation_type"] == "CHAT_TYPE_GROUP_MSG":
            groups.append(conv)
        else:
            privates.append(conv)

    all_messages: list[dict] = []
    strong_mentions: list[dict] = []
    weak_mentions: list[dict] = []

    async def _fetch_group(g: dict) -> None:
        gid = g["group_id"]
        try:
            resp = await get_history_messages(gid, count=30, is_group=True)
            msgs = resp.get("respData", {}).get("chatInfo", [])
            for m in msgs:
                m["_conv_name"] = g.get("group_name", gid)
                m["_conv_type"] = "group"
                m["_conv_id"] = gid
                all_messages.append(m)

                content = m.get("content", "")
                if m.get("at"):
                    at_list = m.get("atAccountList") or []
                    if _MY_ACCOUNT in at_list:
                        strong_mentions.append(m)
                    elif "@所有人" in content or "@all" in content.lower():
                        weak_mentions.append(m)
        except Exception:
            pass

    async def _fetch_private(p: dict) -> None:
        target = p.get("target_account")
        if not target:
            return
        try:
            resp = await get_history_messages(target, count=20, is_group=False)
            msgs = resp.get("respData", {}).get("chatInfo", [])
            for m in msgs:
                m["_conv_name"] = p.get("native_name", target)
                m["_conv_type"] = "private"
                m["_conv_id"] = target
                all_messages.append(m)
        except Exception:
            pass

    # Fetch all conversations concurrently
    tasks = [_fetch_group(g) for g in groups] + [_fetch_private(p) for p in privates]
    await asyncio.gather(*tasks)

    # Sort messages by time (newest first)
    all_messages.sort(key=lambda m: m.get("serverSendTime", 0), reverse=True)
    strong_mentions.sort(key=lambda m: m.get("serverSendTime", 0), reverse=True)
    weak_mentions.sort(key=lambda m: m.get("serverSendTime", 0), reverse=True)

    return {
        "groups": groups,
        "privates": privates,
        "all_messages": all_messages,
        "strong_mentions": strong_mentions,
        "weak_mentions": weak_mentions,
    }


# ── AI Analysis ────────────────────────────────────────────────────────────────


def _build_digest_prompt(collected: dict) -> str:
    """Build a prompt for nga to analyse today's messages."""
    groups = collected["groups"]
    privates = collected["privates"]
    all_msgs = collected["all_messages"]

    # Format a message log
    lines: list[str] = []
    lines.append("以下是今日 WeLink 消息记录，请分析并输出 JSON。\n")
    lines.append("--- 会话列表 ---")
    for g in groups:
        lines.append(f"群聊: {g['group_name']} (id={g['group_id']})")
    for p in privates:
        lines.append(f"私聊: {p.get('native_name', '')} (account={p.get('target_account', '')})")

    lines.append("\n--- 消息记录（时间倒序）---")
    for m in all_msgs:
        t = _ts_to_time(m.get("serverSendTime", 0))
        sender = m.get("sender", "?")
        conv = m.get("_conv_name", "?")
        content = m.get("content", "")
        at_mark = ""
        if m.get("at"):
            if _MY_ACCOUNT in (m.get("atAccountList") or []):
                at_mark = " [@ME]"
            elif "@所有人" in content:
                at_mark = " [@ALL]"
        lines.append(f"[{t}] {conv} | {sender}{at_mark}: {content}")

    lines.append("\n--- 分析要求 ---")
    lines.append("""请分析以上消息，输出严格 JSON（不要 markdown 代码块包裹）：
{
  "topics": [
    {"title": "话题标题", "summary": "30字内摘要", "group_count": 涉及群数, "message_count": 涉及消息数}
  ],
  "unclosed": [
    {"title": "事项", "reason": "提问无人回复/承诺未兑现/决策未定", "source_group": "来源", "key_person": "关键人", "risk": "高/中/低", "detail": "一句话描述"}
  ],
  "closed": [
    {"title": "事项", "conclusion": "结论", "source_group": "来源"}
  ]
}

未闭环判断标准：
- 提问后无人回复（消息以？/吗/呢结尾，后续无应答）
- 承诺类语句未确认完成（"我来""稍后""今晚发""明天前""会跟进"）
- 决策征求无结论（"大家看下""有没有意见""定一下""谁有空"）
- @某人后该人未回复（at=true 且后续无该人消息）
- 多人追问同一事项但无明确结论

请确保 unclosed 按 risk 高→中→低排序，topics 按 message_count 降序。""")

    return "\n".join(lines)


async def _run_ai_analysis(collected: dict) -> dict:
    """Run the LLM analysis and return parsed JSON."""
    prompt = _build_digest_prompt(collected)
    try:
        raw = await run_prompt(prompt)
        # Strip possible markdown code fences
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        return json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        return {
            "topics": [],
            "unclosed": [],
            "closed": [],
            "_error": str(e),
        }


# ── Public API ─────────────────────────────────────────────────────────────────


async def build_daily_digest(date: str | None = None) -> dict:
    """Build a complete daily digest.

    Args:
        date: YYYY-MM-DD (default: today UTC)

    Returns:
        {
            "date": "2026-05-08",
            "overview": {
                "group_chats": 8,
                "private_chats": 5,
                "total_messages": 72,
                "attention_count": 5,
                "strong_count": 2,
                "weak_count": 3,
            },
            "attention": {
                "strong": [...],
                "weak": [...],
            },
            "ai_analysis": {
                "topics": [...],
                "unclosed": [...],
                "closed": [...],
            },
        }
    """
    date = date or _today_utc()

    # 1. Collect all messages
    collected = await _collect_all_messages(date)

    # 2. Compute overview stats
    strong = collected["strong_mentions"]
    weak = collected["weak_mentions"]

    overview = {
        "group_chats": len(collected["groups"]),
        "private_chats": len(collected["privates"]),
        "total_messages": len(collected["all_messages"]),
        "attention_count": len(strong) + len(weak),
        "strong_count": len(strong),
        "weak_count": len(weak),
    }

    # 3. Format attention items for display
    def _fmt_mention(m: dict) -> dict:
        return {
            "content": m.get("content", ""),
            "sender": m.get("sender", ""),
            "conv_name": m.get("_conv_name", ""),
            "conv_type": m.get("_conv_type", ""),
            "time": _ts_to_time(m.get("serverSendTime", 0)),
            "msg_id": m.get("msgId", 0),
        }

    attention = {
        "strong": [_fmt_mention(m) for m in strong],
        "weak": [_fmt_mention(m) for m in weak],
    }

    # 4. Run AI analysis (in background — we can still return partial results)
    ai_analysis = await _run_ai_analysis(collected)

    return {
        "date": date,
        "overview": overview,
        "attention": attention,
        "ai_analysis": ai_analysis,
    }


async def get_unclosed_items(date: str | None = None) -> list[dict]:
    """Return only the unclosed items for a given date."""
    digest = await build_daily_digest(date)
    return digest.get("ai_analysis", {}).get("unclosed", [])
