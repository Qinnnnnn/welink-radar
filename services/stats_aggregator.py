"""History sync & rescan service.

Pulls message history from welink-cli, stores locally, and aggregates stats.
"""

import asyncio
import logging
from typing import AsyncIterator, Optional

from clients.welink import get_history_messages
from services.message_store import (
    bulk_insert_messages, aggregate_daily_stats, save_daily_stats,
    upsert_sync_state, date_of_message,
)
from services.message_links import upsert_links_for_message
from services.mention_index import scan_mentions_for_message
from core.database import get_db

logger = logging.getLogger(__name__)


async def sync_conversation_history(
    conversation_id: str,
    target: str,  # group_id or user_account
    is_group: bool = True,
    max_sync_days: int = 90,
    on_progress: callable = None,
) -> dict:
    """Full history sync for one conversation.

    Paginates through welink-cli history using msgId cursors.
    """
    total_inserted = 0
    total_chunks = 0
    empty_chunks = 0
    failed_chunks = 0
    first_date = None
    last_date = None
    last_msg_id = 0
    current_cursor = None

    cutoff_ms = int(asyncio.get_event_loop().time() * 1000) - (max_sync_days * 86400 * 1000)

    while True:
        try:
            result = await get_history_messages(
                target=target,
                count=100,
                msg_id=current_cursor,
                direction=0,  # older
                is_group=is_group,
            )
        except Exception as e:
            logger.error(f"Sync failed for {conversation_id}: {e}")
            failed_chunks += 1
            break

        resp = result.get("respData", {})
        messages = resp.get("chatInfo", [])
        total_chunks += 1

        if not messages:
            empty_chunks += 1
            break

        # Filter out messages beyond cutoff
        filtered = [m for m in messages if m.get("serverSendTime", 0) >= cutoff_ms]
        if not filtered:
            break

        # Insert messages
        inserted = bulk_insert_messages(conversation_id, filtered)
        total_inserted += inserted

        # Extract links and scan mentions for each message
        for m in filtered:
            try:
                upsert_links_for_message(conversation_id, m)
                scan_mentions_for_message(conversation_id, m)
            except Exception:
                pass

        # Track date range
        times = [m["serverSendTime"] for m in filtered]
        if times:
            msg_first = date_of_message(min(times))
            msg_last = date_of_message(max(times))
            if first_date is None or msg_first < first_date:
                first_date = msg_first
            if last_date is None or msg_last > last_date:
                last_date = msg_last

        # Update cursor
        current_cursor = resp.get("minMsgId", 0)
        if resp.get("maxMsgId", 0) > last_msg_id:
            last_msg_id = resp["maxMsgId"]

        if on_progress:
            await on_progress({
                "conversation_id": conversation_id,
                "inserted": total_inserted,
                "chunks": total_chunks,
                "first_date": first_date,
                "last_date": last_date,
            })

        # Stop if we got fewer messages than requested
        if len(messages) < 100:
            break

    # Aggregate daily stats
    _aggregate_and_save_stats(conversation_id, first_date, last_date)

    # Update sync state
    status = "ok" if failed_chunks == 0 else "partial"
    upsert_sync_state(
        conversation_id=conversation_id,
        total=total_inserted,
        first_date=first_date,
        last_date=last_date,
        last_msg_id=last_msg_id,
        status=status,
        error=f"{failed_chunks} failed chunks" if failed_chunks else None,
    )

    return {
        "conversation_id": conversation_id,
        "total_inserted": total_inserted,
        "total_chunks": total_chunks,
        "empty_chunks": empty_chunks,
        "failed_chunks": failed_chunks,
        "first_date": first_date,
        "last_date": last_date,
        "status": status,
    }


async def sync_all_conversations(
    conversations: list[dict],
    max_sync_days: int = 90,
    concurrency: int = 3,
    on_progress: callable = None,
) -> AsyncIterator[dict]:
    """Sync history for multiple conversations with concurrency control."""
    semaphore = asyncio.Semaphore(concurrency)

    async def sync_one(conv: dict) -> dict:
        async with semaphore:
            conv_id = conv["conversation_id"]
            is_group = conv["type"] == "group"
            target = conv["group_id"] if is_group else conv["target_account"]
            if not target:
                return {"conversation_id": conv_id, "error": "no target"}

            return await sync_conversation_history(
                conversation_id=conv_id,
                target=target,
                is_group=is_group,
                max_sync_days=max_sync_days,
                on_progress=on_progress,
            )

    tasks = [sync_one(c) for c in conversations]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        yield result


def _aggregate_and_save_stats(conversation_id: str, first_date: str | None, last_date: str | None) -> None:
    """Compute and persist daily_stats for all dates with messages."""
    if not first_date or not last_date:
        return

    from services.message_store import list_all_synced_dates
    dates = list_all_synced_dates(conversation_id)
    if dates:
        stats = aggregate_daily_stats(conversation_id, dates)
        if stats:
            save_daily_stats(stats)
