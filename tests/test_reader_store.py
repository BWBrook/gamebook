from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tools import reader_engine as engine
from tools.reader_server import make_server
from tools.reader_store import Conflict, ReaderStore, StoreError, printed_result, source_snapshot


class ReaderStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.store = ReaderStore(self.directory)
        self.view = self.store.create("Test reading")

    def tearDown(self):
        self.temporary.cleanup()

    def action(self, action, payload):
        self.view = self.store.action(self.view["id"], action, payload, self.view["version"])
        return self.view

    def test_pending_roll_and_result_resume_without_repeated_costs(self):
        for choice in ["wait", "climb", "examine", "take_spear", "stalk"]:
            self.action("choose", {"choice_id": choice})
        self.assertEqual(self.view["state"]["marks"], [])
        self.action("roll", {"dice": [15, 20]})
        restored = ReaderStore(self.directory).read(self.view["id"])
        self.assertEqual(restored, self.view)
        self.action("fortune", {"spend": 3})
        self.assertEqual(self.view["state"]["fortune"], 7)
        restored = ReaderStore(self.directory).read(self.view["id"])
        self.assertEqual(restored["state"]["phase"], "result")
        self.action("continue", {})
        self.assertEqual(self.view["state"]["fortune"], 7)

    def test_stale_mutations_do_not_repeat_actions_or_overwrite_notes(self):
        stale = self.view["version"]
        self.action("choose", {"choice_id": "wait"})
        before = self.store._path(self.view["id"]).read_bytes()
        with self.assertRaises(Conflict):
            self.store.action(self.view["id"], "choose", {"choice_id": "climb"}, stale)
        with self.assertRaises(Conflict):
            self.store.note(self.view["id"], "My note", "", "S02", stale)
        self.assertEqual(before, self.store._path(self.view["id"]).read_bytes())

    def test_notes_keep_quotes_revision_state_and_survive_restart(self):
        quote = "A leap will put your fingers on the coping"
        self.view = self.store.note(self.view["id"], "This makes his competence clear.", quote, "S01", self.view["version"])
        self.action("choose", {"choice_id": "wait"})
        restored = ReaderStore(self.directory).read(self.view["id"], "S01")
        self.assertTrue(restored["read_only"])
        self.assertEqual(restored["choices"], [])
        note = restored["notes"][0]
        self.assertEqual(note["quote"], quote)
        self.assertEqual(note["state"]["exposure"], 0)
        self.assertEqual(note["state"]["passage"], "S01")
        self.assertEqual(note["source_revision"], restored["source_revision"])
        report = self.store.report(self.view["id"])
        self.assertIn(quote, report)
        self.assertIn("This makes his competence clear.", report)
        self.assertIn("S01 → S02", report)

    def test_unreached_or_invented_quote_notes_are_rejected(self):
        for passage, quote in [("S11", ""), ("S01", "a made up line")]:
            with self.assertRaises(StoreError):
                self.store.note(self.view["id"], "note", quote, passage, self.view["version"])
        with self.assertRaises(StoreError):
            self.store.read(self.view["id"], "E03")
        self.assertEqual(self.store.read(self.view["id"])["notes"], [])

    def test_engine_change_preserves_review_notes_and_blocks_play(self):
        with patch("tools.reader_store.engine_fingerprint", return_value="new engine"):
            view = self.store.read(self.view["id"])
            self.assertTrue(view["read_only"])
            self.assertIn("rules have changed", view["read_only_reason"])
            with self.assertRaises(Conflict):
                self.store.action(view["id"], "choose", {"choice_id": "climb"}, view["version"])
            annotated = self.store.note(view["id"], "A retrospective note.", "", "S01", view["version"])
            self.assertEqual(len(annotated["notes"]), 1)

    def test_failed_atomic_save_preserves_previous_document(self):
        before = self.store._path(self.view["id"]).read_bytes()
        with patch("tools.reader_store.os.replace", side_effect=OSError("simulated write failure")):
            with self.assertRaises(OSError):
                self.action("choose", {"choice_id": "wait"})
        self.assertEqual(before, self.store._path(self.view["id"]).read_bytes())
        self.assertFalse(list(self.directory.glob(".save-*")))

    def test_every_rolled_outcome_shows_the_book_s_own_result_line(self):
        snapshot = source_snapshot()
        for method, passage in (("stalk", "S05"), ("spear", "S11"), ("sword", "S11"), ("evade", "S11")):
            for outcome, label in engine.RESULT_LABELS.items():
                with self.subTest(method=method, outcome=outcome):
                    html = printed_result(snapshot, passage, {"method": method, "outcome": outcome})
                    self.assertTrue(html.startswith(f"<p><em>{label}:</em>"), html)
        evasion_death = printed_result(snapshot, "S11", {"method": "evade", "outcome": "natural 20"})
        self.assertIn("it is not fooled", evasion_death)
        self.assertEqual(printed_result(snapshot, "S11", None), "")

    def test_a_damaged_session_file_does_not_hide_other_readings(self):
        (self.directory / ("0" * 32 + ".json")).write_text("{not json")
        sessions = self.store.bootstrap()["sessions"]
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sum("error" in session for session in sessions), 1)

    def test_report_puts_notes_before_the_route(self):
        self.view = self.store.note(self.view["id"], "The rules read cleanly.", "", "rules", self.view["version"])
        self.action("choose", {"choice_id": "climb"})
        report = self.store.report(self.view["id"])
        self.assertLess(report.index("## Reader notes (1)"), report.index("## Route"))
        self.assertIn("### Player’s Rules", report)
        self.assertIn("| 1 | S01 | Climb now → S03 |", report)
        self.assertNotIn("```json", report)

    def test_session_snapshot_survives_source_changes_and_detects_corruption(self):
        original = self.view["passage"]["html"]
        with patch("tools.reader_store.source_snapshot", side_effect=RuntimeError("new source")):
            self.assertEqual(self.store.read(self.view["id"])["passage"]["html"], original)
        path = self.store._path(self.view["id"])
        document = json.loads(path.read_text())
        document["snapshot"]["rules"] = "changed"
        path.write_text(json.dumps(document))
        with self.assertRaisesRegex(StoreError, "saved reader text has changed"):
            self.store.read(self.view["id"])


