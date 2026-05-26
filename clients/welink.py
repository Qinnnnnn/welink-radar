"""Mock WeLink CLI wrapper.

In production, calls `welink-cli` via subprocess to fetch WeLink IM data.
In local dev (no welink-cli installed), returns synthetic demo data.

All public functions are async and return Python dicts matching the real CLI output.
"""

import json
import time
from typing import Optional

# ── Mock data ──────────────────────────────────────────────────────────────────

_MOCK_SESSIONS = {
    "conversation_info": [
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "944052726495445547",
         "group_name": "产品需求讨论群", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "708543592267911909",
         "group_name": "技术架构评审", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "675805850476069040",
         "group_name": "AI 项目推进组", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "834854760434885793",
         "group_name": "开源技术交流群", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "张三", "staff_name": "zhangsan 00123456",
         "target_account": "z00123456", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "李四", "staff_name": "lisi 00765432",
         "target_account": "l00765432", "cross_instance": False},
    ],
    "error": {"error_code": "IM.0000", "error_msg": "success"},
}

_MOCK_GROUP_MEMBERS = {
    "member_info_list": [
        {"member_account": "z00123456", "member_type": "TYPE_OWNER", "group_id": "675805850476069040"},
        {"member_account": "l00765432", "member_type": "TYPE_NORMAL", "group_id": "675805850476069040"},
        {"member_account": "w00987654", "member_type": "TYPE_NORMAL", "group_id": "675805850476069040"},
        {"member_account": "q00510847", "member_type": "TYPE_NORMAL", "group_id": "675805850476069040"},
        {"member_account": "l00818094", "member_type": "TYPE_NORMAL", "group_id": "675805850476069040"},
    ],
    "error": {"error_code": "IM.0000", "error_msg": "SUCCESS"},
}

# ── Helpers ────────────────────────────────────────────────────────────────────

_MOCK_ENABLED = True  # Toggle to False when welink-cli is available


def _now_ms() -> int:
    return int(time.time() * 1000)


_MOCK_MESSAGE_POOL = [
    ("大家看下这个新方案，我觉得可以优化一下部署流程", "z00123456"),
    ("同意，容器化之后确实方便很多", "l00765432"),
    ("@所有人 明天下午3点开会讨论 Q2 规划", "z00123456"),
    ("我这边有个性能问题需要帮忙看一下", "w00987654"),
    ("https://github.com/example/awesome-project 这个开源项目可以参考", "q00510847"),
    ("收到，我来跟进这个问题", "l00765432"),
    ("本周的周报已经发出，请大家查收", "z00123456"),
    ("K8s 集群扩容申请已经提交了", "w00987654"),
    ("这个 PR 我 review 过了，有几个建议", "q00510847"),
    ("文档已更新：https://iwiki.huawei.com/pages/12345", "l00765432"),
    ("新版本的性能提升了 30%，可以安排上线了", "z00123456"),
    ("好的，我来安排灰度发布", "w00987654"),
    ("测试环境已经准备好了，大家可以开始验证", "q00510847"),
    ("有个紧急 bug 需要修：登录页白屏", "l00765432"),
    ("已修复，等 CI 通过就合并", "q00510847"),
    ("下周一的演示材料准备好了吗？@张三", "l00765432"),
    ("在整理中，今晚发出来", "z00123456"),
    ("AI 模型推理延迟需要降到 200ms 以内", "w00987654"),
    ("可以用 vLLM 试试，我们之前验证过", "q00510847"),
    ("好的，我搭个 PoC 验证一下效果", "w00987654"),
]


def _generate_mock_messages(group_id: str, count: int = 20) -> list[dict]:
    """Generate synthetic messages for a given group."""
    base_ms = _now_ms()
    messages = []
    for i in range(count):
        content, sender = _MOCK_MESSAGE_POOL[i % len(_MOCK_MESSAGE_POOL)]
        messages.append({
            "at": "@" in content and "所有人" in content,
            "atAccountList": [],
            "content": content,
            "contentType": "TEXT_MSG",
            "groupId": int(group_id),
            "groupType": 0 if group_id == "0" else 0,
            "msgId": int(group_id + str(base_ms - i * 60000)) % (10**17),
            "receiver": "",
            "sender": sender,
            "serverSendTime": base_ms - i * 60000,
        })
    # Ensure msgId values are unique and descending (newest first)
    for i, m in enumerate(messages):
        m["msgId"] = int(f"{hash(group_id) % 10000}{base_ms - i * 60000:013d}"[:17])
    return messages


# ── Public API ─────────────────────────────────────────────────────────────────


async def get_sessions(limit: int = 50) -> dict:
    """Fetch recent conversations. Mirrors `welink-cli im query-recent-conversation`."""
    if _MOCK_ENABLED:
        sessions = _MOCK_SESSIONS.copy()
        sessions["conversation_info"] = sessions["conversation_info"][:limit]
        return sessions
    # TODO: Real implementation via subprocess
    return _MOCK_SESSIONS


async def get_history_messages(
    target: str,
    count: int = 20,
    msg_id: Optional[int] = None,
    direction: int = 1,
    is_group: bool = True,
) -> dict:
    """Fetch history messages. Mirrors `welink-cli im query-history-message`.

    Args:
        target: group_id (if is_group=True) or user_account (if is_group=False)
        count: number of messages to fetch
        msg_id: pagination cursor (msgId to start from)
        direction: 0=older, 1=newer
        is_group: True for group chat, False for private chat
    """
    if _MOCK_ENABLED:
        group_id = target if is_group else "0"
        messages = _generate_mock_messages(group_id, count)
        msg_ids = [m["msgId"] for m in messages]
        max_id = max(msg_ids) if msg_ids else 0
        min_id = min(msg_ids) if msg_ids else 0
        return {
            "respData": {
                "chatInfo": messages,
                "maxMsgId": max_id,
                "minMsgId": min_id,
                "msgTotalCount": count,
            },
            "resultCode": "0",
            "resultContext": "Operate Success",
        }
    # TODO: Real implementation
    return {"respData": {"chatInfo": [], "maxMsgId": 0, "minMsgId": 0, "msgTotalCount": 0},
            "resultCode": "0", "resultContext": "Operate Success"}


async def get_group_members(group_id: str) -> dict:
    """Fetch group members. Mirrors `welink-cli im query-group-member`."""
    if _MOCK_ENABLED:
        return _MOCK_GROUP_MEMBERS
    return {"member_info_list": [], "error": {"error_code": "IM.0000", "error_msg": "SUCCESS"}}


async def get_auth_status() -> dict:
    """Check WeLink CLI auth status."""
    return {"authenticated": True, "message": "Mock auth — no welink-cli installed"}


async def check_cli() -> bool:
    """Check if welink-cli is available."""
    import shutil
    return shutil.which("welink-cli") is not None
