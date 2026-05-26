"""Heuristic group classifier.

Maps conversation names to user-defined group categories using regex patterns.
Mirrors WeChat Radar's group-classifier.ts.
"""

import re
from core.database import get_db

# ── Classification patterns ───────────────────────────────────────────────────

CLASSIFICATION_RULES: list[tuple[list[str], str]] = [
    # (patterns, matching group name)
    (
        ["AI", "智能", "模型", "算法", "机器学习", "深度学习", "LLM", "GPT", "推理", "训练"],
        "AI 商业",
    ),
    (
        ["架构", "系统设计", "技术方案", "代码", "开发", "编程", "K8s", "部署",
         "微服务", "容器", "DevOps", "CI", "CD", "接口", "API"],
        "技术架构",
    ),
    (
        ["产品", "需求", "规划", "版本", "迭代", "PRD", "原型", "设计", "评审"],
        "产品规划",
    ),
    (
        ["团队", "管理", "周报", "例会", "全员", "建设", "外包", "HR", "行政"],
        "团队管理",
    ),
    (
        ["开源", "社区", "GitHub", "GitLab", "贡献", "Apache", "Linux", "基金会"],
        "开源社区",
    ),
]


def classify_conversation_heuristic(name: str, summary: str = "") -> str | None:
    """Guess which group category a conversation belongs to.

    Returns the group name (matching the seeded groups table), or None.
    """
    text = f"{name} {summary}".lower()

    for patterns, group_name in CLASSIFICATION_RULES:
        for pat in patterns:
            if pat.lower() in text:
                return group_name

    return None


def effective_group_ids(name: str, summary: str = "",
                         explicit_ids: list[int] | None = None) -> list[int]:
    """Get effective group IDs for a conversation.

    Uses explicit tags if available, otherwise falls back to heuristic.
    """
    if explicit_ids:
        return explicit_ids

    db = get_db()
    heuristic_name = classify_conversation_heuristic(name, summary)
    if heuristic_name:
        row = db.execute(
            "SELECT id FROM groups WHERE name = ?", (heuristic_name,)
        ).fetchone()
        if row:
            return [row["id"]]

    # Default to "其他"
    row = db.execute("SELECT id FROM groups WHERE name = '其他'").fetchone()
    return [row["id"]] if row else []
