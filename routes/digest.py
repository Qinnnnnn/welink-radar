"""Daily digest API routes."""

from fastapi import APIRouter, Query
from services.daily_digest import build_daily_digest, get_unclosed_items

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("")
async def api_digest(date: str = Query(default="", description="YYYY-MM-DD, default today UTC")):
    """Return the full daily digest.

    Includes overview stats, @mentions (strong/weak), and AI analysis
    (topics, unclosed items, closed items).
    """
    d = date or None
    return await build_daily_digest(d)


@router.get("/unclosed")
async def api_unclosed(date: str = Query(default="", description="YYYY-MM-DD, default today UTC")):
    """Return only the unclosed items for the given date."""
    d = date or None
    return await get_unclosed_items(d)
