"""Mock WeLink CLI wrapper.

In production, calls `welink-cli` via subprocess to fetch WeLink IM data.
In local dev (no welink-cli installed), returns synthetic demo data.

All public functions are async and return Python dicts matching the real CLI output.

Quick-swap: set _MOCK_ENABLED = False and uncomment the subprocess blocks
to use real welink-cli. All callers remain unchanged.
"""

import json
import time
from typing import Optional

# ── Mock toggle ────────────────────────────────────────────────────────────────

_MOCK_ENABLED = True  # Toggle to False when welink-cli is available

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
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "717915662353219752",
         "group_name": "前端技术交流", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "758559285016953862",
         "group_name": "团队管理群", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "823456789012345678",
         "group_name": "DevOps 实践", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "912345678901234567",
         "group_name": "数据平台建设", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "张三", "staff_name": "zhangsan 00123456",
         "target_account": "z00123456", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "李四", "staff_name": "lisi 00765432",
         "target_account": "l00765432", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "王五", "staff_name": "wangwu 00818094",
         "target_account": "w00818094", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "赵六", "staff_name": "zhaoliu 00574872",
         "target_account": "z00574872", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "陈七", "staff_name": "chenqi 00987654",
         "target_account": "c00987654", "cross_instance": False},
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


def _now_ms() -> int:
    return int(time.time() * 1000)


_MY_ACCOUNT = "q00510847"

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

# ── Per-session message scripts (for digest mock) ─────────────────────────────
# Each entry: (sender, content, at_me, at_all)
# at_me = True means the message is directed at _MY_ACCOUNT
# at_all = True means @所有人

_DIGEST_SCRIPTS: dict[str, list[tuple[str, str, bool, bool]]] = {
    "944052726495445547": [  # 产品需求讨论群
        ("z00123456", "新版本的 PRD 已经同步到 iWiki，大家今天看一下，有疑问随时提", False, False),
        ("l00765432", "收到，我下午过一遍", False, False),
        ("w00987654", "第 3 节关于权限模型的描述有点模糊，具体是 RBAC 还是 ABAC？", False, False),
        ("z00123456", "目前规划是 RBAC，后续再考虑 ABAC 扩展", False, False),
        ("q00510847", "好的，我来更新技术方案里的权限部分", False, False),
        ("l00765432", "@所有人 需求评审时间改到周四下午 2 点，请提前准备", False, True),
        ("w00987654", "登录模块的交互稿什么时候能出？设计那边等着接入", False, False),
    ],
    "708543592267911909": [  # 技术架构评审
        ("l00765432", "微服务拆分的方案我更新了，放在 confluence 上", False, False),
        ("z00123456", "看了，网关层的限流策略还需要细化", False, False),
        ("l00765432", "这个我明天补上。另外 @q00510847 你那边 CI 流水线的适配进度怎么样了？", True, False),
        ("q00510847", "CI 流水线已经跑通了，Jenkinsfile 在 review 中", False, False),
        ("w00987654", "Redis 集群的容量规划做了吗？预计 Q3 峰值 QPS 到 50K", False, False),
        ("z00123456", "这个还没评估，谁有空帮忙算一下？", False, False),
        ("l00765432", "我们用的是 Codis 还是原生 Cluster？这个会影响容量模型", False, False),
    ],
    "675805850476069040": [  # AI 项目推进组
        ("w00987654", "vLLM 的 PoC 结果出来了，延迟从 800ms 降到了 180ms", False, False),
        ("q00510847", "效果不错！吞吐量有测试吗？", False, False),
        ("w00987654", "吞吐在 H20 上大概是 2300 tokens/s，还有优化空间", False, False),
        ("z00123456", "下周一的演示就用这个版本吧，@q00510847 帮忙准备一下 demo 脚本", True, False),
        ("q00510847", "没问题，我周五前准备好", False, False),
        ("l00765432", "模型服务的监控告警也要加上，目前只有基础的 CPU/Mem", False, False),
        ("w00987654", "这个我来，用 Prometheus + Grafana", False, False),
        ("z00123456", "好，那我们下周一评审这三个：vLLM 效果、Demo 脚本、监控方案", False, False),
    ],
    "834854760434885793": [  # 开源技术交流群
        ("q00510847", "分享一个不错的 Rust web 框架：https://github.com/tokio-rs/axum", False, False),
        ("l00765432", "Axum 确实好用，我们内部工具链已经在用了", False, False),
        ("z00123456", "有没有 Go 的类似推荐？", False, False),
        ("w00987654", "Go 的话 Fiber 或者 Chi 都不错", False, False),
        ("z00123456", "好的我看看，谢谢", False, False),
        ("q00510847", "这周的 Rust 中国社区 meetup 有人去吗？", False, False),
        ("l00765432", "我报名了，周六下午", False, False),
    ],
    "717915662353219752": [  # 前端技术交流
        ("w00987654", "微前端架构选型，大家觉得 qiankun 还是 Module Federation？", False, False),
        ("z00123456", "我们项目用的 qiankun，坑比较多但不至于不能用", False, False),
        ("q00510847", "Module Federation 在 Webpack 5 上很成熟了，推荐", False, False),
        ("l00765432", "有没有实际落地案例？担心兼容性问题", False, False),
        ("w00987654", "React 18 的 Server Components 你们用上了吗？", False, False),
        ("z00123456", "还没，我们的 Next.js 版本太老了", False, False),
        ("q00510847", "我们升级到 Next 14 了，RSC 体验不错，不过有些三方库不兼容", False, False),
    ],
    "758559285016953862": [  # 团队管理群
        ("z00123456", "@所有人 周五前提交 Q2 OKR 自评，格式参照模板", False, True),
        ("l00765432", "好的，模板在哪里？", False, False),
        ("z00123456", "在 iWiki 上搜「Q2 OKR 自评模板」", False, False),
        ("w00987654", "我这边有几个跨团队协作的目标，怎么写比较合适？", False, False),
        ("z00123456", "跨团队的目标标注一下协作方就行", False, False),
        ("q00510847", "收到，我周五前提交", False, False),
        ("l00765432", "@q00510847 上次说的入职培训材料更新了吗？新人下周就到了", True, False),
        ("q00510847", "还在整理，明天发出来", False, False),
    ],
    "823456789012345678": [  # DevOps 实践
        ("w00987654", "GitHub Actions 的自托管 runner 搭好了，比 SaaS 快 3 倍", False, False),
        ("q00510847", "赞，能不能分享一下配置？我们也在考虑", False, False),
        ("w00987654", "稍后我把 Dockerfile 和 k8s manifest 发到群里", False, False),
        ("l00765432", "安全扫描集成进去了吗？", False, False),
        ("w00987654", "Trivy 已经接了，每次 PR 自动扫", False, False),
        ("z00123456", "Artifactory 的存储快满了，谁清理一下旧的 snapshot？", False, False),
    ],
    "912345678901234567": [  # 数据平台建设
        ("l00765432", "Flink CDC 接 MySQL 的延迟有多大？", False, False),
        ("w00987654", "我们测下来大概是 200-500ms，取决于 binlog 量", False, False),
        ("l00765432", "那还行，满足我们的需求", False, False),
        ("z00123456", "数据湖选型定了吗？Hudi 还是 Iceberg？", False, False),
        ("q00510847", "还在评估，下周出一个对比报告", False, False),
        ("z00123456", "好，注意对比一下 upsert 性能和查询引擎兼容性", False, False),
    ],
}

