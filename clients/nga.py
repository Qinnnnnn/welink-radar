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

_MOCK_DIGEST_RESPONSE = [
    {"type": "step_start", "timestamp": 0, "sessionID": "mock_ses_003",
     "part": {"id": "mock_prt_010", "sessionID": "mock_ses_003",
              "messageID": "mock_msg_003", "type": "step-start"}},
    {"type": "text", "timestamp": 0, "sessionID": "mock_ses_003",
     "part": {"id": "mock_prt_011", "sessionID": "mock_ses_003",
              "messageID": "mock_msg_003", "type": "text",
              "text": json.dumps({
                  "topics": [
                      {"title": "vLLM 推理性能优化",
                       "summary": "PoC 验证完成，延迟从 800ms 降至 180ms，H20 吞吐 2300 tokens/s，下周演示",
                       "group_count": 1, "message_count": 4},
                      {"title": "微服务架构拆分与网关限流",
                       "summary": "方案已更新至 Confluence，限流策略待细化，Redis 集群容量待评估",
                       "group_count": 1, "message_count": 3},
                      {"title": "Q2 OKR 自评与季度报告",
                       "summary": "全员需在周五前提交 OKR 自评，Q2 汇总报告周三前出完整版",
                       "group_count": 2, "message_count": 5},
                      {"title": "CI/CD 流水线与 DevOps 工具链",
                       "summary": "自托管 GitHub Actions runner 提速 3 倍，Trivy 安全扫描已集成，Artifactory 存储待清理",
                       "group_count": 1, "message_count": 3},
                      {"title": "数据平台技术选型",
                       "summary": "数据湖选型 Hudi vs Iceberg 还在评估中，Flink CDC 延迟 200-500ms 满足需求",
                       "group_count": 1, "message_count": 3},
                  ],
                  "unclosed": [
                      {"title": "Redis 集群容量规划待评估",
                       "reason": "提问无人认领",
                       "source_group": "技术架构评审",
                       "key_person": "z00123456",
                       "risk": "中",
                       "detail": "w00987654 询问 Q3 峰值 QPS 50K 的 Redis 容量规划，z00123456 表示还没评估并询问谁有空，目前无人认领"},
                      {"title": "登录模块交互稿未交付",
                       "reason": "承诺未兑现",
                       "source_group": "产品需求讨论群",
                       "key_person": "待确认",
                       "risk": "高",
                       "detail": "设计侧等待登录模块交互稿接入，但对接人未明确，需求评审改到周四"},
                      {"title": "王五的鉴权方式咨询未回复",
                       "reason": "提问无人回复",
                       "source_group": "王五 (私聊)",
                       "key_person": "q00510847",
                       "risk": "中",
                       "detail": "王五两次追问权限中台鉴权用 JWT 还是 OAuth2，最新消息未收到回复"},
                      {"title": "入职培训材料未更新",
                       "reason": "承诺未兑现",
                       "source_group": "团队管理群",
                       "key_person": "q00510847",
                       "risk": "高",
                       "detail": "l00765432 提醒入职培训材料需更新，新人下周到，q00510847 承诺明天发但尚未完成"},
                      {"title": "Q2 OKR 模板路径不明确",
                       "reason": "决策未定",
                       "source_group": "团队管理群",
                       "key_person": "z00123456",
                       "risk": "低",
                       "detail": "多人询问模板路径和跨团队目标填写方式，已解答但需确认全员知晓"},
                      {"title": "Artifactory 存储清理无人执行",
                       "reason": "提问无人认领",
                       "source_group": "DevOps 实践",
                       "key_person": "待确认",
                       "risk": "低",
                       "detail": "z00123456 指出 Artifactory 快满，询问谁清理旧 snapshot，无人回应"},
                  ],
                  "closed": [
                      {"title": "午饭安排确认",
                       "conclusion": "12 点大厅碰头，叫上王五",
                       "source_group": "李四 (私聊)"},
                      {"title": "Axum 框架推荐",
                       "conclusion": "已推荐，团队已在用，Go 推荐 Fiber/Chi",
                       "source_group": "开源技术交流群"},
                      {"title": "性能测试报告发送",
                       "conclusion": "已发送并确认收到，连接池问题正在排查",
                       "source_group": "赵六 (私聊)"},
                  ],
              }, ensure_ascii=False),
              "time": {"start": 0, "end": 0}}},
    {"type": "step_finish", "timestamp": 0, "sessionID": "mock_ses_003",
     "part": {"id": "mock_prt_012", "sessionID": "mock_ses_003",
              "messageID": "mock_msg_003", "type": "step-finish",
              "reason": "stop", "cost": 0,
              "tokens": {"total": 2400, "input": 1800, "output": 600, "reasoning": 0,
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
        if "digest" in prompt.lower() or "摘要" in prompt or "daily" in prompt.lower() or "unclosed" in prompt.lower() or "未闭环" in prompt:
            events = _MOCK_DIGEST_RESPONSE
        elif "topic" in prompt.lower() or "话题" in prompt:
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
        if "digest" in prompt.lower() or "摘要" in prompt or "daily" in prompt.lower() or "unclosed" in prompt.lower() or "未闭环" in prompt:
            events = _MOCK_DIGEST_RESPONSE
        elif "topic" in prompt.lower() or "话题" in prompt:
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
