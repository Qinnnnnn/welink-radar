"""Message links routes — link intelligence and raw links."""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from services.link_intelligence import get_daily_link_intelligence, clear_daily_link_intelligence
from services.message_links import get_raw_links_for_date, backfill_message_links
from datetime import datetime, timezone

router = APIRouter(tags=["links"])


@router.get("/api/topics/links")
async def get_links_intelligence(
    date: str = Query(default=""),
    refresh: str = Query(default="0"),
):
    """Get daily link intelligence."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target_date = date or today
    do_refresh = refresh in ("1", "true")
    result = await get_daily_link_intelligence(target_date, refresh=do_refresh)
    return {"ok": True, **result}


@router.get("/api/message-links/raw")
async def get_raw_links(date: str = Query(default="")):
    """Get raw WeLink message links for a date."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target_date = date or today
    links = get_raw_links_for_date(target_date)
    return {"ok": True, "date": target_date, "links": links}


class ResolveLinkPayload(BaseModel):
    conversation_id: str
    msg_id: int
    url: str
    title: str | None = None
    description: str | None = None
    source: str = "welink"
    confidence: float = 1.0


@router.post("/api/message-links/resolve")
async def resolve_link(payload: ResolveLinkPayload):
    """Store/resolve a message link mapping."""
    from services.message_links import upsert_resolved_link
    upsert_resolved_link()
    return {"ok": True}


class BackfillPayload(BaseModel):
    since: str | None = None
    until: str | None = None


@router.post("/api/message-links/backfill")
async def backfill_links(payload: BackfillPayload):
    """Backfill message links over a date range."""
    result = backfill_message_links(since=payload.since, until=payload.until)
    return {"ok": True, **result}
