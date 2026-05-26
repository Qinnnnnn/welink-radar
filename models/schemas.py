"""Pydantic data models for WeLink Radar."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConfigModel(BaseModel):
    """Persistent user configuration (~/.welink-radar/config.json)."""
    myNicknames: list[str] = Field(default_factory=list)
    defaultRange: str = "week"  # day | week | month | quarter | year
    rescanConcurrency: int = 3
    privacyConfirmed: bool = False
    setupCompleted: bool = False
    demoMode: bool = False
    defaultSyncDays: int = 90


class ConversationInfo(BaseModel):
    """A WeLink conversation (group or private chat)."""
    conversation_id: str  # "group_xxx" or "user_xxx"
    name: str
    type: str  # "group" | "user"
    group_id: Optional[str] = None
    target_account: Optional[str] = None
    staff_name: Optional[str] = None
    group_type: Optional[str] = None
    cross_instance: bool = False


class MessageRow(BaseModel):
    """A stored WeLink message."""
    conversation_id: str
    msg_id: int
    sender: str
    receiver: str
    content: str
    content_type: str  # TEXT_MSG, CARD_MSG, IMAGESPAN_MSG, ...
    is_at: bool = False
    at_accounts: Optional[str] = None  # JSON array string
    send_time: str  # "YYYY-MM-DD HH:MM:SS"
    timestamp: int  # Unix seconds
    date: str  # "YYYY-MM-DD"


class DailyStats(BaseModel):
    """Aggregated daily stats for a conversation."""
    conversation_id: str
    date: str
    total: int
    top_senders: str  # JSON string: [{"sender":"x","count":n}, ...]
    by_hour: str  # JSON string: [0,0,5,12,...] 24 elements
    refreshed_at: int


class MentionRow(BaseModel):
    """A stored @mention."""
    conversation_id: str
    msg_id: int
    sender: str
    content: str
    send_time: str
    timestamp: int
    seen: bool = False


class TopicItem(BaseModel):
    """A daily aggregated topic."""
    id: int
    date: str
    title: str
    summary: Optional[str] = None
    message_count: int
    group_count: int


class TopicDetail(BaseModel):
    """Full topic with associated messages."""
    id: int
    date: str
    title: str
    summary: Optional[str] = None
    message_count: int
    group_count: int
    messages: list[dict] = Field(default_factory=list)


class LinkIntelligenceItem(BaseModel):
    """An aggregated link intelligence entry."""
    canonical_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    domain: str
    source: str  # "article" | "tool"
    count: int
    group_count: int
    last_seen: Optional[str] = None
    sample_content: Optional[str] = None


class GroupRow(BaseModel):
    """A user-defined group/category."""
    id: Optional[int] = None
    name: str
    color: str
    emoji: Optional[str] = None
    sort_order: int = 0


class SyncState(BaseModel):
    """Sync progress for a conversation."""
    conversation_id: str
    last_synced_at: int
    last_msg_id: int
    first_message_date: Optional[str] = None
    last_message_date: Optional[str] = None
    total_messages: int = 0
    status: str = "unknown"


class DashboardStats(BaseModel):
    """Aggregated dashboard response."""
    range: str
    date: str
    days: int = 0
    active_groups: int = 0
    total_messages: int = 0
    total_mentions: int = 0
    silent_groups: int = 0
    trend: list[dict] = Field(default_factory=list)
    trend_peak: Optional[dict] = None
    trend_avg: float = 0.0
    categories: list[dict] = Field(default_factory=list)
    intelligence: Optional[dict] = None
    sidebar_groups: list[dict] = Field(default_factory=list)
    sidebar_categories: list[dict] = Field(default_factory=list)


class SetupStatus(BaseModel):
    """Response for GET /api/setup."""
    configured: bool
    config: Optional[ConfigModel] = None
    env_checks: dict = Field(default_factory=dict)
    demo_available: bool = False
