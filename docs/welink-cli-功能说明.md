## 一、功能

| 类别       | 能力                                                     |
| :--------- |:-------------------------------------------------------|
| 📅 会议     | 查询会议议题、议题材料、会议信息、分页会议列表、会议管理（增/删/改）、议题管理（增/删/改）        |
| 🔍 搜索     | 搜索联系人、搜索群组                                             |
| 👤 联系人   | 查询用户详情、特别关注管理（添加/删除/查询列表）                                  |
| 💬 消息     | 发送消息、创建群组、查询会话、查询群组成员、查看聊天记录、添加群成员                                  |
| 📁 云空间   | 上传下载文件、管理文件和文件夹、查看空间信息、文件操作（复制/移动/重命名文件/外链分享）、空间相关（搜索空间文件/文件夹）|                                 |
| 📧 邮件日历 | Autodiscover、查询邮箱文件夹、获取邮件列表、获取邮件详情、发送邮件、下载（将指定附件下载到本地指定目录）、邮件管理（回复/转发/移动）、日历列表、日历详情、创建日历 |
| 🔧 版本检查 | 检查CLI版本是否过期，自动更新到最新版本                                  |



## 二、安装与快速开始

### 环境要求

开始之前，请确保具备以下条件：

- Node.js（`npm`/`npx`）(参考链接:https://3ms.huawei.com/km/blogs/details/22148443)
- WeLink PC升级到7.34.12及以上版本(https://onebox.huawei.com/v/6707a442f30ff1736bd5f5b300925822/list)
- 管理员权限运行powershell 执行 Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned 命令，选择Y。配置好后关闭powershell，以下操作以普通权限运行powershell或cmd操作。![image](/uploads/a51cb69d-a66f-4280-91ad-ee854533f786/1779155285207.png '1779155285207.png')

### 快速开始（人类用户）

#### 安装

**npm 安装：**

```bash
# 安装/更新 WeLink-CLI
npm install -g @welink/welink-cli --registry=https://cmc.centralrepo.rnd.huawei.com/artifactory/api/npm/product_npm/ --strict-ssl=false

# 查看 WeLink-CLI 版本, 目前最新版本为1.0.14
welink-cli --version
```

#### 配置与使用

```bash
# 1. 登录授权（WeLink移动端扫码登录，默认生产环境）
welink-cli auth login

# 2. 开始使用
welink-cli im send-to-user --receiver "XXX" --text "hello welink-cli"
```

### 快速开始（员工助手）

```bash
# 登录授权（指定生产环境）
welink-cli auth login --env pro

# 开始使用
welink-cli im send-to-user --receiver "XXX" --text "hello welink-cli"
```



## 三、认证

WeLink CLI 使用 OAuth2.0 + WebSocket 进行认证管理。

### 认证命令

| 命令          | 说明                                         |
| ------------- | -------------------------------------------- |
| `auth login`  | 通过 WeLink 移动端扫码授权，用户需配合操作 |
| `auth status` | 查看当前登录状态和已授权的 scope             |
| `auth logout` | 注销登录并清除所有存储的凭证                 |

### 登录授权

**命令格式：**
```bash
welink-cli auth login [--env TEXT]
```

**参数说明：**
- `--env TEXT`：指定环境，可选值为 `pro`（生产环境）
- 如不指定 `--env` 参数，将使用默认环境配置

**使用示例：**
```bash
# 使用默认环境登录
welink-cli auth login

# 指定生产环境登录
welink-cli auth login --env pro

```

**操作流程：**
1. 执行登录命令后，CLI 会生成二维码
2. 使用 WeLink 移动端扫描二维码
3. 在移动端确认授权
4. 授权成功后，CLI 会保存认证信息

### 查看认证状态

**命令格式：**
```bash
welink-cli auth status
```

**使用示例：**
```bash
welink-cli auth status
```

该命令会显示当前的登录状态、用户信息以及已授权的 scope 权限范围。

### 注销登录

**命令格式：**
```bash
welink-cli auth logout
```

**使用示例：**
```bash
welink-cli auth logout
```

该命令会清除所有存储的凭证和配置文件，包括：
- 用户 token 和 refresh token
- WebSocket sign 和 nonce
- 加密密钥存储
- 配置文件（config.json 和 credentials.json）

**注意**：注销后需要重新执行 `auth login` 才能继续使用 CLI。



## 四、三层命令调用

CLI 提供三种粒度的调用方式，覆盖从快速操作到完全自定义的全部场景：

### 1. 快捷命令（Shortcuts）

WeLink CLI 提供了简洁易用的命令别名，方便快速执行常用操作：

**消息快捷命令：**
```bash
# 发送文本消息给用户
welink-cli im send-to-user --receiver "user001" --text "Hello WeLink"

# 发送图片给用户
welink-cli im send-to-user --receiver "user001" --image "./photo.png"

# 发送文件给用户
welink-cli im send-to-user --receiver "user001" --file "./document.pdf"

# 发送消息给群组
welink-cli im send-to-group --group-id "group001" --text "Group message"

# 发送图片给群组
welink-cli im send-to-group --group-id "group001" --image "./photo.png"

# 发送文件给群组
welink-cli im send-to-group --group-id "group001" --file "./document.pdf"

# 查询最近会话
welink-cli im query-recent-conversation

# 查询历史消息
welink-cli im query-history-message --user-account "a0012345" --query-count 20
welink-cli im query-history-message --group-id "1234567891011" --query-count 20

# 创建群组
welink-cli im create-group --name "测试群" --user-account "a0012345" "b0067890" --notice "测试群公告" --type 0

# 查询群组成员
welink-cli im query-group-member --group-id "1234567891011"

# 添加群组成员
welink-cli im add-group-member --group-id "1234567891011" --user-account "c0011111" "d0022222"
```

**会议快捷命令：**

```bash
# 重要：cli 接口中所有的meeting-id皆为会议主键，非视频会议号
# 创建会议，下面参数都是必传
welink-cli meeting create --start-time 1778378400000 --end-time 1778382000000 --subject welink-cli测试创建会议 --meeting-user-list c00899563 t00845328

# 修改会议，其中meetingId是必传的，其余的都是非必传，比如只传subject，那就说明只更新这个会议的名称，只传meeting-user-list说明只更新会议与会人信息
welink-cli meeting update --meeting-id 203422177 --start-time 1777100400000 --end-time 1777104000000 --subject 更新后的主题 --meeting-user-list c00899563 t00845328

# 取消会议，其中meetingId是必传的
welink-cli meeting cancel --meeting-id 184521460

# 分页查询会议，都是必传的参数，其中type表示的含义：0-公开的会议、1-待参加的会议、2-已结束的会议、3-我预定的会议、4-所有的会议、5-我管理的会议
welink-cli meeting query-list --meeting-start-time 1767196800000 --meeting-end-time 1798732799999 --type 1 --meeting-sort asc --page 1 --size 15

# 查询会议详情
welink-cli meeting info --meeting-id 184531461

# 模糊搜索会议，根据会议主题模糊搜索时间范围内的相关会议
welink-cli meeting fuzzy-search --result-type meeting --limit 10 --offset 0 --search-type subject --search-content 代码QC --search-type startTime --search-content 1774972800000 --search-type endTime --search-content 1775664000000

# 创建议题，都是必传参数
welink-cli meeting topic-create --meeting-id 203422177 --topic-name 议题名称 --topic-category 汇报类 --topic-member-list c00899563 t00845328

# 删除议题，都是必传参数
welink-cli meeting topic-delete --meeting-id 203422177 --topic-id 88711297

# 修改议题，其中meetingId和topicId是必传的，其余的都是非必传，比如只传topic-name，那就说明只更新这个议题的名称，只传topic-member-list说明只更新议题的汇报人信息
welink-cli meeting topic-update --meeting-id 203422177 --topic-id 88711297 --topic-name 更新后的议题名称 --topic-category 汇报类 --topic-member-list c00899563 t00845328

# 查询会议下议题信息，重要：meeting-id非视频会议号
welink-cli meeting topic --meeting-id 184531461

# 查询会议下，指定议题材料信息，重要：meeting-id非视频会议号
welink-cli meeting topic-materials --meeting-id 202674731 --topic-id 88520416
```

**云空间快捷命令：**
```bash
# 获取个人空间信息（可优先使用该命令获取个人空间id，取 cloudUserId 字段）
welink-cli onebox user-info

# 上传文件（space-id填上述命令 cloudUserId，parent为父文件夹id，0表示根目录，其他目录id可使用 folder-list 命令获取）
welink-cli onebox file-upload --space-id 123 --parent 0 "./report.pdf"

# 下载文件（空间ID+文件ID唯一决定一个云盘文件）
welink-cli onebox file-download --space-id 123 --file-id 456 --output "./download/"

# 获取文件信息
welink-cli onebox file-info --space-id 123 --file-id 456

# 列出文件夹内容
welink-cli onebox folder-list --space-id 123 --folder-id 0 --offset 0 --limit 20

# 复制文件
welink-cli onebox file-copy --space-id 123 --file-id 456 \
  --dest-parent 789 --dest-space-id 123

# 移动文件
welink-cli onebox file-move --space-id 123 --file-id 456 \
  --dest-parent 789 --dest-space-id 123

# 重命名文件
welink-cli onebox file-rename --space-id 123 --file-id 456 --name "新文件名.pdf"

# 删除文件（移到回收站）
welink-cli onebox file-remove --space-id 123 --file-id 456

# 创建新文件夹
welink-cli onebox folder-new --space-id 123 --parent 0 --name "新文件夹"

# 重命名文件夹
welink-cli onebox folder-rename --space-id 123 --folder-id 789 --name "新文件夹名"

# 删除文件夹（移到回收站）
welink-cli onebox folder-remove --space-id 123 --folder-id 789

# 搜索文件和文件夹
welink-cli onebox node-search --space-id 123 --name "报告" \
  --offset 0 --limit 100
```


**邮件快捷命令：**
```bash
# 首次使用前，必须执行 autodiscover 获取邮箱服务器
welink-cli mail autodiscover --email user@example.com

# 查看收件箱
welink-cli mail list
# 查看更多邮件
welink-cli mail list --max 50

# 搜索未读邮件
welink-cli mail list --is-read 0

# 按发件人筛选
welink-cli mail list --from boss@example.com

# 查看已发送邮件
welink-cli mail list --folder-id sentitems

# 查看自定义文件夹（推荐：先用 mail folders 拿真实 FolderId）
welink-cli mail folders
welink-cli mail list --folder-id <从上一步复制的 FolderId>

# 查看邮件详情（ItemId 从 mail list 获取）
welink-cli mail get --item-id <ItemId>

# 简单发送
welink-cli mail send --to user@example.com --subject "Hello" --body "Hi there"

# 多收件人（逗号分隔）
welink-cli mail send --to "a@example.com,b@example.com" --subject "通知" --body "内容"

# 带抄送和附件
welink-cli mail send --to user@example.com --cc mgr@example.com \
  --subject "报告" --body "见附件" -a report.pdf -a data.xlsx

# HTML 正文（启用 --html 时 --body 要写 HTML 标记，不启用则按纯文本）
welink-cli mail send --to user@example.com --subject "通知" \
  --body "<h1>标题</h1><p>内容</p>" --html

# 下载附件到目录（使用原始文件名）
welink-cli mail attachment --attachment-id <AttachmentId> --path ./downloads/

# 下载附件到指定文件名
welink-cli mail attachment --attachment-id <AttachmentId> --path report.pdf

# 回复
welink-cli mail reply --item-id <ItemId> --body "已收到，谢谢"

# 回复全部
welink-cli mail reply-all --item-id <ItemId> --body "同意"

# HTML 回复
welink-cli mail reply --item-id <ItemId> --body "<p>已收到</p>" --html

# 自定义主题（不再带 RE:/FW: 前缀）
welink-cli mail reply --item-id <ItemId> --subject "周报反馈" --body "已阅"

# 回复/转发追加附件（reply / reply-all / forward 通用）
welink-cli mail reply --item-id <ItemId> --body "补充材料" -a ./report.pdf
welink-cli mail forward --item-id <ItemId> --to peer@example.com   --body "增加封面" -a ./cover.pdf

# 转发（自动包含原始附件）
welink-cli mail forward --item-id <ItemId> --to colleague@example.com --body "请查阅"

# 转发 + 抄送
welink-cli mail forward --item-id <ItemId> --to colleague@example.com --cc mgr@example.com --body "附件转发"

# 移动到草稿箱
welink-cli mail move --item-id <ItemId> --folder-id drafts

# 移动到自定义文件夹（FolderId 从 mail folders 获取）
welink-cli mail move --item-id <ItemId> --folder-id <FolderId>



```

**日历快捷命令：**
```bash
# 首次使用前，必须执行 autodiscover 获取邮箱服务器
welink-cli mail autodiscover --email user@example.com

# 查看本周日历
welink-cli calendar list

# 指定日期范围（注意 --end 不含当天，写 5/1 才覆盖到 4/30）
welink-cli calendar list --start 2026-04-01 --end 2026-05-01

# 单天查询：查 5/8 当天 → --end 写次日 5/9
welink-cli calendar list --start 2026-05-08 --end 2026-05-09

# 查看事件详情（ItemId 从 calendar list 获取）
welink-cli calendar get --item-id <ItemId>

# 创建个人日程
welink-cli calendar create --subject "专注时间" \
  --start 2026-04-10T09:00:00 --end 2026-04-10T11:00:00

# 创建会议（自动发送邀请）
welink-cli calendar create --subject "代码评审" \
  --start 2026-04-10T14:00:00 --end 2026-04-10T15:00:00 \
  --location "会议室 A" --attendee "alice@example.com,bob@example.com"

# JSON 格式输出（--format 在 mail/calendar 后、子命令前）
welink-cli mail --format json list
welink-cli calendar --format json list

```

**搜索快捷命令：**
```bash
# 搜索联系人
welink-cli search person --text "张三"

# 搜索群组
welink-cli search group --text "项目组"

# 指定返回数量搜索
welink-cli search person --text "z00123456" --page-size 50

# 搜索特定类型的群组
welink-cli search group --text "测试" --type 0
```

**联系人快捷命令：**
```bash
# 查询用户详情
welink-cli contact detail userwelinkid_1

# 查询多个用户详情
welink-cli contact detail userwelinkid_1 userwelinkid_2

# 添加特别关注
welink-cli contact add_favorite userwelinkid_1

# 删除特别关注
welink-cli contact del_favorite userwelinkid_1

# 查询特别关注列表
welink-cli contact favorite_list

# 查询特别关注列表（分页）
welink-cli contact favorite_list --pageIndex 2 --pageSize 50
```


### 2. 命令层级结构

WeLink CLI 采用清晰的命令层级结构：

```
welink-cli
├── config          # 配置管理
│   ├── show                    # 显示当前配置
│   ├── init                    # 初始化并检查环境
│   └── timeout                 # WebSocket 超时配置
│       ├── show                # 显示超时配置
│       ├── set                 # 设置超时参数
│       └── reset               # 重置超时参数
├── auth            # 认证管理
│   ├── login                   # 扫码登录
│   ├── status                  # 查看认证状态
│   └── logout                  # 注销登录
├── im              # 即时通讯
│   ├── send-to-user
│   ├── send-to-group
│   ├── create-group
│   ├── query-recent-conversation
│   ├── query-group-member
│   ├── query-history-message
│   └── add-group-member
├── meeting         # 会议
│   ├── info
│   ├── query-list
│   ├── fuzzy-search
│   ├── create
│   ├── update
│   ├── cancel
│   ├── topic
│   ├── topic-create
│   ├── topic-update
│   ├── topic-delete
│   └── topic-materials
├── contact         # 联系人
│   ├── detail                  # 查询用户详情
│   ├── add_favorite            # 添加特别关注
│   ├── del_favorite            # 删除特别关注
│   └── favorite_list           # 查询特别关注列表
├── search          # 搜索功能
│   ├── person
│   └── group
├── onebox          # 云空间
│   ├── file-upload
│   ├── file-download
│   ├── file-info
│   ├── file-copy
│   ├── file-move
│   ├── file-rename
│   ├── file-remove
│   ├── file-share-link-get
│   ├── file-share-link-edit
│   ├── file-share-link-remove
│   ├── folder-list
│   ├── folder-new
│   ├── folder-rename
│   ├── folder-remove
│   ├── user-info
│   └── node-search
├── mail            # 邮件
│   ├── autodiscover
│   ├── list
│   ├── get
│   ├── send
│   ├── reply
│   ├── reply-all
│   ├── forward
│   ├── attachment
│   ├── move
│   ├── delete
│   ├── mark
│   └── folders
├── calendar        # 日历
│   ├── list
│   ├── get
│   └── create
└── version         # 版本检查
    └── check                   # 检查 CLI 版本是否过期
```

**使用说明：**
- 每个主命令（如 `im`、`meeting`）下都有多个子命令
- 执行命令时必须指定子命令，例如 `welink-cli im send-to-user`
- 使用 `--help` 查看命令的详细帮助信息
- 使用 `welink-cli --version` 查看版本信息



## 五、命令详解

### 配置命令（config）

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `config show` | 显示当前配置 | 无 |
| `config init` | 初始化并检查 CLI 环境 | 无 |
| `config timeout show` | 显示 WebSocket 超时配置 | 无 |
| `config timeout set` | 设置 WebSocket 超时参数 | `key`: 参数名<br>`value`: 超时值（毫秒） |
| `config timeout reset` | 重置 WebSocket 超时参数为默认值 | `--all`: 重置所有参数<br>或 `key`: 参数名 |

**配置示例：**
```bash
# 查看当前配置
welink-cli config show

# 初始化并检查 CLI 环境
welink-cli config init

# 查看 WebSocket 超时配置
welink-cli config timeout show

# 设置 WebSocket 超时参数
welink-cli config timeout set ws-connect-timeout 5000

# 重置所有超时参数为默认值
welink-cli config timeout reset --all
```

**WebSocket 超时参数说明：**

| 参数名 | 默认值 | 有效范围 | 说明 |
|--------|--------|----------|------|
| `ws-connect-timeout` | 3000ms | 100-30000ms | WebSocket 连接超时 |
| `ws-verify-timeout` | 30000ms | 1000-120000ms | WebSocket 验证超时 |
| `ws-receive-timeout` | 5000ms | 100-60000ms | WebSocket 接收超时 |
| `ws-close-timeout` | 3000ms | 100-10000ms | WebSocket 关闭超时 |

### 认证命令（auth）

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `auth login` | 通过 WeLink 移动端扫码授权 | `--env`: 指定环境（可选） |
| `auth status` | 查看当前登录状态和已授权的 scope | 无 |
| `auth logout` | 注销登录并清除所有存储的凭证 | 无 |

**认证示例：**
```bash
# 使用默认环境登录
welink-cli auth login

# 指定生产环境登录
welink-cli auth login --env pro

# 查看认证状态
welink-cli auth status

# 注销登录
welink-cli auth logout
```

### IM 消息命令

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `im send-to-user` | 发送消息给用户（支持文本、图片、文件） | `--receiver`: 接收者账号<br>`--text`: 消息内容（文本）<br>`--image`: 图片路径（可选）<br>`--file`: 文件路径（可选） |
| `im send-to-group` | 发送消息给群组（支持文本、图片、文件） | `--group-id`: 群组ID<br>`--text`: 消息内容（文本）<br>`--image`: 图片路径（可选）<br>`--file`: 文件路径（可选） |
| `im create-group` | 创建新群组 | `--name`: 群组名称<br>`--user-account`: 成员账号列表<br>`--notice`: 群公告<br>`--type`: 群类型（0-普通群，1-讨论群） |
| `im query-recent-conversation` | 查询最近会话 | `--count`: 查询数量（可选，默认10） |
| `im query-group-member` | 查询群组成员 | `--group-id`: 群组ID |
| `im query-history-message` | 查询历史消息 | `--group-id`: 群组ID（群聊）或<br>`--user-account`: 用户账号（私聊）<br>`--query-count`: 查询数量<br>`--message-id`: 起始消息ID<br>`--query-direction`: 查询方向（0-更旧，1-更新） |
| `im add-group-member` | 添加群组成员 | `--group-id`: 群组ID<br>`--user-account`: 成员账号列表 |

**IM 命令示例：**
```bash
# 发送消息给用户
welink-cli im send-to-user --receiver "a0012345" --text "Hello WeLink"

# 发送消息给群组
welink-cli im send-to-group --group-id "1234567891011" --text "Group message"

# 创建群组
welink-cli im create-group --name "测试群" --user-account "a0012345" "b0067890" --notice "测试群公告" --type 0

# 查询最近会话
welink-cli im query-recent-conversation --count 20

# 查询群组成员
welink-cli im query-group-member --group-id "1234567891011"

# 查询历史消息（私聊）
welink-cli im query-history-message --user-account "a0012345" --query-count 20

# 查询历史消息（群聊）
welink-cli im query-history-message --group-id "1234567891011" --query-count 20

# 添加群组成员
welink-cli im add-group-member --group-id "1234567891011" --user-account "c0011111" "d0022222"
```

### 会议命令

| 命令 | 说明         | 必需参数                                                                                                                                                                                |
|------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `meeting info` | 查询会议详情     | `--meeting-id`: 会议ID（非视频会议号）                                                                                                                                                        |
| `meeting topic` | 查询会议议题     | `--meeting-id`: 会议ID（非视频会议号）                                                                                                                                                        |
| `meeting topic-materials` | 查询议题材料     | `--meeting-id`: 会议ID（非视频会议号）<br>`--topic-id`: 议题ID                                                                                                                                  |
| `meeting fuzzy-search` | 模糊搜索会议相关信息 | `--limit`: 限制数量<br>`--offset`: 偏移量<br>`--result-type`: 结果类型（meeting/file）<br>`--search-type`: 搜索类型<br>`--search-content`: 搜索内容<br>`--with-full-content`: 是否返回完整内容（true/false）       |
| `meeting create` | 创建会议       | `--subject`: 会议主题（必填）<br>`--start-time`: 开始时间（毫秒时间戳，必填）<br>`--end-time`: 结束时间（毫秒时间戳，必填）<br>`--meeting-user-list`: 与会人列表（必填）                                                         |
| `meeting update` | 更新会议       | `--meeting-id`: 会议ID（必填）<br>`--subject`: 会议主题<br>`--start-time`: 开始时间<br>`--end-time`: 结束时间<br>`--meeting-user-list`: 与会人列表                                                        |
| `meeting cancel` | 取消会议       | `--meeting-id`: 会议ID（必填）                                                                                                                                                            |
| `meeting query-list` | 查询会议列表     | `--page`: 页码<br>`--size`: 每页大小<br>`--meeting-start-time`: 开始时间<br>`--meeting-end-time`: 结束时间<br>`--type`: 类型（0-公开，1-待参加，2-已结束，3-我预定，4-所有，5-我管理）<br>`--meeting-sort`: 排序方式（asc/desc） |
| `meeting topic-create` | 创建议题       | `--meeting-id`: 会议ID（必填）<br>`--topic-name`: 议题名称（必填）<br>`--topic-category`: 议题分类（汇报类、研讨类、决策类、审批类等，必填）<br>`--topic-member-list`: 议题汇报人（必填）                                           |
| `meeting topic-update` | 更新议题       | `--meeting-id`: 会议ID（必填）<br>`--topic-id`: 议题ID（必填）<br>`--topic-name`: 议题名称<br>`--topic-category`: 议题分类<br>`--topic-member-list`: 议题汇报人                                             |
| `meeting topic-delete` | 删除议题       | `--meeting-id`: 会议ID（必填）<br>`--topic-id`: 议题ID（必填）                                                                                                                                          |

**会议命令示例：**
```bash
# 创建会议，下面参数都是必传
welink-cli meeting create --start-time 1778378400000 --end-time 1778382000000 --subject welink-cli测试创建会议 --meeting-user-list c00899563 t00845328

# 修改会议，其中meetingId是必传的，其余的都是非必传，比如只传subject，那就说明只更新这个会议的名称，只传meeting-user-list说明只更新会议与会人信息
welink-cli meeting update --meeting-id 203422177 --start-time 1777100400000 --end-time 1777104000000 --subject 更新后的主题 --meeting-user-list c00899563 t00845328

# 取消会议，其中meetingId是必传的
welink-cli meeting cancel --meeting-id 184521460

# 分页查询会议，都是必传的参数，其中type表示的含义：0-公开的会议、1-待参加的会议、2-已结束的会议、3-我预定的会议、4-所有的会议、5-我管理的会议
welink-cli meeting query-list --meeting-start-time 1767196800000 --meeting-end-time 1798732799999 --type 1 --meeting-sort asc --page 1 --size 15

# 查询会议详情，重要：meeting-id取上面列表命令中meetingId字段，非视频会议号，下同
welink-cli meeting info --meeting-id 184531461

# 模糊搜索会议，根据会议主题模糊搜索时间范围内的相关会议
welink-cli meeting fuzzy-search --result-type meeting --limit 10 --offset 0 --search-type subject --search-content 代码QC --search-type startTime --search-content 1774972800000 --search-type endTime --search-content 1775664000000

# 创建议题，都是必传参数
welink-cli meeting topic-create --meeting-id 203422177 --topic-name 议题名称 --topic-category 汇报类 --topic-member-list c00899563 t00845328

# 删除议题，都是必传参数
welink-cli meeting topic-delete --meeting-id 203422177 --topic-id 88711297

# 修改议题，其中meetingId和topicId是必传的，其余的都是非必传，比如只传topic-name，那就说明只更新这个议题的名称，只传topic-member-list说明只更新议题的汇报人信息
welink-cli meeting topic-update --meeting-id 203422177 --topic-id 88711297 --topic-name 更新后的议题名称 --topic-category 汇报类 --topic-member-list c00899563 t00845328

# 查询会议下议题信息，重要：meeting-id非视频会议号
welink-cli meeting topic --meeting-id 184531461

# 查询会议下，指定议题材料信息，重要：meeting-id非视频会议号
welink-cli meeting topic-materials --meeting-id 202674731 --topic-id 88520416
```

### 搜索命令

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `search person` | 搜索联系人 | `--text`: 搜索关键词<br>`--page-size`: 返回数量（可选，默认20） |
| `search group` | 搜索群组 | `--text`: 搜索关键词<br>`--page-size`: 返回数量（可选，默认20）<br>`--type`: 群组类型（0-群组，1-讨论群，2-全部，可选） |

**搜索示例：**
```bash
# 搜索联系人
welink-cli search person --text "张三"

# 搜索群组
welink-cli search group --text "项目组"

# 指定返回数量搜索
welink-cli search person --text "z00123456" --page-size 50

# 搜索特定类型的群组
welink-cli search group --text "测试" --type 0
```

### 云空间命令

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `onebox file-upload` | 上传文件 | `file-path`: 文件路径<br>`--space-id`: 空间ID<br>`--parent`: 父文件夹ID（可选，默认0） |
| `onebox file-download` | 下载文件 | `--space-id`: 空间ID<br>`--file-id`: 文件ID<br>`--output`: 输出路径（可选，默认当前目录）<br>`--force`: 强制覆盖（可选） |
| `onebox file-info` | 获取文件信息 | `--space-id`: 空间ID<br>`--file-id`: 文件ID |
| `onebox file-copy` | 复制文件 | `--space-id`: 源空间ID<br>`--file-id`: 文件ID<br>`--dest-parent`: 目标父文件夹ID<br>`--dest-space-id`: 目标空间ID |
| `onebox file-move` | 移动文件 | `--space-id`: 空间ID<br>`--file-id`: 文件ID<br>`--dest-parent`: 目标父文件夹ID<br>`--dest-space-id`: 目标空间ID |
| `onebox file-rename` | 重命名文件 | `--space-id`: 空间ID<br>`--file-id`: 文件ID<br>`--name`: 新文件名 |
| `onebox file-remove` | 删除文件（移到回收站） | `--space-id`: 空间ID<br>`--file-id`: 文件ID |
| `onebox folder-list` | 列出文件夹内容 | `--space-id`: 空间ID<br>`--folder-id`: 文件夹ID（可选，默认0）<br>`--limit`: 分页大小（可选，默认20）<br>`--offset`: 分页偏移（可选，默认0） |
| `onebox folder-new` | 创建新文件夹 | `--space-id`: 空间ID<br>`--parent`: 父文件夹ID（可选，默认0）<br>`--name`: 文件夹名称 |
| `onebox folder-rename` | 重命名文件夹 | `--space-id`: 空间ID<br>`--folder-id`: 文件夹ID<br>`--name`: 新文件夹名称 |
| `onebox folder-remove` | 删除文件夹（移到回收站） | `--space-id`: 空间ID<br>`--folder-id`: 文件夹ID |
| `onebox user-info` | 获取用户信息 | 无 |
| `onebox node-search` | 搜索文件和文件夹 | `--space-id`: 空间ID<br>`--name`: 搜索关键词<br>`--offset`: 分页偏移（可选，默认0）<br>`--limit`: 最大结果数（可选，默认100）<br>`--with-path`: 包含路径信息（可选）<br>`--exact-search`: 精确匹配（可选）<br>`--file-type`: 文件类型过滤（可选，file/folder/all） |
| `onebox file-share-link-get` | 创建并获取文件分享外链（若已存在则返回已有外链，默认仅自己可见） | `--space-id`: 空间ID<br/>`--file-id`: 文件ID |
| `onebox file-share-link-edit` | 编辑文件分享外链（修改权限和提取码） | `--space-id`: 空间ID<br/>`--file-id`: 文件ID<br/>`--role`: 权限角色（viewer/previewer/editor/prohibitVisitors）<br/>`--set-plain-access-code`: 设置提取码（可选）<br/>`--unset-plain-access-code`: 取消提取码（可选） |
| `onebox file-share-link-remove` | 取消文件分享外链 | `--space-id`: 空间ID<br/>`--file-id`: 文件ID |

**云空间命令示例：**
```bash
# 获取用户信息（获取个人空间ID，使用响应中的 cloudUserId 字段）
welink-cli onebox user-info

# 上传文件
welink-cli onebox file-upload --space-id 123 --parent 0 "./report.pdf"

# 下载文件
welink-cli onebox file-download --space-id 123 --file-id 456 --output "./downloads/"

# 获取文件信息
welink-cli onebox file-info --space-id 123 --file-id 456

# 列出文件夹内容
welink-cli onebox folder-list --space-id 123 --folder-id 0 --limit 20 --offset 0

# 复制文件
welink-cli onebox file-copy --space-id 123 --file-id 456 \
  --dest-parent 789 --dest-space-id 123

# 移动文件
welink-cli onebox file-move --space-id 123 --file-id 456 \
  --dest-parent 789 --dest-space-id 123

# 重命名文件
welink-cli onebox file-rename --space-id 123 --file-id 456 --name "新文件名.pdf"

# 删除文件
welink-cli onebox file-remove --space-id 123 --file-id 456

# 创建新文件夹
welink-cli onebox folder-new --space-id 123 --parent 0 --name "新文件夹"

# 重命名文件夹
welink-cli onebox folder-rename --space-id 123 --folder-id 789 --name "新文件夹名"

# 删除文件夹
welink-cli onebox folder-remove --space-id 123 --folder-id 789

# 搜索文件和文件夹
welink-cli onebox node-search --space-id 123 --name "报告" \
  --offset 0 --limit 100 --file-type all
```

**分享外链权限说明：**

| role 值 | 权限说明 |
|---------|---------|
| `viewer` | 浏览、预览、下载 |
| `previewer` | 浏览、预览 |
| `editor` | 浏览、预览、下载、编辑 |
| `prohibitVisitors` | 仅自己可见 |

**分享外链使用示例：**
```bash
# 创建分享外链（返回外链URL，默认仅自己可见）
welink-cli onebox file-share-link-get --space-id 329434 --file-id 3806

# 修改外链权限为可下载
welink-cli onebox file-share-link-edit --space-id 329434 --file-id 3806 --role viewer

# 设置提取码
welink-cli onebox file-share-link-edit --space-id 329434 --file-id 3806 --role viewer --set-plain-access-code abc123

# 取消提取码
welink-cli onebox file-share-link-edit --space-id 329434 --file-id 3806 --role viewer --unset-plain-access-code

# 删除分享外链
welink-cli onebox file-share-link-remove --space-id 329434 --file-id 3806
```


### 邮件命令

**重要提示**：首次使用邮件日历功能前，必须执行 `mail autodiscover` 命令获取自己所在的邮箱服务器地址。

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `mail autodiscover` | 执行 Autodiscover（首次使用必须执行） | `--email`: 用户邮箱 |
| `mail folders` | 列出邮件文件夹 | — |
| `mail list` | 查询邮件列表（支持筛选、KQL） | — |
| `mail get` | 查看邮件详情 | `--item-id` |
| `mail send` | 发送邮件（可带附件） | `--to`、`--subject` |
| `mail attachment` | 下载邮件附件 | `--attachment-id`、`--path` |
| `mail reply` | 回复发件人 | `--item-id` |
| `mail reply-all` | 回复所有人 | `--item-id` |
| `mail forward` | 转发邮件（可追加附件） | `--item-id`、`--to` |
| `mail move` | 移动邮件到指定文件夹 | `--item-id`、`--folder-id` |

**邮件命令使用示例：**

#### mail autodiscover — 执行 Autodiscover（首次必须先执行autoDiscover）

**用途**：通过邮箱地址发现 Exchange 服务器域名

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `--email` | 是 | 用户邮箱地址 |

**输出**：
- 成功：`Discovered EWS URL: https://imailcn55.email.huawei.com/EWS/Exchange.asmx`


#### mail list — 查询邮件列表

**用途**：查询指定文件夹的邮件列表，支持多种筛选条件。

**参数**：

| 选项 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `--folder-id` | `inbox` | 否 | 文件夹 ID。**推荐**：先用 `mail folders` 拿到实际 FolderId（base64 长串）后填入。也支持常用简称：`inbox` / `sentitems` / `drafts` / `deleteditems` / `calendar`。**不支持中文别名**（`收件箱` 等会报 `ErrorInvalidIdMalformed`） |
| `--max` | `10` | 否 | 最大返回数（0-500） |
| `--offset` | `0` | 否 | 分页偏移量，用于翻页 |
| `--is-read` | `-1` | 否 | 已读状态筛选：`0`=未读、`1`=已读、`-1`=全部 |
| `--from` | | 否 | 按发件人筛选（模糊匹配） |
| `--subject` | | 否 | 按主题筛选（模糊匹配） |
| `--start` | | 否 | 起始日期，**包含**当天（格式：`YYYY-MM-DD`） |
| `--end` | | 否 | 结束日期，**不包含**当天（格式：`YYYY-MM-DD`，等价于 `YYYY-MM-DDT00:00:00`）。例如查 `2026-05-08` 单天的邮件，要写 `--end 2026-05-09`；要覆盖整个 4 月，要写 `--end 2026-05-01` |
| `--query` | | 否 | KQL 查询字符串（**高级语法**，详见下方说明） |

**输出字段**（table 格式）：

| 字段 | 说明 |
|------|------|
| `#` | 序号 |
| `Read` | 已读状态（`Y`/`N`） |
| `From` | 发件人 |
| `Subject` | 主题 |
| `Date` | 接收时间 |
| `ItemId` | 邮件唯一标识，用于 `mail get`、`mail attachment` 等后续命令 |

**示例**：

```bash
# 翻页查看第 11-20 封邮件
welink-cli mail list --max 10 --offset 10

# 查找某人在 4/1 ~ 4/10（含 4/10 当天）发的未读邮件
# 注意：--end 是不含的边界。要覆盖到 4/10 当天，必须传 4/11
welink-cli mail list --from zhang@example.com --is-read 0 \
  --start 2026-04-01 --end 2026-04-11

# 查询单天（5/8 当天的邮件）— 同样要把 --end 写成次日
welink-cli mail list --start 2026-05-08 --end 2026-05-09

# 用 mail folders 拿到真实 FolderId 后查询自定义文件夹（推荐）
welink-cli mail folders          # 找到目标行的 FolderId
welink-cli mail list --folder-id AAMkADQ3...folder-id...
```

##### `--query`（KQL 高级语法）

`--query` 把字符串原样透传给 Exchange 服务端的 KQL（Keyword Query Language）解析器，
功能强大但**写错时报错信息晦涩**。日常筛选**优先使用 `--from` / `--subject` / `--start` / `--end` 等专用选项**，
仅在专用选项不够用（如同时模糊匹配多个字段、按附件名搜索等）时再考虑 KQL：

```bash

# 字段限定（多关键词默认 AND 关系）
welink-cli mail list --query "from:zhang subject:周报"
```

> 完整 KQL 语法见 Microsoft 官方文档：[Keyword Query Language reference](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/keyword-query-language-kql-syntax-reference)。

#### mail get — 获取邮件详情

**用途**：获取单封邮件的完整内容，包括正文、收件人、附件列表等。

**前置条件**：需要先通过 `mail list` 获取邮件的 `ItemId`。

**参数**：

| 选项 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `--item-id` | | 是 | 邮件的 ItemId（从 `mail list` 输出获取） |
| `--body-type` | `Text` | 否 | 正文格式：`Text`（纯文本）/ `HTML` |

**输出字段**：

| 字段 | 说明 |
|------|------|
| `Subject` | 主题 |
| `From` | 发件人姓名及邮箱 |
| `Date` | 接收时间 |
| `Read` | 已读状态 |
| `Importance` | 重要程度（Low/Normal/High） |
| `To` | 收件人列表 |
| `CC` | 抄送列表（有则显示） |
| `Categories` | 分类标签（有则显示） |
| `Attachments` | 是否有附件（Yes/No） |
| 附件详情 | 每个附件显示：名称、类型、大小、**附件 ID**（用于 `mail attachment` 下载） |
| `ItemId` | 邮件唯一标识 |
| `Body` | 正文内容 |

**示例**：

```bash
welink-cli mail get --item-id AAMkADQ3...

# 输出示例：
# Subject:     周报
# From:        张三 <zhang@example.com>
# Date:        2026-04-10T09:30:00Z
# Read:        Yes
# Importance:  Normal
# To:          team@example.com
# Attachments: Yes
#   - 周报.xlsx (application/vnd.openxmlformats...) [45.2 KB]
#     ID: AAMkADQ3...attachment-id...
# ItemId:      AAMkADQ3...
#
# --- Body (Text) ---
# 本周工作内容如下...
```

#### mail folders — 列出邮件文件夹

**用途**：列出所有邮件文件夹及其统计信息。

**参数**：无额外参数。

**输出字段**（table 格式）：

| 字段 | 说明 |
|------|------|
| `Name` | 文件夹显示名称 |
| `Total` | 邮件总数 |
| `Unread` | 未读数 |
| `FolderId` | 文件夹 ID，可用于 `mail list --folder-id` |

**使用场景**：当内置名称（`inbox`、`sentitems`）不满足需求时，通过此命令获取自定义文件夹的实际 ID。

#### mail send — 发送邮件

**用途**：发送邮件，支持多收件人、抄送、密送、HTML 正文和文件附件。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `--to` | 是 | 收件人邮箱。支持逗号分隔（`"a@x.com,b@x.com"`）或重复指定（`--to a --to b`） |
| `--subject` | 是 | 邮件主题 |
| `--body` | 否 | 邮件正文。**纯文本**时直接写文字；启用 `--html` 时改为 **HTML 标记字符串**（如 `"<p>Hi</p>"`） |
| `--cc` | 否 | 抄送，格式同 `--to` |
| `--bcc` | 否 | 密送，格式同 `--to` |
| `--html` | 否 | 标记 `--body` 内容为 HTML 格式（flag，无需赋值）。不启用时 `--body` 按纯文本发送，HTML 标签会被原样显示而不渲染 |
| `--attachment`, `-a` | 否 | 附件文件路径，可重复指定多个 |

**发送机制**：
- 无附件时：直接发送
- 有附件时：自动执行三步协议（创建草稿 → 上传附件 → 发送），无需手动操作

**输出**：
- 成功：`Mail sent successfully` 或 `Mail sent successfully (N attachment(s))`
- 失败：抛出错误信息

#### mail attachment — 下载附件

**用途**：下载邮件附件到本地。

**前置条件**：需要先通过 `mail get` 获取附件的 `AttachmentId`。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `--attachment-id` | 是 | 附件 ID（从 `mail get` 附件详情获取） |
| `--path` | 是 | 保存路径。为目录时使用原始文件名，为文件路径时使用指定文件名 |

**输出**：
- 成功：`Attachment saved to <path>`
- 失败：抛出错误信息

**示例**：

```bash
# 步骤 1：查看邮件详情，获取附件 ID
welink-cli mail get --item-id AAMkADQ3...

# 输出中的附件信息：
#   - 周报.xlsx (application/vnd.openxmlformats...) [45.2 KB]
#     ID: AAMkADQ3...attachment-id...

# 步骤 2：下载附件到目录（保留原始文件名）
welink-cli mail attachment --attachment-id AAMkADQ3...attachment-id... --path ./downloads/

# 步骤 2（替代）：下载附件到指定文件名
welink-cli mail attachment --attachment-id AAMkADQ3...attachment-id... --path report.xlsx
```

#### mail reply — 回复邮件

**用途**：回复单封邮件（仅回复发件人）。

**前置条件**：需要先通过 `mail list` 获取邮件的 `ItemId`。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `--item-id` | 是 | 邮件的 ItemId |
| `--body` | 否 | 回复正文。`--html` 启用时填 HTML 标记，否则填纯文本 |
| `--html` | 否 | 标记 `--body` 为 HTML 格式（不启用 = 纯文本） |
| `--subject` | 否 | 自定义主题。不传时由 EWS 自动生成 `RE:` 前缀 |
| `--attachment`, `-a` | 否 | 附件文件路径，可重复指定多个。指定时走 3 步流程（CreateDraft → CreateAttachment → SendItem） |

**输出**：
- 成功：`Reply sent successfully` 或 `Reply sent successfully (N attachment(s))`

**示例**：

```bash
# 纯文本回复
welink-cli mail reply --item-id AAMkADQ3... --body "已收到，谢谢"

# HTML 回复
welink-cli mail reply --item-id AAMkADQ3... \
  --body "<p>已收到，<b>谢谢</b></p>" --html

# 自定义主题（不再带 RE: 前缀）
welink-cli mail reply --item-id AAMkADQ3... \
  --subject "周报反馈" --body "已收到"

# 带附件回复
welink-cli mail reply --item-id AAMkADQ3... \
  --body "补充材料见附件" -a ./report.pdf -a ./data.xlsx
```

#### mail reply-all — 回复全部

**用途**：回复邮件的所有收件人（发件人 + 所有 To/CC）。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `--item-id` | 是 | 邮件的 ItemId |
| `--body` | 否 | 回复正文。`--html` 启用时填 HTML 标记，否则填纯文本 |
| `--html` | 否 | 标记 `--body` 为 HTML 格式（不启用 = 纯文本） |
| `--subject` | 否 | 自定义主题。不传时由 EWS 自动生成 `RE:` 前缀 |
| `--attachment`, `-a` | 否 | 附件文件路径，可重复指定多个。指定时走 3 步流程 |

**输出**：
- 成功：`Reply-all sent successfully` 或 `Reply-all sent successfully (N attachment(s))`

**示例**：

```bash
welink-cli mail reply-all --item-id AAMkADQ3... --body "同意，我参加"

# 自定义主题
welink-cli mail reply-all --item-id AAMkADQ3... \
  --subject "周会纪要" --body "同意"

# 带附件回复全部
welink-cli mail reply-all --item-id AAMkADQ3... \
  --body "请查阅修订稿" -a ./minutes-v2.docx
```

#### mail forward — 转发邮件

**用途**：转发邮件给指定收件人，可选包含原始附件。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `--item-id` | 是 | 邮件的 ItemId |
| `--to` | 是 | 转发收件人。支持逗号分隔（`"a@x.com,b@x.com"`）或重复指定 |
| `--cc` | 否 | 抄送，格式同 `--to` |
| `--body` | 否 | 转发正文（会出现在原始邮件内容之前）。`--html` 启用时填 HTML 标记，否则填纯文本 |
| `--html` | 否 | 标记 `--body` 为 HTML 格式（不启用 = 纯文本） |
| `--subject` | 否 | 自定义主题。不传时由 EWS 自动生成 `FW:` 前缀 |
| `--attachment`, `-a` | 否 | 额外附件文件路径，可重复指定多个。原始邮件附件会自动包含，本选项用于追加新附件 |

> 转发自动包含原始邮件的附件，无需额外参数。`--attachment` 用于追加新附件（走 3 步流程）。

**输出**：
- 成功：`Mail forwarded successfully` 或 `Mail forwarded successfully (N attachment(s))`

**示例**：

```bash
# 简单转发
welink-cli mail forward --item-id AAMkADQ3... \
  --to colleague@example.com --body "请查阅"

# 转发给多人 + 抄送
welink-cli mail forward --item-id AAMkADQ3... \
  --to "a@example.com,b@example.com" --cc mgr@example.com \
  --body "附件请查收"

# 自定义主题（不再带 FW: 前缀）
welink-cli mail forward --item-id AAMkADQ3... \
  --to colleague@example.com --subject "项目启动通知" --body "请查阅"

# 转发并追加新附件（原始附件保留 + 新增 cover.pdf）
welink-cli mail forward --item-id AAMkADQ3... \
  --to colleague@example.com --body "增加封面" -a ./cover.pdf
```

#### mail move — 移动邮件

**用途**：将邮件移动到指定文件夹。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `--item-id` | 是 | 邮件的 ItemId |
| `--folder-id` | 是 | 目标文件夹。**推荐**：先用 `mail folders` 拿到实际 FolderId 后填入。也支持常用简称：`inbox` / `sentitems` / `drafts` / `deleteditems` / `calendar`。**不支持中文别名** |

**输出**：
- 成功：`Mail moved successfully`

**注意事项**：
- 移动操作后邮件的 **ItemId 会发生变化**（EWS 行为），原 ItemId 不再有效
- 如需对移动后的邮件继续操作，需从目标文件夹重新获取新 ItemId

**示例**：

```bash
# 移动到草稿箱
welink-cli mail move --item-id AAMkADQ3... --folder-id drafts

# 移动到自定义文件夹（FolderId 从 mail folders 获取）
welink-cli mail move --item-id AAMkADQ3... --folder-id AAMkADQ3...folder-id...
```


### 日历命令

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `calendar list` | 查询日历事件 | — |
| `calendar get` | 查看事件详情 | `--item-id` |
| `calendar create` | 创建事件（可邀请参会人） | `--subject`、`--start`、`--end` |



#### calendar list — 查询日历事件

**用途**：查询指定日期范围内的日历事件。

**参数**：

| 选项 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `--start` | 今天 | 否 | 起始日期，**包含**当天（格式：`YYYY-MM-DD`） |
| `--end` | start + 7 天 | 否 | 结束日期，**不包含**当天（格式：`YYYY-MM-DD`，等价于 `YYYY-MM-DDT00:00:00`）。例如查 `2026-05-08` 单天的事件，要写 `--end 2026-05-09`；要覆盖整个 4 月，要写 `--end 2026-05-01` |
| `--max` | `20` | 否 | 最大返回数（0-500） |

**输出字段**（table 格式）：

| 字段 | 说明 |
|------|------|
| `Subject` | 事件主题 |
| `Start` | 开始时间 |
| `End` | 结束时间 |
| `Location` | 地点 |
| `Status` | 忙闲状态（Free/Tentative/Busy/OOF） |
| `Organizer` | 组织者 |
| `ItemId` | 事件唯一标识，用于 `calendar get` 获取详情 |

**示例**：

```bash
# 查询整个 4 月（注意 --end 是不含的边界，要写 5/1 才覆盖到 4/30）
welink-cli calendar list --start 2026-04-01 --end 2026-05-01

# 查询 4/10 单天（--end 写次日）
welink-cli calendar list --start 2026-04-10 --end 2026-04-11

# 查询今天（假设今天是 5/8，--end 写明天 5/9）
welink-cli calendar list --start 2026-05-08 --end 2026-05-09

# 查看更多事件
welink-cli calendar list --max 50
```

#### calendar get — 获取事件详情

**用途**：获取单个日历事件的完整信息。

**前置条件**：需要先通过 `calendar list` 获取事件的 `ItemId`。

**参数**：

| 选项 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `--item-id` | | 是 | 事件的 ItemId（从 `calendar list` 输出获取） |
| `--body-type` | `Text` | 否 | 正文格式：`Text` / `HTML` |

**输出字段**：

| 字段 | 说明 |
|------|------|
| `Subject` | 事件主题 |
| `Start` | 开始时间 |
| `End` | 结束时间 |
| `Location` | 地点 |
| `Organizer` | 组织者姓名及邮箱 |
| `All Day` | 是否全天事件 |
| `Cancelled` | 是否已取消 |
| `Status` | 忙闲状态 |
| `Importance` | 重要程度 |
| `Categories` | 分类标签（有则显示） |
| `Meeting URL` | 在线会议链接（有则显示） |
| `ItemId` | 事件唯一标识 |
| `Body` | 事件描述正文 |

#### calendar create — 创建日历事件

**用途**：创建日历事件。指定参会人时自动发送会议邀请。

**参数**：

| 选项 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `--subject` | | 是 | 事件主题 |
| `--start` | | 是 | 开始时间（ISO 8601 不带时区后缀，如 `2026-04-10T14:00:00`，按 `--tz` 指定的时区解释） |
| `--end` | | 是 | 结束时间（格式同上，按 `--tz` 指定的时区解释） |
| `--body` | | 否 | 事件描述。`--html` 启用时填 HTML 标记，否则填纯文本 |
| `--location` | | 否 | 地点 |
| `--html` | | 否 | 标记 `--body` 为 HTML 格式（不启用 = 纯文本） |
| `--attendee` | | 否 | 参会人邮箱。支持逗号分隔或重复指定 |
| `--reminder` | `15` | 否 | 提醒分钟数（设为 `0` 则不提醒） |

> **时区**：`--timezone`/`--tz` 是 `calendar` 父命令选项，写在 `calendar` 后、`create` 前。
> `--start` / `--end` 字符串**不带后缀**（推荐写法）时按 `--tz` 解释；如果显式带 `+08:00` 或 `Z` 后缀，
> 会先转 UTC 再发送。默认 `China Standard Time`。

**邀请行为**：
- 指定 `--attendee` → 自动发送会议邀请邮件
- 不指定 `--attendee` → 仅创建个人日程，不发邀请

**输出**：
- 成功：`Calendar event created successfully` + 新事件的 `ItemId`

**示例**：

```bash
# 个人日程
welink-cli calendar create --subject "专注时间" \
  --start 2026-04-10T09:00:00 --end 2026-04-10T11:00:00

# 会议邀请（逗号分隔参会人）
welink-cli calendar create --subject "周会" \
  --start 2026-04-10T10:00:00 --end 2026-04-10T11:00:00 \
  --location "会议室 B" \
  --attendee "alice@example.com,bob@example.com,charlie@example.com" \
  --reminder 10

# 指定时区（--tz 写在 calendar 后、create 前）
welink-cli calendar --tz "Tokyo Standard Time" create --subject "跨时区会议" \
  --start 2026-04-10T14:00:00 --end 2026-04-10T15:00:00 \
  --attendee "tokyo-team@example.com"
```

### 联系人命令

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `contact detail` | 查询用户详细信息 | `accounts`: 用户账号列表（welinkId） |
| `contact add_favorite` | 添加特别关注 | `accounts`: 用户账号列表（welinkId） |
| `contact del_favorite` | 删除特别关注 | `accounts`: 用户账号列表（welinkId） |
| `contact favorite_list` | 查询特别关注列表 | — |

**联系人命令使用示例：**

#### contact detail — 查询用户详细信息

**用途**：查询指定用户的详细信息。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `accounts` | 是 | 用户账号（welinkId），支持多个值 |
| `--source` | 否 | 来源标识（默认：welink-cli） |

**示例**：

```bash
# 查询单个用户详情
welink-cli contact detail userwelinkid_1

# 查询多个用户详情
welink-cli contact detail userwelinkid_1 userwelinkid_2
```

#### contact add_favorite — 添加特别关注

**用途**：将指定用户添加到特别关注列表。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `accounts` | 是 | 用户账号（welinkId），支持多个值 |
| `--source` | 否 | 来源标识（默认：welink-cli） |

**示例**：

```bash
# 添加单个特别关注
welink-cli contact add_favorite userwelinkid_1

# 添加多个特别关注
welink-cli contact add_favorite userwelinkid_1 userwelinkid_2
```

#### contact del_favorite — 删除特别关注

**用途**：从特别关注列表中删除指定用户。

**参数**：

| 选项 | 必填 | 说明 |
|------|------|------|
| `accounts` | 是 | 用户账号（welinkId），支持多个值 |
| `--source` | 否 | 来源标识（默认：welink-cli） |

**示例**：

```bash
# 删除单个特别关注
welink-cli contact del_favorite userwelinkid_1

# 删除多个特别关注
welink-cli contact del_favorite userwelinkid_1 userwelinkid_2
```

#### contact favorite_list — 查询特别关注列表

**用途**：查询当前用户的特别关注列表，支持分页。

**参数**：

| 选项 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `--pageIndex` | 1 | 否 | 页码（1-10000） |
| `--pageSize` | 50 | 否 | 每页数量（1-50） |
| `--source` | welink-cli | 否 | 来源标识 |

**示例**：

```bash
# 查询特别关注列表（第一页）
welink-cli contact favorite_list

# 查询第二页，每页50条
welink-cli contact favorite_list --pageIndex 2 --pageSize 50
```

### 版本检查命令

| 命令 | 说明 | 必需参数 |
|------|------|----------|
| `version check` | 检查 CLI 版本是否过期，如过期则自动更新到最新版本 | 无 |

**版本检查命令使用示例：**

```bash
# 检查 CLI 版本是否过期
welink-cli version check
```

该命令会检查当前 CLI 版本是否过期。如果版本过期，会自动更新到最新版本。

### 通用选项

**全局选项：**
- `-v, --verbose`: 启用详细输出
- `-d, --debug`: 启用调试输出（包含 --verbose）
- `--version`: 显示版本信息
- `-h, --help`: 显示帮助信息

**邮件/日历通用选项：**
- `--format`: 输出格式（table/json，默认table）
- `--timezone, --tz`: 时区ID（默认China Standard Time）

**邮件/日历的常用时区ID：**
- `China Standard Time`: UTC+8（北京、上海）
- `Tokyo Standard Time`: UTC+9（东京、首尔）
- `Singapore Standard Time`: UTC+8（新加坡）
- `GMT Standard Time`: UTC+0（伦敦）
- `Eastern Standard Time`: UTC-5（纽约）
- `Pacific Standard Time`: UTC-8（洛杉矶）

运行 `welink-cli <command> --help` 查看详细的参数说明。
