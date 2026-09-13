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
> `SKILL.md` 并创建等效的每日任务。不要索取我的学校邮箱密码。安装完成后，先
> 询问我的身份、兴趣、空闲时段和语言偏好，再立即生成最新一期个性化日报。

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

普通 ChatGPT 如果不能永久安装 GitHub Skill，可以读取 `SKILL.md` 后创建等效的
每日计划；具体能否后台运行取决于当前账户是否提供任务功能。

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

## 权限与隐私

- 只访问 `www.um.edu.mo` 的公开网页；
- 不读取邮箱，不保存 Cookie，不索取密码、验证码或学生证号；
- 安装 Skill 不等于已经开启每日推送；创建定时任务前应由用户明确同意；
- 报名、发送消息、加入日历等外部操作仍需用户明确要求。

## License

[MIT](LICENSE)
