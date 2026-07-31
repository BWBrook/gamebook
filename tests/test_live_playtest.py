from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import live_playtest as lp


class HarnessTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.story = self.root / "slice.md"
        self.rules = self.root / "rules.md"
        self.sheet = self.root / "sheet.md"
        self.story.write_text(
            "# Slice\n\n"
            "Introduction that must not be shown.\n\n"
            "## S01 — First\n\n"
            "Reached text.\n\n"
            "## A reader-facing inset\n\n"
            "Still part of the reached passage.\n\n"
            "Turn to **S02**.\n\n"
            "## S02 — Second\n\n"
            "Unreached secret.\n\n"
            "## E01 — Ending\n\n"
            "Terminal prose.\n",
            encoding="utf-8",
        )
        self.rules.write_text(
            "# Rules\n\n"
            "## Fortune\n\n"
            "Spend after the roll.\n\n"
            "### Timing\n\n"
            "The captured target does not change.\n\n"
            "## Endings\n\n"
            "Stop at a terminal.\n",
            encoding="utf-8",
        )
        self.sheet.write_text("# Sheet\n", encoding="utf-8")

    def fixed_clock(self) -> str:
        return "2026-07-31T10:00:00Z"

    def initial_state(self) -> dict[str, object]:
        return lp.build_initial_state(
            attributes={"BRN": 13, "AGI": 12, "CUN": 12, "WIL": 12},
            resources={"Fortune": (10, 10), "Stamina": (6, 6)},
            pressure=("Exposure", 0, 5),
            possessions=["Sword"],
            story_marks=[],
            start_passage="S01",
        )

    def start(self, session_id: str = "test-session") -> lp.LoadedSession:
        return lp.start_session(
            self.root / "sessions",
            session_id,
            self.story,
            self.rules,
            self.sheet,
            "Natural calibration playthrough",
            None,
            self.initial_state(),
            self.fixed_clock,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()


class MarkdownIndexTests(HarnessTestCase):
    def test_passage_index_returns_one_bounded_block(self) -> None:
        passages = lp.index_passages(self.story)
        self.assertEqual(list(passages), ["S01", "S02", "E01"])
        self.assertTrue(passages["S01"].startswith("## S01 — First\n"))
        self.assertIn("Reached text.", passages["S01"])
        self.assertIn("Still part of the reached passage.", passages["S01"])
        self.assertNotIn("Introduction", passages["S01"])
        self.assertNotIn("Unreached secret", passages["S01"])

    def test_duplicate_passage_identifier_is_rejected(self) -> None:
        self.story.write_text(
            "## S01 — First\n\nOne.\n\n## S01 — Duplicate\n\nTwo.\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(lp.HarnessError, "duplicate passage S01"):
            lp.index_passages(self.story)

    def test_rules_are_indexed_case_insensitively_without_h3_splitting(self) -> None:
        sections = lp.index_rule_sections(self.rules)
        self.assertEqual(list(sections), ["fortune", "endings"])
        self.assertIn("## Fortune", sections["fortune"])
        self.assertIn("Spend after", sections["fortune"])
        self.assertIn("### Timing", sections["fortune"])

    def test_named_value_parsers(self) -> None:
        self.assertEqual(lp.parse_named_integer("BRN=13"), ("BRN", 13))
        self.assertEqual(
            lp.parse_named_bound("Fortune=10/10"),
            ("Fortune", 10, 10),
        )
        with self.assertRaisesRegex(lp.HarnessError, "NAME=VALUE"):
            lp.parse_named_integer("BRN")
        with self.assertRaisesRegex(lp.HarnessError, "CURRENT/MAXIMUM"):
            lp.parse_named_bound("Fortune=10")


class PersistenceTests(HarnessTestCase):
    def test_start_writes_one_authoritative_event_and_cache(self) -> None:
        loaded = self.start()
        self.assertEqual(loaded.document["format_version"], 1)
        self.assertEqual(loaded.document["dice_mode"], "physical")
        self.assertEqual(loaded.document["observer_mode"], "neutral")
        self.assertEqual(loaded.document["last_event"], 1)
        self.assertEqual(loaded.events[0]["type"], "session_started")
        self.assertIsNone(loaded.events[0]["before"])
        self.assertEqual(
            loaded.events[0]["after"]["state"]["current_passage"],
            "S01",
        )
        self.assertEqual(
            lp.replay_events(loaded.events),
            loaded.events[-1]["after"],
        )

    def test_duplicate_session_identifier_is_rejected(self) -> None:
        self.start()
        with self.assertRaisesRegex(lp.HarnessError, "already exists"):
            self.start()

    def test_missing_start_passage_is_rejected(self) -> None:
        state = self.initial_state()
        state["current_passage"] = "S99"
        with self.assertRaisesRegex(lp.HarnessError, "undefined start passage S99"):
            lp.start_session(
                self.root / "sessions",
                "missing-passage",
                self.story,
                self.rules,
                self.sheet,
                "Missing-passage check",
                None,
                state,
                self.fixed_clock,
            )

    def test_reader_hash_drift_stops_loading(self) -> None:
        self.start()
        self.story.write_text("## S01 — Changed\n\nChanged.\n", encoding="utf-8")
        with self.assertRaisesRegex(lp.HarnessError, "reader file changed"):
            lp.load_session(self.root / "sessions", "test-session")

    def test_stale_cache_requires_explicit_recovery(self) -> None:
        loaded = self.start()
        document_path = loaded.directory / "session.json"
        document = json.loads(document_path.read_text(encoding="utf-8"))
        document["last_event"] = 0
        document_path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(lp.HarnessError, "recover-cache"):
            lp.load_session(self.root / "sessions", "test-session")

        recovered = lp.recover_cache(
            self.root / "sessions",
            "test-session",
            self.fixed_clock,
        )
        self.assertEqual(recovered.document["last_event"], 1)
        self.assertEqual(recovered.state, self.initial_state())

    def test_broken_event_chain_cannot_be_recovered(self) -> None:
        loaded = self.start()
        event_path = loaded.directory / "events.jsonl"
        event = json.loads(event_path.read_text(encoding="utf-8"))
        event["number"] = 2
        event_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(lp.HarnessError, "event number"):
            lp.recover_cache(
                self.root / "sessions",
                "test-session",
                self.fixed_clock,
            )
