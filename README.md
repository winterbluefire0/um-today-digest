# UM Today Digest · 今日澳大智能日报

把澳大公开的《今日澳大》和活动日历变成一份与个人兴趣、身份和时间相关的
每日摘要。Skill 不读取学校邮箱，也不需要澳大学生账号；需要登录的报名页只会
作为链接交给用户自行打开。

[![扫码把功能交给你的 Agent](assets/install-qr.png)](https://github.com/winterbluefire0/um-today-digest)

二维码指向本仓库首页。现场观众扫码后，只需把仓库链接或下面这一句话发给自己的
Agent；Agent 会按自身能力选择直接安装、读取 Skill，或建立等效的每日任务。

## 发给你的 Agent

复制下面这段话给支持联网的 Agent：

> 请检查并安装这个公开的 Agent Skill：
> <https://github.com/winterbluefire0/um-today-digest>。如果你支持 Agent Skills，请安装
> `um-today-digest` 到当前用户或当前 Agent；如果你不支持持久 Skill，就读取
> `SKILL.md` 并按其中规则工作。不要索取我的学校邮箱密码。安装后，用一个简短问题
> 同时询问我的身份、兴趣、空闲时段、语言偏好和希望收到日报的时间；我回答后立即
> 生成首份个性化日报，并在平台支持时创建每日任务。最后分别告诉我：Skill 是否
> 安装、首份日报是否生成、每日任务是否创建，以及如何暂停。

## 安装

通用 AgentSkills 客户端：

```bash
npx skills add https://github.com/winterbluefire0/um-today-digest
```

OpenClaw：

```bash
openclaw skills install git:winterbluefire0/um-today-digest@main
```

QwenPaw：

```bash
qwenpaw skills install https://github.com/winterbluefire0/um-today-digest --agent-id default
```

DeepSeek Harness 可以把仓库放入项目的 `.agents/skills/um-today-digest`，或把
Skill 目录安装到 `~/.dsh/skills/um-today-digest`。Claude Code、Codex 及其他
支持 Agent Skills 的客户端可以使用上面的通用命令，或让 Agent 从 GitHub 安装。

不同平台的 Skill 安装和后台定时能力不是同一件事：

| 平台 | Skill 使用方式 | 主动日报 | 当前验证状态 |
| --- | --- | --- | --- |
| ChatGPT / Codex | 读取仓库或使用平台提供的 Skill 能力 | 需要账户提供 Tasks / Automation | 仓库与格式已验证，账户能力因版本而异 |
| Claude Code | 通用 Agent Skills 安装或读取仓库 | 需要运行环境另配调度器 | 按 Agent Skills 结构适配，未逐环境实测 |
| OpenClaw | 使用上方 `openclaw skills install` | 使用其调度能力 | 安装命令按官方格式编写，未在本机实测 |
| DeepSeek Harness | 放入 `.agents/skills` 或 `.dsh/skills` | 需要调度插件或任务服务 | 目录结构适配，未在本机实测 |
| 阿里 QwenPaw | 使用上方 `qwenpaw skills install` | 使用 Cron 或 Heartbeat | 安装命令按官方格式编写，未在本机实测 |

如果平台不能永久安装 Skill，Agent 仍可读取 `SKILL.md` 生成当次日报；能否在后台
持续发送取决于该平台是否提供定时任务。

## 使用后的完整流程

1. Agent 安装或读取 Skill；
2. 用一个问题收集最少必要偏好和推送时间；
3. 当场生成首份“校园概览＋与你有关的活动”；
4. 平台支持时创建每日任务，并保存非敏感偏好与近期已推送项目；
5. 用户可以回复“感兴趣”“少推这类”“暂停日报”或修改时间。

## 是否需要澳大学生账户？

已用未登录状态验证：UM Today 资料库、日期详情页、公开活动详情页和 iCal 活动
日历都可直接访问，因此发现与筛选活动不需要学校账户。部分 `e-bulletin`、MyUM
或报名页面可能在用户点开后要求登录；Skill 会标注这种情况，并把登录动作留给
用户本人。

## 数据源

- [UM Today 公开资料库](https://www.um.edu.mo/um-today/)
- [澳大公开活动日历](https://www.um.edu.mo/eventscalendar/?ical=1)

确定性抓取器只依赖 Python 标准库：

```bash
python3 scripts/fetch_um_today.py --days 30 --format json
```

抓取器会排除已取消和已结束的日历活动，过滤非资讯门户，并在单个公开来源失败时
保留其他可用来源。Agent 会对最终入选项目继续打开官方详情页，核对报名截止、
适用对象、报名入口和奖励信息。

## 权限与隐私

- 只访问澳大 `*.um.edu.mo` 的公开网页；
- 不读取邮箱，不保存 Cookie，不索取密码、验证码或学生证号；
- 安装 Skill 不等于已经开启每日推送；创建定时任务前应由用户明确同意；
- 报名、发送消息、加入日历等外部操作仍需用户明确要求。

## License

[MIT](LICENSE)
