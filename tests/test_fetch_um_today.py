from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
from zoneinfo import ZoneInfo


SCRIPT = Path(__file__).parents[1] / "scripts" / "fetch_um_today.py"
SPEC = importlib.util.spec_from_file_location("fetch_um_today", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FetchUmTodayTests(unittest.TestCase):
    def test_discovers_latest_issue(self):
        sample = """
        <a href='/um-today/detail/20260910/'>old</a>
        <a href='/um-today/detail/20260911/'>latest</a>
        """
        self.assertEqual(
            MODULE.discover_latest_issue(sample),
            ("20260911", "https://www.um.edu.mo/um-today/detail/20260911/"),
        )

    def test_extracts_event_and_notice_tables(self):
        sample = """
        <table><tr><td>09:00 - 10:00</td><td><a href='/event/1/'>AI Talk</a></td>
        <td>E2-G019</td></tr></table>
        <table><tr><td><a href='https://e-bulletin.um.edu.mo/notice/1/'>Career notice</a></td>
        <td>SAO</td></tr></table>
        <table><tr><td><a href='https://myum.um.edu.mo/portal/'>Online Services and Information</a></td>
        <td></td></tr></table>
        """
        result = MODULE.classify_issue_tables(sample, MODULE.ARCHIVE_URL)
        self.assertEqual(result["events"][0]["title"], "AI Talk")
        self.assertEqual(result["events"][0]["url"], "https://www.um.edu.mo/event/1/")
        self.assertEqual(result["notices"][0]["department"], "SAO")
        self.assertEqual(len(result["notices"]), 1)

    def test_parses_and_filters_ical(self):
        sample = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART;TZID=Asia/Macau:20260915T110000
DTEND;TZID=Asia/Macau:20260915T120000
UID:one@example.test
SUMMARY:AI Research Workshop
DESCRIPTION:Public workshop
URL:https://www.um.edu.mo/event/1/
LOCATION:E2-G019
CATEGORIES:Workshop
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=Asia/Macau:20260915T120000
DTEND;TZID=Asia/Macau:20260915T130000
UID:cancelled@example.test
STATUS:CANCELLED
SUMMARY:Cancelled workshop
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=Asia/Macau:20200101T100000
UID:past-without-end@example.test
SUMMARY:Old event without an end time
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=Asia/Macau:20270115T110000
DTEND;TZID=Asia/Macau:20270115T120000
UID:two@example.test
SUMMARY:Too far away
END:VEVENT
END:VCALENDAR
"""
        start = datetime(2026, 9, 13, tzinfo=ZoneInfo("Asia/Macau"))
        events = MODULE.parse_ical(sample, start, 30)
        self.assertEqual([item["uid"] for item in events], ["one@example.test"])
        self.assertEqual(events[0]["venue"], "E2-G019")
        self.assertEqual(events[0]["status"], "CONFIRMED")

    def test_keeps_calendar_when_issue_detail_fails(self):
        archive = "<a href='/um-today/detail/20260911/'>latest</a>"
        calendar = "BEGIN:VCALENDAR\nEND:VCALENDAR\n"

        def fake_fetch(url):
            if url == MODULE.ARCHIVE_URL:
                return archive
            if url == MODULE.ICAL_URL:
                return calendar
            raise URLError("issue unavailable")

        with patch.object(MODULE, "fetch_text", side_effect=fake_fetch):
            payload = MODULE.build_payload(30)

        self.assertTrue(payload["source_status"]["archive"]["ok"])
        self.assertFalse(payload["source_status"]["issue"]["ok"])
        self.assertTrue(payload["source_status"]["calendar"]["ok"])
        self.assertEqual(payload["warnings"][0]["source"], "issue")


if __name__ == "__main__":
    unittest.main()
