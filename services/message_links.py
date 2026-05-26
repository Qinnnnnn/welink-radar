"""Message link extraction service.

Extracts URLs from WeLink messages, canonicalizes them, and stores in message_links table.
Handles TEXT_MSG plain URLs and CARD_MSG embedded JSON payloads.
"""

import json
import logging
import re
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from core.database import get_db

logger = logging.getLogger(__name__)

# URL regex pattern
URL_PATTERN = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')

# Tracking params to strip for canonicalization
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "source", "from", "spm",
}

# Common article/tool domains for classification
ARTICLE_DOMAINS = {
    "iwiki.huawei.com", "3ms.huawei.com", "csdn.net", "zhihu.com",
    "juejin.cn", "mp.weixin.qq.com", "blog.", "docs.",
}
TOOL_DOMAINS = {
    "github.com", "gitlab.", "npmjs.com", "pypi.org",
    "docker.com", "hub.docker.com", "clouddrive.huawei.com",
    "onebox.huawei.com",
}


def extract_message_links(content: str) -> list[str]:
    """Extract raw URLs from message content."""
    return URL_PATTERN.findall(content)


def canonicalize_url(url: str) -> str:
    """Strip tracking params and normalize URL."""
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        # Remove tracking params
        cleaned = {k: v for k, v in query_params.items() if k not in TRACKING_PARAMS}
        new_query = urlencode(cleaned, doseq=True) if cleaned else ""
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                           parsed.params, new_query, parsed.fragment))
    except Exception:
        return url


def classify_link_domain(url: str) -> tuple[str, str]:
    """Classify a URL as 'article', 'tool', or 'unknown'.
    Returns (kind, domain).
    """
    try:
        domain = urlparse(url).netloc.lower()
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]

        for ad in ARTICLE_DOMAINS:
            if ad in domain:
                return "article", domain
        for td in TOOL_DOMAINS:
            if td in domain:
                return "tool", domain
        return "unknown", domain
    except Exception:
        return "unknown", ""


def upsert_links_for_message(conversation_id: str, message: dict) -> int:
    """Extract and store links from a single message. Returns count stored."""
    content = message.get("content", "")
    content_type = message.get("contentType", "TEXT_MSG")
    msg_id = message["msgId"]
    sender = message.get("sender", "")
    server_send_time = message.get("serverSendTime", 0)

    from services.message_store import send_time_of_message, date_of_message
    s_time = send_time_of_message(server_send_time)
    ts = int(server_send_time / 1000)
    date_str = date_of_message(server_send_time)
    now = int(time.time())

    # Extract URLs from plain text
    urls = extract_message_links(content)

    # Also try to extract URLs from CARD_MSG JSON payloads
    if content_type == "CARD_MSG" and not urls:
        try:
            card = json.loads(content)
            card_str = json.dumps(card, ensure_ascii=False)
            urls = extract_message_links(card_str)
        except (json.JSONDecodeError, TypeError):
            pass

    # Also check IMAGESPAN_MSG for cloud drive URLs
    if content_type == "IMAGESPAN_MSG" and not urls:
        urls = extract_message_links(content)

    if not urls:
        return 0

    db = get_db()
    stored = 0
    for url in urls:
        canonical = canonicalize_url(url)
        kind, domain = classify_link_domain(canonical)
        try:
            cur = db.execute(
                """INSERT OR IGNORE INTO message_links
                   (conversation_id, msg_id, date, sender, send_time, timestamp,
                    url, canonical_url, title, description, domain, source, raw_kind, confidence, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, 1, ?)""",
                (conversation_id, msg_id, date_str, sender, s_time, ts,
                 url, canonical, domain, "welink", kind, now),
            )
            if cur.rowcount > 0:
                stored += 1
        except Exception as e:
            logger.error(f"Failed to store link: {e}")

    if stored > 0:
        db.commit()
    return stored


def upsert_resolved_link(title: str | None = None, description: str | None = None,
                          source: str = "welink", confidence: float = 1.0) -> bool:
    """Placeholder for manual link resolution. Not yet implemented."""
    # This would resolve a specific message link with enriched metadata
    return True


def backfill_message_links(since: str | None = None, until: str | None = None) -> dict:
    """Scan all stored messages and backfill links for those missing from message_links."""
    db = get_db()

    conditions = ["1=1"]
    params = []
    if since:
        conditions.append("date >= ?")
        params.append(since)
    if until:
        conditions.append("date <= ?")
        params.append(until)

    where = " AND ".join(conditions)

    # Find messages that contain URLs but may not have been processed
    rows = db.execute(
        f"""SELECT * FROM messages
            WHERE {where}
            AND (content LIKE '%http://%' OR content LIKE '%https://%')
            ORDER BY timestamp DESC
            LIMIT 10000""",
        params,
    ).fetchall()

    total = 0
    for row in rows:
        msg = dict(row)
        msg["msgId"] = msg["msg_id"]
        count = upsert_links_for_message(msg["conversation_id"], msg)
        total += count

    return {"processed": len(rows), "links_stored": total}


def get_raw_links_for_date(date: str) -> list[dict]:
    """Get raw message_links for a given date."""
    db = get_db()
    rows = db.execute(
        """SELECT * FROM message_links WHERE date = ? ORDER BY timestamp DESC""",
        (date,),
    ).fetchall()
    return [dict(r) for r in rows]
