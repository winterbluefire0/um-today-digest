# Profile and delivery state

Read this file when recurring delivery, preference learning, or duplicate suppression
is requested.

Keep the smallest state that makes recommendations and delivery reliable. Prefer the
host's private task memory or application state. If the host uses a workspace file,
store it outside this public Skill repository and ensure it is not committed.

Suggested shape:

```json
{
  "profile": {
    "role": "student",
    "study_level": null,
    "interests": ["AI", "career"],
    "availability": ["weekday lunch", "after 18:00"],
    "language": "zh-Hans",
    "values": ["networking", "Smart Points"]
  },
  "delivery": {
    "time": "09:40",
    "timezone": "Asia/Macau",
    "enabled": true
  },
  "history": {
    "last_issue_date": "20260914",
    "delivered_item_keys": ["https://www.um.edu.mo/event/12345/"],
    "updated_at": "2026-09-14T09:40:00+08:00"
  }
}
```

Use a canonical official URL as the item key when available; otherwise use the iCal
UID, then a normalized title plus start time. Keep only recent history needed for
deduplication. Record an item only after it was successfully delivered.

Do not store names, student numbers, email addresses, passwords, one-time codes,
precise location, private calendar content, or inferred sensitive traits. Treat a
user's explicit `Interested`, `Less like this`, schedule change, pause, or resume as a
state update. Do not infer a permanent preference from silence or one missed event.