class ReaderHTTPTests(unittest.TestCase):
    def test_local_http_actions_exports_and_request_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            server = make_server(0, Path(directory))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"

            def request(path, payload=None, headers=None):
                data = json.dumps(payload).encode() if payload is not None else None
                supplied = {"Content-Type": "application/json"} if data else {}
                supplied.update(headers or {})
                return urlopen(Request(base + path, data=data, headers=supplied))

            try:
                with request("/api/sessions", {"label": "HTTP test"}) as response:
                    view = json.load(response)
                with request(f"/api/sessions/{view['id']}/action", {"action": "choose", "payload": {"choice_id": "climb"}, "version": view["version"]}) as response:
                    self.assertEqual(json.load(response)["state"]["passage"], "S03")
                with request(f"/api/sessions/{view['id']}/report") as response:
                    self.assertIn("attachment", response.headers["Content-Disposition"])
                    self.assertIn("S01 → S03", response.read().decode())
                for path, payload, headers, status in [
                    ("/api/bootstrap", None, {"Host": "evil.example"}, 403),
                    ("/api/sessions", {}, {"Origin": "https://evil.example"}, 403),
                    ("/../.git/config", None, {}, 404),
                    ("/api/sessions", {}, {"Content-Type": "text/plain"}, 415),
                ]:
                    with self.subTest(path=path, headers=headers), self.assertRaises(HTTPError) as caught:
                        request(path, payload, headers)
                    self.assertEqual(caught.exception.code, status)
                    caught.exception.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
