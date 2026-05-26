"""Topic aggregation service.

Uses nga (AI CLI) to extract discussion topics from daily messages.
"""

import json
import logging
import time
from core.database import get_db
from clients.nga import run_prompt
from clients.welink import get_sessions

logger = logging.getLogger(__name__)

TOPIC_BUILD_PROMPT = """你是一个群聊分析师。请分析以下来自多个 WeLink 群的消息，提取出 3-8 个主要讨论话题。

对每个话题，输出:
- title: 简洁的话题标题（10字以内）
- summary: 话题摘要（30-50字，说明讨论了什么）
- message_count: 涉及该话题的消息数（估算）
- group_count: 涉及该话题的群数量（估算）

严格按照以下 JSON 格式输出（只输出 JSON，不要其他文字）：
[
  {"title": "话题标题", "summary": "话题摘要", "message_count": 5, "group_count": 2},
  ...
]

以下是消息列表（格式：[群名] 发送者: 内容）：
"""


async def build_topics_for_date(date: str, on_progress=None) -> dict:
    """Build topics for a given date using AI.

    Loads messages, chunks them, sends to nga, merges results.
    """
    db = get_db()

    # Load candidate messages
    rows = db.execute(
        """SELECT m.*, c.name as conversation_name
           FROM messages m
           LEFT JOIN conversations c ON m.conversation_id = c.conversation_id
           WHERE m.date = ?
           ORDER BY m.timestamp DESC
           LIMIT 500""",
        (date,),
    ).fetchall()

    if not rows:
        return {"date": date, "topics": [], "message": "No messages found for this date"}

    # Format messages for the prompt
    messages_text = []
    seen = set()
    for r in rows:
        content = r["content"]
        # Deduplicate nearly identical messages
        key = content[:50]
        if key in seen:
            continue
        seen.add(key)
        name = r["conversation_name"] or r["conversation_id"]
        sender = r["sender"]
        messages_text.append(f"[{name}] {sender}: {content}")

    # Truncate to manageable size (~100 messages)
    if len(messages_text) > 100:
        messages_text = messages_text[:100]

    prompt = TOPIC_BUILD_PROMPT + "\n".join(messages_text)

    if on_progress:
        await on_progress({"phase": "calling_ai", "message_count": len(messages_text)})

    # Call nga
    try:
        raw_response = await run_prompt(prompt)
        topics_data = _parse_topics_json(raw_response)
    except Exception as e:
        logger.error(f"AI topic building failed: {e}")
        # Fallback: create a single topic from all messages
        topics_data = [{
            "title": f"{date} 群聊汇总",
            "summary": f"当日共 {len(messages_text)} 条有效消息",
            "message_count": len(messages_text),
            "group_count": len(set(r["conversation_id"] for r in rows)),
        }]

    if on_progress:
        await on_progress({"phase": "saving", "topic_count": len(topics_data)})

    # Persist topics
    _save_topics(date, topics_data, rows)

    return {"date": date, "topics": topics_data, "raw_message_count": len(rows)}


def _parse_topics_json(raw: str) -> list[dict]:
    """Parse the AI response as JSON, with fallback."""
    # Try to find JSON array in the response
    text = raw.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else text

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try to extract JSON array using regex
    import re
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Fallback
    return [{"title": "群聊摘要", "summary": text[:100], "message_count": 0, "group_count": 0}]


def _save_topics(date: str, topics_data: list[dict], messages: list) -> None:
    """Save topics and topic-message associations to DB."""
    db = get_db()
    now = int(time.time())

    # Clear existing topics for this date
    db.execute("DELETE FROM topic_messages WHERE topic_id IN (SELECT id FROM topics WHERE date = ?)", (date,))
    db.execute("DELETE FROM topics WHERE date = ?", (date,))

    for td in topics_data[:30]:  # Max 30 topics
        cursor = db.execute(
            """INSERT INTO topics (date, title, summary, message_count, group_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (date, td["title"], td.get("summary", ""),
             td.get("message_count", 0), td.get("group_count", 0), now),
        )
        topic_id = cursor.lastrowid

        # Associate messages (simple: assign somewhat arbitrarily based on keywords)
        title_words = set(td["title"].lower())
        assigned = 0
        for m in messages:
            if assigned >= 10:
                break
            content = (m["content"] or "").lower()
            # Simple keyword match
            if any(w in content for w in title_words if len(w) >= 2):
                db.execute(
                    """INSERT OR IGNORE INTO topic_messages (topic_id, conversation_id, msg_id, score)
                       VALUES (?, ?, ?, 0.5)""",
                    (topic_id, m["conversation_id"], m["msg_id"]),
                )
                assigned += 1

    db.commit()


def list_topics(date: str) -> list[dict]:
    """List topics for a date."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM topics WHERE date = ? ORDER BY message_count DESC",
        (date,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_topic_detail(topic_id: int) -> dict | None:
    """Get a topic with its associated messages."""
    db = get_db()
    topic = db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if not topic:
        return None

    topic_dict = dict(topic)

    # Get associated messages
    msg_rows = db.execute(
        """SELECT m.*, c.name as conversation_name
           FROM topic_messages tm
           JOIN messages m ON tm.conversation_id = m.conversation_id AND tm.msg_id = m.msg_id
           LEFT JOIN conversations c ON m.conversation_id = c.conversation_id
           WHERE tm.topic_id = ?
           ORDER BY m.timestamp DESC
           LIMIT 50""",
        (topic_id,),
    ).fetchall()

    topic_dict["messages"] = [dict(r) for r in msg_rows]
    return topic_dict
