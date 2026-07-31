from __future__ import annotations

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
