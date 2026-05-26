"""Mock NGA (AI) client wrapper.

In production, calls `nga run "<prompt>" --format json` via subprocess.
In local dev (no nga installed), returns synthetic responses.

Output is NDJSON (JSON Lines): one JSON object per line.
Event types: step_start, text (multiple), step_finish.
"""

import json
import time
from typing import AsyncIterator


_MOCK_ENABLED = True  # Toggle to False when nga CLI is available


# ── Mock responses ─────────────────────────────────────────────────────────────

_MOCK_TOPIC_RESPONSE = [
    {"type": "step_start", "timestamp": 0, "sessionID": "mock_ses_001",
     "part": {"id": "mock_prt_001", "sessionID": "mock_ses_001",
              "messageID": "mock_msg_001", "type": "step-start"}},
    {"type": "text", "timestamp": 0, "sessionID": "mock_ses_001",
     "part": {"id": "mock_prt_002", "sessionID": "mock_ses_001",
              "messageID": "mock_msg_001", "type": "text",
              "text": json.dumps([
                  {"title": "K8s 集群扩容讨论",
                   "summary": "团队讨论容器化部署和K8s集群扩容方案，涉及性能优化和灰度发布策略",
                   "message_count": 5, "group_count": 2},
                  {"title": "AI 模型推理性能优化",
                   "summary": "讨论使用 vLLM 降低推理延迟，目标 200ms 以内",
                   "message_count": 3, "group_count": 1},
                  {"title": "Q2 季度规划会议",
                   "summary": "安排 Q2 产品规划会议，涉及演示材料准备和项目里程碑",
                   "message_count": 4, "group_count": 2},
              ], ensure_ascii=False),
              "time": {"start": 0, "end": 0}}},
    {"type": "step_finish", "timestamp": 0, "sessionID": "mock_ses_001",
     "part": {"id": "mock_prt_003", "sessionID": "mock_ses_001",
              "messageID": "mock_msg_001", "type": "step-finish",
              "reason": "stop", "cost": 0,
              "tokens": {"total": 1200, "input": 1000, "output": 200, "reasoning": 0,
                         "cache": {"read": 0, "write": 0}}}},
]

_MOCK_LINK_TITLE_RESPONSE = [
    {"type": "step_start", "timestamp": 0, "sessionID": "mock_ses_002",
     "part": {"id": "mock_prt_004", "sessionID": "mock_ses_002",
              "messageID": "mock_msg_002", "type": "step-start"}},
    {"type": "text", "timestamp": 0, "sessionID": "mock_ses_002",
     "part": {"id": "mock_prt_005", "sessionID": "mock_ses_002",
              "messageID": "mock_msg_002", "type": "text",
              "text": json.dumps([
                  {"url": "https://github.com/example/awesome-project",
                   "title": "Awesome Project - 开源工具集", "kind": "tool"},
                  {"url": "https://iwiki.huawei.com/pages/12345",
                   "title": "K8s 部署最佳实践文档", "kind": "article"},
              ], ensure_ascii=False),
              "time": {"start": 0, "end": 0}}},
    {"type": "step_finish", "timestamp": 0, "sessionID": "mock_ses_002",
     "part": {"id": "mock_prt_006", "sessionID": "mock_ses_002",
              "messageID": "mock_msg_002", "type": "step-finish",
              "reason": "stop", "cost": 0,
              "tokens": {"total": 800, "input": 600, "output": 200, "reasoning": 0,
                         "cache": {"read": 0, "write": 0}}}},
]


# ── Public API ─────────────────────────────────────────────────────────────────


async def run_prompt(prompt: str) -> str:
    """Run a prompt through nga and collect the text response.

    Returns the concatenated text from all `text` events.
    """
    if _MOCK_ENABLED:
        # Determine which mock to use based on prompt content
        if "topic" in prompt.lower() or "话题" in prompt:
            events = _MOCK_TOPIC_RESPONSE
        elif "link" in prompt.lower() or "链接" in prompt or "title" in prompt.lower():
            events = _MOCK_LINK_TITLE_RESPONSE
        else:
            events = _MOCK_TOPIC_RESPONSE  # default

        text_parts = []
        for event in events:
            if event["type"] == "text":
                text_parts.append(event["part"]["text"])
        return "".join(text_parts)

    # TODO: Real implementation via subprocess
    return ""


async def run_prompt_stream(prompt: str) -> AsyncIterator[dict]:
    """Run a prompt and yield NDJSON events one by one.

    Yields each JSON event dict as it arrives.
    """
    if _MOCK_ENABLED:
        if "topic" in prompt.lower() or "话题" in prompt:
            events = _MOCK_TOPIC_RESPONSE
        elif "link" in prompt.lower() or "链接" in prompt or "title" in prompt.lower():
            events = _MOCK_LINK_TITLE_RESPONSE
        else:
            events = _MOCK_TOPIC_RESPONSE
        for event in events:
            yield event
        return

    # TODO: Real implementation via subprocess streaming
    yield {
        "type": "step_finish", "timestamp": int(time.time() * 1000),
        "sessionID": "empty", "part": {"type": "step-finish", "reason": "stop"}
    }


async def check_nga() -> bool:
    """Check if nga CLI is available."""
    import shutil
    return shutil.which("nga") is not None
