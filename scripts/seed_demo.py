"""Demo data seeder for WeLink Radar.

Generates 14 days of synthetic WeLink conversations, messages, and stats.
Adapted from wechat-radar/lib/demo-data.ts for WeLink's data model.
"""

import json
import random
import time
from datetime import datetime, timezone, timedelta

from core.database import get_db
from core.config import write_config

# ── Demo data ─────────────────────────────────────────────────────────────────

DEMO_GROUPS = [
    {"group_id": "944052726495445547", "name": "产品需求讨论群", "type": "group",
     "group_type": "NORMAL_GROUP"},
    {"group_id": "708543592267911909", "name": "技术架构评审", "type": "group",
     "group_type": "NORMAL_GROUP"},
    {"group_id": "675805850476069040", "name": "AI 项目推进组", "type": "group",
     "group_type": "NORMAL_GROUP"},
    {"group_id": "834854760434885793", "name": "开源技术交流群", "type": "group",
     "group_type": "NORMAL_GROUP"},
]

DEMO_SENDERS = ["z00123456", "l00765432", "w00987654", "q00510847", "l00818094",
                "j00629149", "z00540487", "p00829773"]

DEMO_CONTENTS_POOL = [
    # Product discussions
    ("大家看下这个新方案，我觉得可以优化一下部署流程", "z00123456"),
    ("同意，容器化之后确实方便很多，k8s 的 auto-scaling 也很好用", "l00765432"),
    ("@所有人 明天下午3点开会讨论 Q2 产品规划", "z00123456"),
    ("我这边有个性能问题需要帮忙看一下，API 响应时间超过 500ms", "w00987654"),
    ("https://github.com/kubernetes/kubernetes 可以参考下最新版本", "q00510847"),

    # Tech architecture
    ("本周微服务架构评审的结论：建议统一使用 gRPC 做服务间通信", "l00765432"),
    ("K8s 集群扩容申请已经提交了，预计下周可以到位", "w00987654"),
    ("这个 PR 我 review 过了，代码质量不错，有几个小的建议已 comment", "q00510847"),
    ("文档已更新：https://iwiki.huawei.com/pages/k8s-best-practices", "l00765432"),
    ("新版本的性能提升了 30%，压测通过了，可以安排上线", "z00123456"),

    # AI/ML topics
    ("AI 模型的推理延迟需要降到 200ms 以内，目前是 450ms", "w00987654"),
    ("可以用 vLLM 试试做 batch inference，我们之前在另一个项目验证过效果", "q00510847"),
    ("好的，我搭个 PoC 验证一下效果，预计三天内出结果", "j00629149"),
    ("MiniMax-M2.7 在代码生成任务上表现不错，可以考虑集成", "z00540487"),
    ("@所有人 今天下午的 AI 分享会改到 4 点，大家注意时间", "p00829773"),

    # Team management
    ("本周周报已经发出，请大家查收，重点关注 Q2 OKR 进展", "z00123456"),
    ("下周一的产品演示材料准备好了吗？需要提前发给领导 review", "l00765432"),
    ("在整理中，今晚发出来给大家看", "z00123456"),
    ("团队建设活动定在下周五下午，地点待定", "p00829773"),
    ("新同事下周一入职，请大家帮忙做好 on-boarding 准备", "l00765432"),

    # Open source
    ("最近 Apache 基金会发布了新的孵化项目，跟我们的方向很契合", "q00510847"),
    ("开源社区的 star 数突破 1000 了 🎉", "z00123456"),
    ("有人提交了一个很棒的 PR，优化了我们的构建流程", "j00629149"),
    ("这个 issue 需要讨论一下：https://github.com/example/project/issues/42", "q00510847"),
    ("周末的线上 meetup 有人报名参加吗？讲 K8s 最佳实践", "w00987654"),
]

DEMO_LINKS = [
    "https://github.com/kubernetes/kubernetes",
    "https://iwiki.huawei.com/pages/k8s-best-practices",
    "https://github.com/vllm-project/vllm",
    "https://github.com/example/project/issues/42",
    "https://clouddrive.huawei.com/f/doc12345",
]

