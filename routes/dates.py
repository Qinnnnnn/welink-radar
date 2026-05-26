"""Dates route — returns dates with message data."""

from fastapi import APIRouter
from core.database import get_db

router = APIRouter(prefix="/api/dates", tags=["dates"])


@router.get("")
async def get_dates():
    """Return message counts grouped by date."""
    db = get_db()
    rows = db.execute(
        """SELECT date, COUNT(*) as count
           FROM messages
           GROUP BY date
           ORDER BY date DESC
           LIMIT 365"""
    ).fetchall()
    return {"ok": True, "dates": [{"date": r["date"], "count": r["count"]} for r in rows]}
