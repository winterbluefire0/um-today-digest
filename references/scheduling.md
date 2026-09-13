# Scheduling guidance

Read this file only when the user asks for recurring delivery, subscription,
monitoring, reminders, or an automatic daily digest.

## Required behavior

1. Confirm the user's desired delivery time and timezone if they are not already
   clear. Default to `09:40 Asia/Macau` only when the user accepts the default.
2. Use the host agent's native scheduler, automation, heartbeat, or cron facility.
3. Save a cohesive job prompt that invokes `um-today-digest`, fetches the newest
   public sources, applies the saved non-sensitive preferences, checks the delivery
   history described in [state.md](state.md), and suppresses unchanged output.
4. Tell the user what was scheduled, including time, timezone, destination, and how
   to pause or remove it.

Installing a Skill and creating a schedule are separate operations. Never claim both
succeeded when only the Skill installation is visible.

## Suggested scheduled-task prompt

```text
Use the um-today-digest skill to check the public University of Macau UM Today
archive and event calendar. Apply my saved non-sensitive interests and availability.
Send three to five newly relevant events or urgent deadlines with reasons and
official links. Stay quiet when there is no new issue, changed deadline, or newly
relevant event. After a successful delivery, record the issue date and stable IDs or
canonical URLs of the delivered items. Never request or use my UM email password.
```

## Host adaptations

- ChatGPT or Codex: use its native task or automation feature when exposed.
- Claude-based agents: use the scheduler supplied by the Claude host; Claude Code
  alone does not make a background schedule portable across machines.
- OpenClaw: use its configured scheduling capability after the user authorizes the
  recurring job.
- DeepSeek Harness: use the active profile's scheduling plugin or task service.
- QwenPaw: use its Cron or Heartbeat capability for the current agent and channel.

Do not invent a raw command or configuration file when the host exposes no verified
scheduling interface. In that case, leave the Skill installed and offer on-demand
use.
