"""@Mention tracking service.

Uses welink-cli's structured `at` field (at=true + atAccountList) as primary source.
Also scans myNicknames in content as secondary source for CARD_MSG nested mentions.
"""

import json
import logging
from core.database import get_db
from core.config import read_config

logger = logging.getLogger(__name__)


def scan_mentions_for_message(conversation_id: str, message: dict) -> bool:
    """Check if a message mentions the current user and index it.

    Returns True if a mention was detected and stored.
    """
    # Primary: structured @mention from welink-cli
    is_at = message.get("at", False)
    at_accounts = message.get("atAccountList", [])
    content = message.get("content", "")
    content_type = message.get("contentType", "TEXT_MSG")

    # If structured @mention is present, store it
    if is_at:
        return _store_mention(conversation_id, message)

    # Secondary: scan content for myNicknames (especially for CARD_MSG)
    config = read_config()
    nicknames = config.myNicknames
    if nicknames and content:
        for nick in nicknames:
            if nick and nick in content:
                return _store_mention(conversation_id, message)

    return False


def _store_mention(conversation_id: str, message: dict) -> bool:
    """Insert a mention record."""
    db = get_db()
    msg_id = message["msgId"]
    sender = message.get("sender", "")
    content = message.get("content", "")
    server_send_time = message.get("serverSendTime", 0)

    from services.message_store import send_time_of_message
    s_time = send_time_of_message(server_send_time)
    ts = int(server_send_time / 1000)

    try:
        cur = db.execute(
            """INSERT OR IGNORE INTO mentions
               (conversation_id, msg_id, sender, content, send_time, timestamp, seen)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (conversation_id, msg_id, sender, content, s_time, ts),
        )
        db.commit()
        return cur.rowcount > 0
    except Exception as e:
        logger.error(f"Failed to store mention: {e}")
        return False


def rebuild_mention_index() -> dict:
    """Full rebuild of the mention index from stored messages."""
    db = get_db()
    config = read_config()
    nicknames = config.myNicknames

    if not nicknames:
        return {"scanned": 0, "found": 0}

    # Clear existing mentions
    db.execute("DELETE FROM mentions")

    # Find all messages with at=1 or containing nicknames
    found = 0
    scanned = 0

    # Structured mentions
    rows = db.execute(
        "SELECT * FROM messages WHERE is_at = 1"
    ).fetchall()
    for row in rows:
        msg = dict(row)
        msg["msgId"] = msg["msg_id"]
        if _store_mention(msg["conversation_id"], msg):
            found += 1
        scanned += 1

    # Content-based mentions (for CARD_MSG etc.)
    if nicknames:
        for nick in nicknames:
            rows = db.execute(
                "SELECT * FROM messages WHERE content LIKE ? AND is_at = 0",
                (f"%{nick}%",),
            ).fetchall()
            for row in rows:
                msg = dict(row)
                msg["msgId"] = msg["msg_id"]
                if _store_mention(msg["conversation_id"], msg):
                    found += 1
                scanned += 1

    db.commit()
    return {"scanned": scanned, "found": found}


def list_mentions(limit: int = 1000, offset: int = 0) -> list[dict]:
    """List recent @mentions."""
    db = get_db()
    rows = db.execute(
        """SELECT * FROM mentions ORDER BY timestamp DESC LIMIT ? OFFSET ?""",
        (min(limit, 5000), offset),
    ).fetchall()
    return [dict(r) for r in rows]


def count_mentions() -> int:
    """Count total @mentions."""
    db = get_db()
    row = db.execute("SELECT COUNT(*) as cnt FROM mentions").fetchone()
    return row["cnt"] if row else 0


def count_mentions_since(unix_seconds: int) -> int:
    """Count mentions since a Unix timestamp."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM mentions WHERE timestamp >= ?",
        (unix_seconds,),
    ).fetchone()
    return row["cnt"] if row else 0


def count_mentions_between(since_unix: int, until_unix: int) -> int:
    """Count mentions in a time range."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM mentions WHERE timestamp >= ? AND timestamp <= ?",
        (since_unix, until_unix),
    ).fetchone()
    return row["cnt"] if row else 0


def mark_mentions_seen(conversation_id: str | None = None) -> int:
    """Mark mentions as seen. If conversation_id is None, mark all."""
    db = get_db()
    if conversation_id:
        db.execute(
            "UPDATE mentions SET seen = 1 WHERE conversation_id = ? AND seen = 0",
            (conversation_id,),
        )
    else:
        db.execute("UPDATE mentions SET seen = 1 WHERE seen = 0")
    db.commit()
    return db.changes
