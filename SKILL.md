---
name: um-today-digest
description: Creates a concise, personalized University of Macau daily digest from the public UM Today archive and event calendar. Use when a user asks about 今日澳大, UM Today, campus activities, seminars, recruitment notices, registration deadlines, personalized event recommendations, or a recurring UM campus digest.
license: MIT
metadata:
  author: winterbluefire0
  version: "0.1.0"
---

# UM Today Digest

Help University of Macau students replace manual newsletter scanning with a short,
source-linked digest and, when requested, a recurring proactive delivery.

This Skill requires access to public web pages. Python 3 is optional for deterministic
extraction; recurring delivery requires the host agent to provide scheduling or
automation.

## Public sources

Use only these public sources by default:

- UM Today archive: <https://www.um.edu.mo/um-today/>
- Dated issue: `https://www.um.edu.mo/um-today/detail/YYYYMMDD/`
- UM public event calendar: <https://www.um.edu.mo/eventscalendar/?ical=1>
- Individual event pages linked by those sources

Do not ask for a UM email password, student number, one-time code, or mailbox access.
Some registration or internal-service links may require the user to sign in after
opening them. Label that clearly and let the user complete the sign-in themselves.

## First use

If the user has not supplied preferences, collect only the fields that materially
change the recommendations:

- student or staff status, and study level when relevant;
- subjects or opportunity types they care about;
- usual free time or concrete calendar constraints;
- preferred language;
- whether they value Smart Points, CS, prizes, networking, or career opportunities.

Do not block an immediate digest on a long questionnaire. One compact question or
reasonable user-approved defaults are enough; unknown preferences remain unknown.

## Retrieve current information

When Python 3 and shell execution are available, run:

```bash
python3 scripts/fetch_um_today.py --days 30 --format json
```

Resolve the script path relative to this Skill directory. The script uses only the
Python standard library and does not authenticate. If it cannot run, browse the
public archive, latest dated issue, calendar feed, and relevant event detail pages
directly.

The newest issue may be from the previous working day. Treat “no new weekend or
holiday issue” as normal, not as a failure. Never present an old issue as published
today; always show its actual issue date.

## Select and rank

Apply hard exclusions before preference ranking:

1. Remove events and deadlines that have passed.
2. Exclude items explicitly limited to a different audience, such as staff-only
   notices for a student.
3. Mark, rather than hide, uncertain audience restrictions or possible schedule
   conflicts.
4. Deduplicate the same event across UM Today and the calendar using its canonical
   URL, UID, or normalized title plus start time.

Then rank by explicit interests, time compatibility, audience fit, deadline urgency,
location convenience, and the user's earlier feedback. Do not invent eligibility,
remaining seats, registration success, attendance credit, or organiser approval.

## Digest format

Default to three to five recommendations. Use the user's preferred language and keep
the digest readable on a phone. For each item include:

- title;
- date, time, and venue when available;
- one concrete “why this fits you” reason based on known preferences;
- registration deadline or immediate action when available;
- access note such as `public details` or `UM login may be required`;
- original official link.

Separate urgent deadlines from optional discovery picks. If nothing is a good match,
say so instead of padding the digest with weak recommendations.

End with compact feedback choices such as `Interested`, `Remind me`, and `Less like
this`. Update preferences only from the user's explicit response.

## Recurring delivery

Create, change, or disable a recurring task only after the user explicitly requests
it. Read [references/scheduling.md](references/scheduling.md) before doing so.

If the host supports native scheduling, prefer that mechanism. If it does not,
explain the limitation and offer an on-demand digest. A successful installation of
this Skill does not by itself prove that recurring delivery has been configured.

## Freshness and safety

- Cite official UM links for every recommendation.
- Do not send messages, register for events, or add calendar entries without the
  user's explicit request and any confirmation required by the host.
- Stay quiet on scheduled runs when there is no new issue, no changed deadline, and
  no newly relevant event.
- If retrieval fails, report the failing source and retain the last verified digest
  as dated information; do not fabricate a fresh result.
