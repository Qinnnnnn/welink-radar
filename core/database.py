"""SQLite database initialization, migration, and schema for WeLink Radar.

Uses Python's built-in sqlite3 module. WAL mode + foreign keys enabled.
Database file: ~/.welink-radar/radar.db
"""

import sqlite3
import threading
from pathlib import Path
from core.config import DATA_DIR

DB_PATH = DATA_DIR / "radar.db"

_local = threading.local()

# ── Schema version ────────────────────────────────────────────────────────────

SCHEMA_VERSION = 1

# ── Table DDL ─────────────────────────────────────────────────────────────────

DDL_STATEMENTS = [
    # User-defined group categories (e.g. "AI 商业", "技术架构")
    """
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        color TEXT NOT NULL,
        emoji TEXT,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at INTEGER NOT NULL
    )
    """,

    # Which groups a conversation belongs to
    """
    CREATE TABLE IF NOT EXISTS group_tags (
        conversation_id TEXT NOT NULL,
        group_id INTEGER NOT NULL,
        PRIMARY KEY (conversation_id, group_id),
        FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
    )
    """,

    # Starred/favorite conversations
    """
    CREATE TABLE IF NOT EXISTS favorites (
        conversation_id TEXT PRIMARY KEY,
        starred_at INTEGER NOT NULL
    )
    """,

    # Cached conversation metadata
    """
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        group_id TEXT,
        target_account TEXT,
        staff_name TEXT,
        group_type TEXT,
        cross_instance INTEGER DEFAULT 0,
        updated_at INTEGER NOT NULL
    )
    """,

    # Core message storage
    """
    CREATE TABLE IF NOT EXISTS messages (
        conversation_id TEXT NOT NULL,
        msg_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL DEFAULT '',
        content TEXT NOT NULL,
        content_type TEXT NOT NULL DEFAULT 'TEXT_MSG',
        is_at INTEGER NOT NULL DEFAULT 0,
        at_accounts TEXT,
        send_time TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        date TEXT NOT NULL,
        PRIMARY KEY (conversation_id, msg_id)
    )
    """,

    # Daily aggregated stats per conversation
    """
    CREATE TABLE IF NOT EXISTS daily_stats (
        conversation_id TEXT NOT NULL,
        date TEXT NOT NULL,
        total INTEGER NOT NULL,
        top_senders TEXT NOT NULL,
        by_hour TEXT NOT NULL,
        refreshed_at INTEGER NOT NULL,
        PRIMARY KEY (conversation_id, date)
    )
    """,

    # @Mention index
    """
    CREATE TABLE IF NOT EXISTS mentions (
        conversation_id TEXT NOT NULL,
        msg_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        content TEXT NOT NULL,
        send_time TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        seen INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (conversation_id, msg_id)
    )
    """,

    # Extracted message links (URLs)
    """
    CREATE TABLE IF NOT EXISTS message_links (
        conversation_id TEXT NOT NULL,
        msg_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        sender TEXT NOT NULL,
        send_time TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        url TEXT NOT NULL,
        canonical_url TEXT NOT NULL,
        title TEXT,
        description TEXT,
        domain TEXT NOT NULL,
        source TEXT NOT NULL,
        raw_kind TEXT NOT NULL,
        confidence REAL NOT NULL DEFAULT 1,
        created_at INTEGER NOT NULL,
        PRIMARY KEY (conversation_id, msg_id, canonical_url)
    )
    """,

    # Aggregated topics (AI-generated)
    """
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT,
        message_count INTEGER NOT NULL,
        group_count INTEGER NOT NULL,
        created_at INTEGER NOT NULL
    )
    """,

    # Topic-to-message membership
    """
    CREATE TABLE IF NOT EXISTS topic_messages (
        topic_id INTEGER NOT NULL,
        conversation_id TEXT NOT NULL,
        msg_id INTEGER NOT NULL,
        score REAL NOT NULL DEFAULT 0,
        PRIMARY KEY (topic_id, conversation_id, msg_id),
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
    )
    """,

    # Link intelligence cache (per date)
    """
    CREATE TABLE IF NOT EXISTS link_intelligence_cache (
        date TEXT NOT NULL,
        version TEXT NOT NULL,
        payload TEXT NOT NULL,
        generated_at INTEGER NOT NULL,
        PRIMARY KEY (date, version)
    )
    """,

    # Sync state per conversation
    """
    CREATE TABLE IF NOT EXISTS sync_state (
        conversation_id TEXT PRIMARY KEY,
        last_synced_at INTEGER NOT NULL,
        last_msg_id INTEGER NOT NULL DEFAULT 0,
        first_message_date TEXT,
        last_message_date TEXT,
        total_messages INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'unknown',
        last_error TEXT,
        failed_chunks INTEGER NOT NULL DEFAULT 0,
        empty_chunks INTEGER NOT NULL DEFAULT 0,
        total_chunks INTEGER NOT NULL DEFAULT 0
    )
    """,

    # Key-value metadata store
    """
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
]

# ── Index DDL ─────────────────────────────────────────────────────────────────

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_messages_conversation_date ON messages(conversation_id, date)",
    "CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date)",
    "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC)",
    "CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender)",
    "CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)",
    "CREATE INDEX IF NOT EXISTS idx_mentions_timestamp ON mentions(timestamp DESC)",
    "CREATE INDEX IF NOT EXISTS idx_message_links_date ON message_links(date, timestamp DESC)",
    "CREATE INDEX IF NOT EXISTS idx_message_links_canonical ON message_links(canonical_url)",
    "CREATE INDEX IF NOT EXISTS idx_message_links_domain ON message_links(domain)",
    "CREATE INDEX IF NOT EXISTS idx_message_links_source ON message_links(source)",
    "CREATE INDEX IF NOT EXISTS idx_topics_date ON topics(date DESC, message_count DESC)",
    "CREATE INDEX IF NOT EXISTS idx_topic_messages_topic ON topic_messages(topic_id)",
    "CREATE INDEX IF NOT EXISTS idx_link_intelligence_cache_generated ON link_intelligence_cache(generated_at DESC)",
]

# ── Default seed data ─────────────────────────────────────────────────────────

DEFAULT_GROUPS = [
    ("AI 商业", "#6366f1", "🤖", 0),
    ("技术架构", "#06b6d4", "🏗️", 1),
    ("产品规划", "#f59e0b", "📋", 2),
    ("团队管理", "#10b981", "👥", 3),
    ("开源社区", "#8b5cf6", "🌐", 4),
    ("其他", "#6b7280", "📌", 99),
]

# ── Public API ─────────────────────────────────────────────────────────────────


def get_db() -> sqlite3.Connection:
    """Get a thread-local database connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = _open_db()
    return _local.conn


def _open_db() -> sqlite3.Connection:
    """Open database, enable WAL + foreign keys, run migrations."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    # Run schema migrations
    _run_migrations(conn)

    return conn


def _run_migrations(conn: sqlite3.Connection) -> None:
    """Create tables, indexes, and seed default data if needed."""
    current_version = _get_schema_version(conn)

    for ddl in DDL_STATEMENTS:
        conn.execute(ddl)

    if current_version < 1:
        for idx_ddl in INDEX_STATEMENTS:
            conn.execute(idx_ddl)
        _seed_default_groups(conn)
        _set_schema_version(conn, SCHEMA_VERSION)

    conn.commit()


def _get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version from meta table."""
    try:
        row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        return int(row["value"]) if row else 0
    except sqlite3.OperationalError:
        return 0


def _set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', ?)",
        (str(version),),
    )


def _seed_default_groups(conn: sqlite3.Connection) -> None:
    """Insert default group categories."""
    import time
    now = int(time.time())
    for name, color, emoji, sort_order in DEFAULT_GROUPS:
        conn.execute(
            "INSERT OR IGNORE INTO groups (name, color, emoji, sort_order, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, color, emoji, sort_order, now),
        )


def close_db() -> None:
    """Close the thread-local connection."""
    if hasattr(_local, "conn") and _local.conn is not None:
        _local.conn.close()
        _local.conn = None