# Private chat scripts — keyed by target_account
_P2P_SCRIPTS: dict[str, list[tuple[str, str]]] = {
    "z00123456": [  # 张三 — Q2 report discussion
        ("q00510847", "张三，Q2 的汇总报告你那边数据齐了吗？"),
        ("z00123456", "差不多了，还差运维团队的故障统计"),
        ("q00510847", "那个我催一下运维，今天下班前给你"),
        ("z00123456", "好的，我这周三前能出完整版"),
        ("q00510847", "对了，报告中要单列 AI 相关的投入产出"),
        ("z00123456", "明白，我加一个专项章节"),
    ],
    "l00765432": [  # 李四 — lunch (closed)
        ("l00765432", "中午一起吃饭？食堂有新开的湘菜窗口"),
        ("q00510847", "好啊，12 点大厅碰头"),
        ("l00765432", "OK，叫上王五一起"),
        ("q00510847", "行，我跟他说"),
    ],
    "w00818094": [  # 王五 — asking for help, NO response (unclosed!)
        ("w00818094", "老哥，你们那个权限中台的接口文档能发我一份吗？"),
        ("q00510847", "可以，在 iWiki 上搜「权限中台 API 文档 v2.3」"),
        ("w00818094", "找到了，谢谢！对了，鉴权那块是用 JWT 还是 OAuth2？"),
        ("w00818094", "我们这边准备对接，不太确定用哪种方式"),
        ("w00818094", "？看到回一下，比较急"),
    ],
    "z00574872": [  # 赵六 — file sharing (closed)
        ("q00510847", "赵六，上次说的性能测试报告我发你了"),
        ("z00574872", "收到，我看了，吞吐量比预期低了 20%"),
        ("q00510847", "对，怀疑是数据库连接池配置的问题，我在排查"),
        ("z00574872", "有结果了同步我一下"),
        ("q00510847", "好的"),
    ],
    "c00987654": [  # 陈七 — new member onboarding
        ("c00987654", "Hi，我是新加入基础设施组的陈七"),
        ("q00510847", "欢迎！有什么需要帮助的吗？"),
        ("c00987654", "想了解一下我们目前的发布流程，有没有文档可以参考？"),
        ("q00510847", "有，我发你一个链接：https://iwiki.huawei.com/pages/release-flow"),
        ("c00987654", "感谢！我看完有疑问再请教你"),
    ],
}


