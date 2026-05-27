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
        {"recent_conversation_type": "CHAT_TYPE_P2P_MSG", "group_id": "0",
         "group_name": "", "group_type": "NORMAL_GROUP",
         "native_name": "张洋洋", "staff_name": "zhangyangyang 00628533",
         "target_account": "z00628533", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "944052726495445547",
         "group_name": "无线设计桌面模块内审", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "708543592267911909",
         "group_name": "工具二部团队建设群", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "675805850476069040",
         "group_name": "ALM&AI 2025", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "717915662353219752",
         "group_name": "ALM&AI 2025全员", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "758559285016953862",
         "group_name": "无线设计技术交流群", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "834854760434885793",
         "group_name": "工具二部全员群", "group_type": "NORMAL_GROUP",
         "native_name": "", "staff_name": "", "target_account": "", "cross_instance": False},
        {"recent_conversation_type": "CHAT_TYPE_GROUP_MSG", "group_id": "823456789012345678",
         "group_name": "CI/CD 流水线讨论组", "group_type": "NORMAL_GROUP",
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
    "944052726495445547": [  # 无线设计桌面模块内审
        ("z00123456", "桌面模块 v2.3 的内审材料已经上传了，大家这周内完成评审", False, False),
        ("l00765432", "收到，我负责 UI 一致性检查那部分", False, False),
        ("w00987654", "模块间接口文档是不是还没更新？我这边对不上", False, False),
        ("z00123456", "接口文档我来催一下架构组，争取明天更新", False, False),
        ("q00510847", "我这里有个兼容性测试的结论，已同步到附件", False, False),
        ("l00765432", "@所有人 评审截止时间延长到周五下班前，大家合理安排", False, True),
        ("w00987654", "请问故障注入测试的用例谁来写？这部分一直没人认领", False, False),
    ],
    "708543592267911909": [  # 工具二部团队建设群
        ("l00765432", "这次团建定在下周六，大家投票选一下：爬山还是轰趴？", False, False),
        ("z00123456", "爬山！上次去阳台山体验很好", False, False),
        ("w00987654", "轰趴 +1，夏天爬山太热了", False, False),
        ("q00510847", "轰趴吧，人数多室内好组织", False, False),
        ("l00765432", "好，那暂定轰趴，我明天出详细方案。@q00510847 帮忙统计一下参加人数", True, False),
        ("q00510847", "没问题，今晚发统计表到群里", False, False),
        ("w00987654", "经费预算批下来了吗？上次说这周会有结果", False, False),
    ],
    "675805850476069040": [  # ALM&AI 2025
        ("w00987654", "vLLM 推理服务的 PoC 跑通了，H20 上延迟 180ms，比预期好", False, False),
        ("q00510847", "不错，吞吐量测了吗？我们需要单卡支撑 100+ 并发", False, False),
        ("w00987654", "目前 2300 tokens/s，并发 64 没问题，再高需要多卡", False, False),
        ("z00123456", "下周给领导演示就用这个版本，@q00510847 准备 Demo 脚本和 slides", True, False),
        ("q00510847", "好的，我周四前出一版", False, False),
        ("l00765432", "模型服务的可观测性也要跟上，目前只有基础指标", False, False),
        ("w00987654", "Prometheus + Grafana 的方案我这周搭出来", False, False),
        ("z00123456", "好，下周评审三个：PoC 数据、Demo 材料、监控方案", False, False),
    ],
    "834854760434885793": [  # 工具二部全员群
        ("z00123456", "@所有人 部门季度总结会定在下周三下午 2 点，地点 3F 大会议室", False, True),
        ("l00765432", "收到，需要提前准备什么材料吗？", False, False),
        ("z00123456", "各小组准备 5 分钟的进展汇报 slides", False, False),
        ("w00987654", "我们组这季度主要做了推理优化，数据我整理一下", False, False),
        ("q00510847", "收到，我这边整理 Q2 的交付清单", False, False),
    ],
    "717915662353219752": [  # ALM&AI 2025全员
        ("z00123456", "欢迎新同事加入 ALM&AI 团队！本周五下午有新人介绍会", False, False),
        ("w00987654", "欢迎欢迎，新同学是做哪个方向的？", False, False),
        ("l00765432", "好像是做模型评估的，之前在大厂做过类似工作", False, False),
        ("q00510847", "欢迎！有什么需要帮忙的随时找我", False, False),
        ("z00123456", "@所有人 本周五 4 点，3F 茶水间，新人欢迎会，大家尽量参加", False, True),
        ("w00987654", "收到，我准备一下团队介绍 slides", False, False),
    ],
    "758559285016953862": [  # 无线设计技术交流群
        ("l00765432", "有没有人用过新的天线仿真工具 HFSS 2025？据说速度快了不少", False, False),
        ("w00987654", "我用过 beta 版，求解器的精度提高了，但 GPU 加速还没适配好", False, False),
        ("z00123456", "我们项目还在用 2023 版本，升级需要 license 重新申请吗？", False, False),
        ("w00987654", "不需要，同一个 license server 可以直接激活", False, False),
        ("q00510847", "我这边有份 HFSS 2025 的迁移指南，稍后发上来", False, False),
        ("l00765432", "好人一生平安，正好需要", False, False),
        ("w00987654", "对了，下周有天线设计 workshop，有人一起去吗？", False, False),
    ],
    "823456789012345678": [  # CI/CD 流水线讨论组
        ("w00987654", "自建 runner 跑起来了，构建时间从 12 分钟降到了 4 分钟", False, False),
        ("q00510847", "这个提升太明显了，镜像拉取是走的内网缓存？", False, False),
        ("w00987654", "对，Harbor 做了镜像预热，大镜像也能秒拉", False, False),
        ("l00765432", "安全扫描那步的 Trivy 能并行跑吗？现在串行太慢了", False, False),
        ("w00987654", "我已经改了，新配置下 Trivy 和 SonarQube 并行执行", False, False),
        ("z00123456", "帮忙把配置模板同步到 wiki 上吧，其他组也想接入", False, False),
    ],
}

# Private chat scripts — keyed by target_account
_P2P_SCRIPTS: dict[str, list[tuple[str, str]]] = {
    "z00628533": [  # 张洋洋
        ("z00628533", "你好，你那边有根据工号查询个人信息的工具吗？"),
        ("q00510847", "有，我发你一个 Excel 宏"),
        ("q00510847", "[文件] 根据工号查询个人信息_Office2013版本.xlsm"),
        ("z00628533", "吗的这玩意儿咋看"),
        ("q00510847", "我看下"),
        ("q00510847", "打开后启用宏，然后在 A1 格输入工号就行"),
        ("z00628533", "OK 我试试"),
    ],
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
        ("w00818094", "怎么说，能看到不，走完没"),
    ],
    "z00574872": [  # 赵六 — file sharing (closed)
        ("q00510847", "赵六，上次说的性能测试报告我发你了"),
        ("z00574872", "收到，我看了，吞吐量比预期低了 20%"),
        ("q00510847", "对，怀疑是数据库连接池配置的问题，我在排查"),
        ("z00574872", "有结果了同步我一下"),
        ("q00510847", "好的"),
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
