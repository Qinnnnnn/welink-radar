"""DB info route — database metadata."""

import os
from fastapi import APIRouter
from core.config import DATA_DIR
from core.database import DB_PATH, get_db

router = APIRouter(prefix="/api/dbinfo", tags=["dbinfo"])


@router.get("")
async def get_dbinfo():
    """Return database metadata and top groups."""
    db_size = os.path.getsize(str(DB_PATH)) if DB_PATH.exists() else 0
    db = get_db()

    counts = {}
    for table in ["messages", "conversations", "mentions", "message_links", "topics", "daily_stats"]:
        row = db.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
        counts[table] = row["cnt"] if row else 0

    top_groups = db.execute(
        """SELECT conversation_id, COUNT(*) as cnt
           FROM messages GROUP BY conversation_id
           ORDER BY cnt DESC LIMIT 10"""
    ).fetchall()

    return {
        "dataDir": str(DATA_DIR),
        "dbPath": str(DB_PATH),
        "dbSize": db_size,
        "counts": counts,
        "topGroups": [{"id": r["conversation_id"], "count": r["cnt"]} for r in top_groups],
    }