def _generate_mock_messages(group_id: str, count: int = 20) -> list[dict]:
    """Generate synthetic messages for a given group.

    Uses per-session scripts from _DIGEST_SCRIPTS when available,
    otherwise falls back to the generic _MOCK_MESSAGE_POOL.
    """
    base_ms = _now_ms()
    messages = []

    script = _DIGEST_SCRIPTS.get(group_id)
    if script:
        for i, (sender, content, at_me, at_all) in enumerate(script):
            messages.append({
                "at": at_me or at_all,
                "atAccountList": [_MY_ACCOUNT] if at_me else [],
                "content": content,
                "contentType": "TEXT_MSG",
                "groupId": int(group_id),
                "groupType": 0,
                "msgId": 0,  # filled below
                "receiver": "",
                "sender": sender,
                "serverSendTime": base_ms - i * 120000,
            })
    else:
        for i in range(count):
            content, sender = _MOCK_MESSAGE_POOL[i % len(_MOCK_MESSAGE_POOL)]
            is_at = "@" in content and "所有人" in content
            messages.append({
                "at": is_at,
                "atAccountList": [],
                "content": content,
                "contentType": "TEXT_MSG",
                "groupId": int(group_id),
                "groupType": 0,
                "msgId": 0,
                "receiver": "",
                "sender": sender,
                "serverSendTime": base_ms - i * 60000,
            })

    for i, m in enumerate(messages):
        m["msgId"] = int(f"{hash(group_id) % 10000}{base_ms - i * 60000:013d}"[:17])
    return messages


def _generate_p2p_messages(target_account: str, count: int = 10) -> list[dict]:
    """Generate synthetic private-chat messages using per-contact scripts."""
    base_ms = _now_ms()
    messages = []

    script = _P2P_SCRIPTS.get(target_account)
    if script:
        for i, (sender, content) in enumerate(script):
            is_me = sender == _MY_ACCOUNT
            messages.append({
                "at": False,
                "atAccountList": [],
                "content": content,
                "contentType": "TEXT_MSG",
                "groupId": 0,
                "groupType": 0,
                "msgId": 0,
                "receiver": target_account if is_me else _MY_ACCOUNT,
                "sender": sender,
                "serverSendTime": base_ms - i * 180000,
            })
    else:
        for i in range(min(count, 5)):
            content, sender = _MOCK_MESSAGE_POOL[i % len(_MOCK_MESSAGE_POOL)]
            messages.append({
                "at": False,
                "atAccountList": [],
                "content": content,
                "contentType": "TEXT_MSG",
                "groupId": 0,
                "groupType": 0,
                "msgId": 0,
                "receiver": target_account if sender == _MY_ACCOUNT else _MY_ACCOUNT,
                "sender": sender,
                "serverSendTime": base_ms - i * 180000,
            })

    for i, m in enumerate(messages):
        m["msgId"] = int(f"99{hash(target_account) % 10000}{base_ms - i * 60000:011d}"[:17])
    return messages


# ── Public API ─────────────────────────────────────────────────────────────────


async def get_sessions(limit: int = 50) -> dict:
    """Fetch recent conversations. Mirrors `welink-cli im query-recent-conversation`."""
    if _MOCK_ENABLED:
        sessions = _MOCK_SESSIONS.copy()
        sessions["conversation_info"] = sessions["conversation_info"][:limit]
        return sessions
    # TODO: Real implementation via subprocess:
    # result = subprocess.run(
    #     f"welink-cli im query-recent-conversation --count {limit}",
    #     shell=True, capture_output=True, text=True
    # )
    # return json.loads(result.stdout)
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
        msg_id: pagination cursor
        direction: 0=older, 1=newer
        is_group: True for group chat, False for private chat
    """
    if _MOCK_ENABLED:
        if is_group:
            messages = _generate_mock_messages(target, count)
        else:
            messages = _generate_p2p_messages(target, count)
        msg_ids = [m["msgId"] for m in messages]
        max_id = max(msg_ids) if msg_ids else 0
        min_id = min(msg_ids) if msg_ids else 0
        return {
            "respData": {
                "chatInfo": messages,
                "maxMsgId": max_id,
                "minMsgId": min_id,
                "msgTotalCount": len(messages),
            },
            "resultCode": "0",
            "resultContext": "Operate Success",
        }
    # TODO: Real implementation via subprocess:
    # if is_group:
    #     cmd = f"welink-cli im query-history-message --group-id {target} --query-count {count}"
    # else:
    #     cmd = f"welink-cli im query-history-message --user-account {target} --query-count {count}"
    # result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # return json.loads(result.stdout)
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
