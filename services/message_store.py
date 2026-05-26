"""Message persistence and daily stats aggregation."""

import json
import time
from datetime import datetime, timezone
from core.database import get_db


def date_of_message(server_send_time_ms: int) -> str:
    """Convert serverSendTime (Unix ms) to YYYY-MM-DD."""
    return datetime.fromtimestamp(server_send_time_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def send_time_of_message(server_send_time_ms: int) -> str:
    """Convert serverSendTime (Unix ms) to YYYY-MM-DD HH:MM:SS."""
    return datetime.fromtimestamp(server_send_time_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def bulk_insert_messages(conversation_id: str, messages: list[dict]) -> int:
    """Insert a batch of messages from welink-cli output. Returns count inserted.

    Skips system messages and revoke notices.
    """
    db = get_db()
    inserted = 0

    rows = []
    for m in messages:
        content = m.get("content", "")
        content_type = m.get("contentType", "TEXT_MSG")

        # Skip system messages
        if content_type in ("SYSTEM_MSG", "NOTIFY_MSG"):
            continue

        msg_id = m["msgId"]
        sender = m.get("sender", "")
        receiver = m.get("receiver", "")
        server_send_time = m.get("serverSendTime", 0)
        is_at = 1 if m.get("at", False) else 0
        at_accounts = json.dumps(m.get("atAccountList", []), ensure_ascii=False) if m.get("atAccountList") else None
        s_time = send_time_of_message(server_send_time)
        ts = int(server_send_time / 1000)
        date_str = date_of_message(server_send_time)

        rows.append((conversation_id, msg_id, sender, receiver, content, content_type,
                      is_at, at_accounts, s_time, ts, date_str))

    for row in rows:
        try:
            cur = db.execute(
                """INSERT OR IGNORE INTO messages
                   (conversation_id, msg_id, sender, receiver, content, content_type,
                    is_at, at_accounts, send_time, timestamp, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                row,
            )
            if cur.rowcount > 0:
                inserted += 1
        except Exception:
            pass

    db.commit()
    return inserted


def list_messages_for_date(conversation_id: str, date: str, limit: int = 1000) -> list[dict]:
    """List messages for a conversation on a given date."""
    db = get_db()
    rows = db.execute(
        """SELECT * FROM messages
           WHERE conversation_id = ? AND date = ?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (conversation_id, date, min(limit, 5000)),
    ).fetchall()
    return [dict(r) for r in rows]


def list_messages_for_period(conversation_id: str, since: str, until: str, limit: int = 5000) -> list[dict]:
    """List messages in a date range."""
    db = get_db()
    rows = db.execute(
        """SELECT * FROM messages
           WHERE conversation_id = ? AND date >= ? AND date <= ?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (conversation_id, since, until, min(limit, 10000)),
    ).fetchall()
    return [dict(r) for r in rows]


def aggregate_daily_stats(conversation_id: str, dates: list[str]) -> list[dict]:
    """Compute daily stats (total, hourly distribution, top senders) for given dates.

    Returns list of dicts ready for insertion into daily_stats table.
    """
    db = get_db()
    results = []
    now = int(time.time())

    for date in dates:
        rows = db.execute(
            """SELECT sender, timestamp FROM messages
               WHERE conversation_id = ? AND date = ?""",
            (conversation_id, date),
        ).fetchall()

        if not rows:
            continue

        total = len(rows)

        # Hourly distribution (24 buckets)
        by_hour = [0] * 24
        for r in rows:
            hour = datetime.fromtimestamp(r["timestamp"], tz=timezone.utc).hour
            by_hour[hour] += 1

        # Top senders (top 10)
        sender_counts: dict[str, int] = {}
        for r in rows:
            sender_counts[r["sender"]] = sender_counts.get(r["sender"], 0) + 1
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_senders_json = json.dumps(
            [{"sender": s, "count": c} for s, c in top_senders],
            ensure_ascii=False,
        )

        results.append({
            "conversation_id": conversation_id,
            "date": date,
            "total": total,
            "top_senders": top_senders_json,
            "by_hour": json.dumps(by_hour),
            "refreshed_at": now,
        })

    return results


def save_daily_stats(stats: list[dict]) -> int:
    """Persist daily stats rows. Returns count saved."""
    db = get_db()
    count = 0
    for s in stats:
        db.execute(
            """INSERT OR REPLACE INTO daily_stats
               (conversation_id, date, total, top_senders, by_hour, refreshed_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (s["conversation_id"], s["date"], s["total"],
             s["top_senders"], s["by_hour"], s["refreshed_at"]),
        )
        count += 1
    db.commit()
    return count


def get_cached_stats(conversation_id: str, date: str) -> dict | None:
    """Get cached daily stats for a single conversation+date."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM daily_stats WHERE conversation_id = ? AND date = ?",
        (conversation_id, date),
    ).fetchone()
    return dict(row) if row else None


def list_cached_stats_for_date(date: str) -> list[dict]:
    """Get all cached stats for a given date across all conversations."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM daily_stats WHERE date = ?",
        (date,),
    ).fetchall()
    return [dict(r) for r in rows]


def list_cached_stats_range(since: str, until: str) -> list[dict]:
    """Get cached stats for a date range."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM daily_stats WHERE date >= ? AND date <= ?",
        (since, until),
    ).fetchall()
    return [dict(r) for r in rows]


# ── Sync state ────────────────────────────────────────────────────────────────


def get_sync_state(conversation_id: str) -> dict | None:
    """Get sync state for a conversation."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM sync_state WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    return dict(row) if row else None


def upsert_sync_state(conversation_id: str, total: int, first_date: str | None = None,
                       last_date: str | None = None, last_msg_id: int = 0,
                       status: str = "ok", error: str | None = None) -> None:
    """Create or update sync state for a conversation."""
    db = get_db()
    now = int(time.time())
    existing = get_sync_state(conversation_id)
    if existing:
        db.execute(
            """UPDATE sync_state SET last_synced_at = ?, total_messages = ?,
               first_message_date = COALESCE(?, first_message_date),
               last_message_date = COALESCE(?, last_message_date),
               last_msg_id = MAX(?, last_msg_id),
               status = ?, last_error = ?
               WHERE conversation_id = ?""",
            (now, total, first_date, last_date, last_msg_id, status, error, conversation_id),
        )
    else:
        db.execute(
            """INSERT INTO sync_state
               (conversation_id, last_synced_at, last_msg_id, first_message_date,
                last_message_date, total_messages, status, last_error)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (conversation_id, now, last_msg_id, first_date, last_date, total, status, error),
        )
    db.commit()


def list_all_synced_dates(conversation_id: str) -> list[str]:
    """List all dates that have messages for a conversation."""
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT date FROM messages WHERE conversation_id = ? ORDER BY date ASC",
        (conversation_id,),
    ).fetchall()
    return [r["date"] for r in rows]


def count_messages_in_range(conversation_id: str, since: str, until: str) -> int:
    """Count messages in a date range."""
    db = get_db()
    row = db.execute(
        """SELECT COUNT(*) as cnt FROM messages
           WHERE conversation_id = ? AND date >= ? AND date <= ?""",
        (conversation_id, since, until),
    ).fetchone()
    return row["cnt"] if row else 0