# ── Seed function ─────────────────────────────────────────────────────────────


def seed_demo_data(days: int = 14):
    """Seed demo data: conversations, messages, daily_stats, and links."""
    db = get_db()
    now_ms = int(time.time() * 1000)
    today = datetime.now(timezone.utc)

    # Enable demo mode in config
    write_config({
        "demoMode": True,
        "setupCompleted": True,
        "privacyConfirmed": True,
        "myNicknames": ["张三", "San Zhang", "zhangsan"],
    })

    # Insert conversations
    for conv in DEMO_GROUPS:
        db.execute(
            """INSERT OR REPLACE INTO conversations
               (conversation_id, name, type, group_id, target_account, staff_name, group_type, cross_instance, updated_at)
               VALUES (?, ?, ?, ?, NULL, NULL, ?, 0, ?)""",
            (f"group_{conv['group_id']}", conv["name"], conv["type"],
             conv["group_id"], conv["group_type"], int(time.time())),
        )

    # Generate messages for each day
    for day_offset in range(days, -1, -1):
        day = today - timedelta(days=day_offset)
        date_str = day.strftime("%Y-%m-%d")

        for conv in DEMO_GROUPS:
            conv_id = f"group_{conv['group_id']}"

            # Random number of messages per group per day (5-35)
            msg_count = random.randint(5, 35)

            for i in range(msg_count):
                content, sender = random.choice(DEMO_CONTENTS_POOL)
                msg_time_ms = now_ms - (day_offset * 86400 * 1000) - (i * random.randint(30000, 300000))
                msg_id = int(f"{hash(conv_id) % 10000}{msg_time_ms:013d}"[:17])
                ts = int(msg_time_ms / 1000)
                s_time = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                is_at = "@所有人" in content or "@" in content and sender != "z00123456"
                at_list = json.dumps(["所有人"]) if "@所有人" in content else None

                try:
                    db.execute(
                        """INSERT OR IGNORE INTO messages
                           (conversation_id, msg_id, sender, receiver, content, content_type,
                            is_at, at_accounts, send_time, timestamp, date)
                           VALUES (?, ?, ?, '', ?, 'TEXT_MSG', ?, ?, ?, ?, ?)""",
                        (conv_id, msg_id, sender, content, 1 if is_at else 0,
                         at_list, s_time, ts, date_str),
                    )
                except Exception:
                    pass

                # Occasionally insert a link
                if random.random() < 0.15:
                    url = random.choice(DEMO_LINKS)
                    parsed_domain = url.split("/")[2] if "//" in url else url
                    try:
                        db.execute(
                            """INSERT OR IGNORE INTO message_links
                               (conversation_id, msg_id, date, sender, send_time, timestamp,
                                url, canonical_url, domain, source, raw_kind, confidence, created_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'welink', 'article', 1, ?)""",
                            (conv_id, msg_id, date_str, sender, s_time, ts,
                             url, url, parsed_domain, ts),
                        )
                    except Exception:
                        pass

        db.commit()

    # Aggregate daily stats for all conversations and dates
    from services.message_store import aggregate_daily_stats, save_daily_stats
    for conv in DEMO_GROUPS:
        conv_id = f"group_{conv['group_id']}"
        dates = []
        for day_offset in range(days, -1, -1):
            day = today - timedelta(days=day_offset)
            dates.append(day.strftime("%Y-%m-%d"))
        stats = aggregate_daily_stats(conv_id, dates)
        if stats:
            save_daily_stats(stats)

    # Rebuild mention index
    from services.mention_index import rebuild_mention_index
    rebuild_mention_index()

    print(f"✅ Demo data seeded: {len(DEMO_GROUPS)} conversations, {days + 1} days of messages")
    return {"conversations": len(DEMO_GROUPS), "days": days + 1}


if __name__ == "__main__":
    seed_demo_data()
