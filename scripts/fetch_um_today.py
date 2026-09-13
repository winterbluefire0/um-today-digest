#!/usr/bin/env python3
"""Fetch public UM Today and University of Macau calendar data as JSON.

This helper uses only the Python standard library. It does not access email, cookies,
or authenticated University of Macau services.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ARCHIVE_URL = "https://www.um.edu.mo/um-today/"
ISSUE_URL = "https://www.um.edu.mo/um-today/detail/{date}/"
ICAL_URL = "https://www.um.edu.mo/eventscalendar/?ical=1"
USER_AGENT = "um-today-digest/0.2 (+https://github.com/winterbluefire0/um-today-digest)"
MACAU = ZoneInfo("Asia/Macau")
FETCH_EXCEPTIONS = (HTTPError, URLError, TimeoutError, ValueError, OSError)
ALL_ERRORS = FETCH_EXCEPTIONS + (RuntimeError,)


def fetch_text(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def discover_latest_issue(archive_html: str) -> tuple[str, str]:
    dates = re.findall(r"/um-today/detail/(20\d{6})/?", archive_html)
    if not dates:
        raise ValueError("No dated UM Today issue was found in the public archive")
    issue_date = max(dates)
    return issue_date, ISSUE_URL.format(date=issue_date)


class TableParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.tables: list[list[dict[str, Any]]] = []
        self._table_stack: list[list[dict[str, Any]]] = []
        self._row_stack: list[dict[str, Any]] = []
        self._cell_stack: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "table":
            self._table_stack.append([])
        elif tag == "tr" and self._table_stack:
            self._row_stack.append({"cells": []})
        elif tag in {"td", "th"} and self._row_stack:
            self._cell_stack.append({"text_parts": [], "links": []})
        elif tag == "a" and self._cell_stack and values.get("href"):
            self._cell_stack[-1]["links"].append(
                urljoin(self.base_url, values["href"] or "")
            )
        elif tag == "br" and self._cell_stack:
            self._cell_stack[-1]["text_parts"].append(" ")

    def handle_data(self, data: str) -> None:
        if self._cell_stack:
            self._cell_stack[-1]["text_parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell_stack and self._row_stack:
            cell = self._cell_stack.pop()
            raw = "".join(cell.pop("text_parts"))
            cell["text"] = html.unescape(re.sub(r"\s+", " ", raw).strip())
            self._row_stack[-1]["cells"].append(cell)
        elif tag == "tr" and self._row_stack and self._table_stack:
            row = self._row_stack.pop()
            if any(cell.get("text") for cell in row["cells"]):
                self._table_stack[-1].append(row)
        elif tag == "table" and self._table_stack:
            rows = self._table_stack.pop()
            if rows:
                self.tables.append(rows)


def classify_issue_tables(issue_html: str, issue_url: str) -> dict[str, Any]:
    parser = TableParser(issue_url)
    parser.feed(issue_html)
    events: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    seen_events: set[tuple[Any, ...]] = set()
    seen_notices: set[tuple[Any, ...]] = set()

    for table_index, rows in enumerate(parser.tables):
        for row in rows:
            cells = row["cells"]
            texts = [cell["text"] for cell in cells]
            if len(cells) >= 3 and re.match(r"^\d{1,2}:\d{2}\s*[–-]", texts[0]):
                links = cells[1].get("links", [])
                event = {
                    "time": texts[0],
                    "title": texts[1],
                    "venue": texts[2],
                    "url": links[0] if links else None,
                    "access": "public_details",
                }
                key = (event["time"], event["title"], event["venue"], event["url"])
                if key not in seen_events:
                    events.append(event)
                    seen_events.add(key)
            elif len(cells) >= 2 and texts[0] and not texts[0].lower().startswith("more "):
                links = cells[0].get("links", [])
                if not links:
                    continue
                notice_url = links[0]
                hostname = (urlparse(notice_url).hostname or "").lower()
                if (
                    hostname == "myum.um.edu.mo"
                    or "online services and information" in texts[0].lower()
                ):
                    continue
                if hostname != "um.edu.mo" and not hostname.endswith(".um.edu.mo"):
                    continue
                notice = {
                    "table": table_index,
                    "title": texts[0],
                    "department": texts[1],
                    "url": notice_url,
                    "access": (
                        "um_login_may_be_required"
                        if hostname in {"e-bulletin.um.edu.mo", "myum.um.edu.mo"}
                        else "public_details"
                    ),
                }
                key = (notice["title"], notice["department"], notice["url"])
                if key not in seen_notices:
                    sections.append(notice)
                    seen_notices.add(key)

    return {"events": events, "notices": sections}


def unfold_ical(text: str) -> list[str]:
    lines = text.replace("\r\n", "\n").split("\n")
    unfolded: list[str] = []
    for line in lines:
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    return unfolded


def ical_unescape(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\N", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def parse_ical_datetime(key: str, value: str) -> datetime | None:
    try:
        if re.fullmatch(r"\d{8}", value):
            return datetime.strptime(value, "%Y%m%d").replace(tzinfo=MACAU)
        if value.endswith("Z"):
            return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
        tzid_match = re.search(r"(?:^|;)TZID=([^;:]+)", key)
        zone = MACAU
        if tzid_match:
            try:
                zone = ZoneInfo(tzid_match.group(1).strip('"'))
            except (KeyError, ValueError):
                zone = MACAU
        return parsed.replace(tzinfo=zone)
    except ValueError:
        return None


def parse_ical(text: str, start: datetime, days: int) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current: dict[str, list[tuple[str, str]]] | None = None

    for line in unfold_ical(text):
        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT" and current is not None:
            normalized: dict[str, str] = {}
            for base, values in current.items():
                normalized[base] = values[0][1]
            start_entries = current.get("DTSTART", [])
            end_entries = current.get("DTEND", [])
            event_start = parse_ical_datetime(*start_entries[0]) if start_entries else None
            event_end = parse_ical_datetime(*end_entries[0]) if end_entries else None
            horizon = start + timedelta(days=days)
            status = normalized.get("STATUS", "CONFIRMED").strip().upper()
            if status == "CANCELLED" or event_start is None:
                current = None
                continue
            effective_end = event_end or event_start
            if effective_end <= start:
                current = None
                continue
            if event_start > horizon:
                current = None
                continue
            events.append(
                {
                    "uid": normalized.get("UID"),
                    "title": ical_unescape(normalized.get("SUMMARY", "")),
                    "description": ical_unescape(normalized.get("DESCRIPTION", "")),
                    "start": event_start.isoformat() if event_start else None,
                    "end": event_end.isoformat() if event_end else None,
                    "venue": ical_unescape(normalized.get("LOCATION", "")),
                    "categories": ical_unescape(normalized.get("CATEGORIES", "")),
                    "url": normalized.get("URL"),
                    "last_modified": normalized.get("LAST-MODIFIED"),
                    "status": status,
                    "access": "public_details",
                }
            )
            current = None
            continue
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        base = key.split(";", 1)[0]
        current.setdefault(base, []).append((key, value))

    return sorted(events, key=lambda item: (item["start"] or "", item["title"]))


def build_payload(days: int) -> dict[str, Any]:
    now = datetime.now(MACAU)
    warnings: list[dict[str, str]] = []
    source_status: dict[str, dict[str, Any]] = {
        "archive": {"url": ARCHIVE_URL, "ok": False},
        "issue": {"url": None, "ok": False, "skipped": True},
        "calendar": {"url": ICAL_URL, "ok": False},
    }
    issue_url: str | None = None
    latest_issue: dict[str, Any] | None = None
    calendar_events: list[dict[str, Any]] = []

    try:
        archive_html = fetch_text(ARCHIVE_URL)
        issue_date, issue_url = discover_latest_issue(archive_html)
        source_status["archive"]["ok"] = True
        source_status["issue"] = {"url": issue_url, "ok": False}
        latest_issue = {"date": issue_date, "url": issue_url, "events": [], "notices": []}
        try:
            issue_html = fetch_text(issue_url)
            latest_issue.update(classify_issue_tables(issue_html, issue_url))
            source_status["issue"]["ok"] = True
        except FETCH_EXCEPTIONS as exc:
            warnings.append({"source": "issue", "url": issue_url, "error": str(exc)})
    except FETCH_EXCEPTIONS as exc:
        warnings.append({"source": "archive", "url": ARCHIVE_URL, "error": str(exc)})

    try:
        calendar_text = fetch_text(ICAL_URL)
        calendar_events = parse_ical(calendar_text, now, days)
        source_status["calendar"]["ok"] = True
    except FETCH_EXCEPTIONS as exc:
        warnings.append({"source": "calendar", "url": ICAL_URL, "error": str(exc)})

    if not source_status["archive"]["ok"] and not source_status["calendar"]["ok"]:
        detail = "; ".join(f"{item['source']}: {item['error']}" for item in warnings)
        raise RuntimeError(f"All public UM sources failed ({detail})")

    return {
        "generated_at": now.isoformat(),
        "sources": {"archive": ARCHIVE_URL, "issue": issue_url, "calendar": ICAL_URL},
        "source_status": source_status,
        "warnings": warnings,
        "latest_issue": latest_issue,
        "calendar_events": calendar_events,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30, help="Upcoming calendar horizon")
    parser.add_argument("--format", choices=("json",), default="json")
    args = parser.parse_args()
    if not 1 <= args.days <= 366:
        parser.error("--days must be between 1 and 366")
    try:
        payload = build_payload(args.days)
    except ALL_ERRORS as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
