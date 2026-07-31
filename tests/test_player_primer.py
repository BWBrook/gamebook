from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

from tools import live_playtest as lp


ROOT = Path(__file__).resolve().parents[1]
TOWER = ROOT / "stories/public_domain/howard/tower_of_the_elephant/playtest"
RULES = TOWER / "quick-rules.md"
SHEET = TOWER / "adventure-sheet.md"
STORY = TOWER / "slice-01.md"
S01_MARKER = "## S01 — The Outer Wall".encode("utf-8")
NUMBERED_BODY_SHA256 = (
    "2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496"
)
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class PlayerPrimerIntegrationTests(unittest.TestCase):
    def test_harness_exposes_the_complete_primer_lookup_surface(self) -> None:
        self.assertEqual(
            list(lp.index_rule_sections(RULES)),
            [
                "before you begin",
                "part i: how to play",
                "part ii: rules for this adventure",
                "rules at a glance",
            ],
        )

    def test_story_preamble_reader_links_resolve_in_rules_then_sheet_order(self) -> None:
        story = STORY.read_text(encoding="utf-8")
        preamble = story[:story.index(S01_MARKER.decode("utf-8"))]
        targets = LINK_RE.findall(preamble)
        self.assertEqual(targets, ["quick-rules.md", "adventure-sheet.md"])
        for target in targets:
            self.assertTrue((TOWER / target).is_file(), target)

    def test_numbered_passage_bytes_are_unchanged(self) -> None:
        payload = STORY.read_bytes()
        self.assertEqual(payload.count(S01_MARKER), 1)
        numbered = payload[payload.index(S01_MARKER):]
        self.assertEqual(
            hashlib.sha256(numbered).hexdigest(),
            NUMBERED_BODY_SHA256,
        )
