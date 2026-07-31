# Live Playtest Observer Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and calibrate a thin local observer harness through which Barry can play the current *Tower of the Elephant* slice live with physical dice while Codex neutrally presents reached prose, resolves mechanics, tracks state, and preserves an auditable local record.

**Architecture:** Keep the three reader-facing Markdown files authoritative and extract only passage and rules-section boundaries. A single Python standard-library operator CLI records an append-only JSON Lines event stream, maintains an atomically replaced state cache, and derives a deterministic Markdown report; choices, authored consequences, and transitions remain explicit operator inputs rather than a second gamebook schema. Implement the tool test-first in focused internal sections, then run one natural live calibration session before considering permanent formats or AI facilitation.

**Tech Stack:** Python 3.10+ standard library (`argparse`, `copy`, `dataclasses`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `tempfile`, `unittest`), Markdown, JSON Lines, Git, physical d20s, and `uv` for a Python 3.10 compatibility check only

## Global Constraints

- Begin from local `main` at or after approved design commit `0b5b857`; `origin/main` does not yet contain that design.
- Use Python 3.10 or newer and the Python standard library only.
- Add no package manifest, lockfile, application framework, database, network service, model API, provider integration, or third-party runtime dependency.
- Keep `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`, `quick-rules.md`, and `adventure-sheet.md` authoritative and unchanged.
- Hash all three reader-facing files when a session starts and refuse normal mutation or resume after any hash changes.
- Parse passage and rules headings only. Do not parse prose into legal choices, authored outcome tables, enemy statistics, hidden conditions, or a permanent schema.
- Display only the currently reached passage during ordinary play.
- Keep physical dice and neutral-observer mode as the only live modes in this increment.
- Require the operator to record a choice before a roll or transition and to enter every authored state change and destination explicitly.
- Resolve standard rolls with one d20, Advantage with two d20s keeping the lower result, and Disadvantage with two d20s keeping the higher result.
- Select the die before checking natural results, calculating margin, or considering Fortune.
- Record arithmetic margin as `captured target - selected die` even for locked natural results; mark the margin resolution-inert for a selected natural 1 or natural 20.
- Lock a selected natural 1 or natural 20 and forbid any Fortune command for that roll.
- For an ordinary selected die, allow a Fortune spend from zero through current Fortune, subtract it arithmetically from the selected result, and do not invent a lower clamp at 1. The original selected face remains the basis for natural-result handling.
- Deduct Fortune only when the Fortune decision is recorded; the captured target remains unchanged.
- Keep Fortune, Stamina, Exposure, possessions, and story marks within their
  approved representations; reject a resource update that would cross an
  inclusive recorded bound.
- Saturate a positive Exposure change at its printed maximum of 5; reject a negative change below 0 or a direct correction outside 0-5.
- Reject invalid input before appending an event or replacing the cache.
- Keep `events.jsonl` append-only and authoritative. Treat `session.json` as an atomic derived cache and rebuild it only through the explicit `recover-cache` command.
- Preserve original mistakes and add compensating `correction` events; never rewrite or remove prior events.
- Reject all state-changing operations after a session is finished. Permit read-only state inspection and report regeneration.
- Keep `.playtest/` ignored by Git. Raw voice-transcribed comments, local timing, and reports remain untracked unless Barry separately approves a curated summary.
- Store voice-transcribed text as received. Do not call it raw audio or claim that the harness retained audio.
- Do not recommend or rank choices, rewrite prose, adjudicate authored fiction automatically, reveal unread passages, run balance simulations, author the upper tower, or design the permanent companion.
- Use temporary directories in every automated session test so the test suite never creates raw evidence below the repository's `.playtest/`.
- Leave `README.md` unchanged in this increment: the observer remains explicitly preliminary to the permanent deterministic and AI-guided tools mentioned there.

---

## File map

- Create `tools/live_playtest.py` — Python 3.10-compatible standard-library
  module and command-line entry point. Internal sections, in order:
  Markdown indexing, value parsing, state validation, event persistence,
  observer operations, dice and Fortune, sheet mutation, lifecycle and
  corrections, reporting, and CLI dispatch.
- Create `tests/test_live_playtest.py` — `unittest` unit, persistence, CLI, and
  real-*Tower* integration tests. It imports `tools.live_playtest` as an
  implicit namespace package; do not add `tools/__init__.py`.
- Create `docs/playtesting/live-playtest.md` — operator protocol, exact command
  examples, neutral-observer boundary, evidence handling, recovery procedure,
  and live calibration checklist.
- Modify `.gitignore` — add the labelled `# Local playtest sessions` section
  containing `.playtest/`.
- Retain
  `docs/superpowers/specs/2026-07-31-live-playtest-observer-harness-design.md`
  as the governing approved design.
- Retain every file below
  `stories/public_domain/howard/tower_of_the_elephant/playtest/` unchanged.

## Runtime records

Every session lives at `.playtest/sessions/<session-id>/` by default:

```text
session.json
events.jsonl
report.md
```

`session.json` has this stable version-1 shape:

```json
{
  "format_version": 1,
  "harness_version": "0.1.0",
  "session_id": "tower-calibration-01",
  "purpose": "Natural calibration playthrough",
  "hypothesis": null,
  "reader_files": {
    "story": {"path": "/absolute/path/slice-01.md", "sha256": "hex"},
    "rules": {"path": "/absolute/path/quick-rules.md", "sha256": "hex"},
    "sheet": {"path": "/absolute/path/adventure-sheet.md", "sha256": "hex"}
  },
  "dice_mode": "physical",
  "observer_mode": "neutral",
  "initial_state": {},
  "current_state": {},
  "workflow": {"choice": null, "roll": null},
  "last_event": 1,
  "created_at": "RFC-3339 UTC timestamp",
  "updated_at": "RFC-3339 UTC timestamp"
}
```

The state objects stored under `initial_state` and `current_state` have exactly
these keys:

```json
{
  "attributes": {"BRN": 13, "AGI": 12, "CUN": 12, "WIL": 12},
  "resources": {
    "Fortune": {"current": 10, "maximum": 10},
    "Stamina": {"current": 6, "maximum": 6}
  },
  "pressure": {"name": "Exposure", "current": 0, "maximum": 5},
  "possessions": ["Sword"],
  "story_marks": [],
  "current_passage": "S01",
  "status": "active"
}
```

The operational `workflow` remains outside the reader sheet. `choice` holds
the current committed choice until a transition. `roll` holds the captured
target, physical dice, selected die, natural lock, margins, Fortune status,
and final result until the transition clears it.

Every `events.jsonl` object has:

```json
{
  "number": 2,
  "type": "passage_shown",
  "timestamp": "RFC-3339 UTC timestamp",
  "passage": "S01",
  "data": {},
  "before": {"state": {}, "workflow": {}},
  "after": {"state": {}, "workflow": {}}
}
```

The first `session_started` event has `before: null` and a complete initial
snapshot in `after`. All later `before` snapshots must equal the preceding
event's `after` snapshot. Full snapshots are intentionally verbose: they keep
replay and correction auditable without requiring future code to reinterpret
old authored outcomes.

## Public Python interfaces

All functions below live in `tools/live_playtest.py`. Later tasks must use
these names and signatures consistently.

```python
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

JSONDict = dict[str, Any]
Clock = Callable[[], str]

class HarnessError(ValueError):
    pass

@dataclass
class LoadedSession:
    directory: Path
    document: JSONDict
    events: list[JSONDict]
    state: JSONDict
    workflow: JSONDict
```

This table locks the remaining signatures; Tasks 1-7 provide their complete
behaviour and concrete algorithms.

| Function | Locked signature |
| --- | --- |
| Time and files | `utc_now() -> str`; `sha256_file(path: Path) -> str` |
| Markdown | `index_passages(path: Path) -> dict[str, str]`; `index_rule_sections(path: Path) -> dict[str, str]` |
| CLI values | `parse_named_integer(value: str) -> tuple[str, int]`; `parse_named_bound(value: str) -> tuple[str, int, int]` |
| Initial state | `build_initial_state(attributes: dict[str, int], resources: dict[str, tuple[int, int]], pressure: tuple[str, int, int], possessions: Sequence[str], story_marks: Sequence[str], start_passage: str) -> JSONDict` |
| Start | `start_session(sessions_dir: Path, session_id: str, story_path: Path, rules_path: Path, sheet_path: Path, purpose: str, hypothesis: str \| None, initial_state: JSONDict, clock: Clock = utc_now) -> LoadedSession` |
| Event store | `read_events(path: Path) -> list[JSONDict]`; `replay_events(events: Sequence[JSONDict]) -> JSONDict`; `load_session(sessions_dir: Path, session_id: str, *, verify_hashes: bool = True, verify_cache: bool = True) -> LoadedSession` |
| Event append | `append_event(loaded: LoadedSession, event_type: str, data: JSONDict, new_state: JSONDict, new_workflow: JSONDict, clock: Clock = utc_now) -> JSONDict` |
| Recovery | `recover_cache(sessions_dir: Path, session_id: str, clock: Clock = utc_now) -> LoadedSession` |
| Presentation | `show_current_passage(loaded: LoadedSession, clock: Clock = utc_now) -> str`; `format_state(state: JSONDict) -> str` |
| Notes and rules | `record_note(loaded: LoadedSession, kind: str, text: str, clock: Clock = utc_now) -> JSONDict`; `record_rules_lookup(loaded: LoadedSession, section: str, clock: Clock = utc_now) -> str` |
| Choice | `record_choice(loaded: LoadedSession, text: str, method: str \| None, intended_destination: str \| None, clock: Clock = utc_now) -> JSONDict` |
| Dice | `resolve_roll(attribute: str, target: int, mode: str, dice: Sequence[int]) -> JSONDict`; `record_roll(loaded: LoadedSession, attribute: str, mode: str, dice: Sequence[int], clock: Clock = utc_now) -> JSONDict` |
| Fortune | `apply_fortune(roll: JSONDict, spend: int, available: int) -> JSONDict`; `record_fortune(loaded: LoadedSession, spend: int, clock: Clock = utc_now) -> JSONDict` |
| Resources | `change_resource(loaded: LoadedSession, name: str, delta: int, reason: str, clock: Clock = utc_now) -> JSONDict`; `change_pressure(loaded: LoadedSession, delta: int, reason: str, clock: Clock = utc_now) -> JSONDict` |
| Collections | `change_collection(loaded: LoadedSession, collection: str, action: str, name: str, reason: str, *, allow_duplicate: bool = False, clock: Clock = utc_now) -> JSONDict` |
| Transition | `goto_passage(loaded: LoadedSession, destination: str, clock: Clock = utc_now) -> JSONDict` |
| Correction | `correct_session(loaded: LoadedSession, target_event: int, reason: str, operation: str, *, name: str \| None = None, value: int \| str \| None = None, replacement_text: str \| None = None, clock: Clock = utc_now) -> JSONDict` |
| Lifecycle | `pause_session(loaded: LoadedSession, reason: str, clock: Clock = utc_now) -> JSONDict`; `resume_session(loaded: LoadedSession, clock: Clock = utc_now) -> JSONDict`; `finish_session(loaded: LoadedSession, outcome: str, clock: Clock = utc_now) -> JSONDict` |
| Report | `render_report(document: JSONDict, events: Sequence[JSONDict]) -> str`; `write_report(loaded: LoadedSession) -> Path` |
| CLI | `build_parser() -> Any`; `main(argv: Sequence[str] \| None = None) -> int` |

## CLI contract

All commands use:

```bash
python3 tools/live_playtest.py \
  --sessions-dir .playtest/sessions \
  <command> <arguments>
```

The default `--sessions-dir` is `.playtest/sessions`.

| Command | Exact arguments |
| --- | --- |
| `start` | `SESSION_ID --story PATH --rules PATH --sheet PATH --purpose TEXT [--hypothesis TEXT] [--start-passage S01] --attribute NAME=VALUE --resource NAME=CURRENT/MAX --pressure NAME=CURRENT/MAX [--possession NAME] [--mark NAME]`; attribute, resource, possession, and mark options are repeatable |
| `show` | `SESSION_ID` |
| `state` | `SESSION_ID` |
| `note` | `SESSION_ID --kind {player,operator,rules-question} --text TEXT` |
| `lookup` | `SESSION_ID --section HEADING` |
| `choose` | `SESSION_ID --text TEXT [--method TEXT] [--destination PASSAGE_ID]` |
| `roll` | `SESSION_ID --attribute NAME --mode {standard,advantage,disadvantage} --die FACE [--die FACE]` |
| `fortune` | `SESSION_ID --spend INTEGER` |
| `apply resource` | `SESSION_ID NAME --delta INTEGER --reason TEXT` |
| `apply pressure` | `SESSION_ID --delta INTEGER --reason TEXT` |
| `apply possession` | `SESSION_ID {add,consume,remove} NAME --reason TEXT [--allow-duplicate]` |
| `apply mark` | `SESSION_ID {add,consume,remove} NAME --reason TEXT [--allow-duplicate]` |
| `goto` | `SESSION_ID PASSAGE_ID` |
| `correct` | `SESSION_ID --target-event INTEGER --reason TEXT` plus exactly one correction option described in Task 5 |
| `recover-cache` | `SESSION_ID` |
| `pause` | `SESSION_ID --reason TEXT` |
| `resume` | `SESSION_ID` |
| `finish` | `SESSION_ID --outcome TEXT` |
| `report` | `SESSION_ID` |

Successful mutation commands print the event and complete current state as
UTF-8 JSON. `show` and `lookup` print Markdown. `state` prints the human-readable
complete sheet. `report` prints the generated path. A `HarnessError` prints one
`error: <message>` line to standard error and exits with status 2.

---

### Task 1: Index reader Markdown and establish the private runtime boundary

**Files:**

- Create: `tools/live_playtest.py`
- Create: `tests/test_live_playtest.py`
- Modify: `.gitignore`
- Read:
  `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`
- Read:
  `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`

**Interfaces:**

- Consumes: UTF-8 Markdown with passage headings such as
  `## S01 — The Outer Wall`, ending headings such as
  `## E03 — Death in the Garden`, and ordinary reader-rule `##` headings.
- Produces: `HarnessError`, `sha256_file`, `index_passages`,
  `index_rule_sections`, `parse_named_integer`, and `parse_named_bound`.
  Later tasks rely on each returned section containing its heading and body,
  ending immediately before the next `##` heading.

- [ ] **Step 1: Add failing extraction and parser tests**

Create `tests/test_live_playtest.py` with a reusable temporary-file fixture and
these initial cases:

```python
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
```

- [ ] **Step 2: Run the tests and verify the missing module fails**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: import failure because `tools.live_playtest` does not exist.

- [ ] **Step 3: Implement exact heading extraction and value parsing**

Create `tools/live_playtest.py` with Python 3.10-compatible imports, constants,
and these algorithms:

```python
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FORMAT_VERSION = 1
HARNESS_VERSION = "0.1.0"
PASSAGE_HEADING = re.compile(
    r"^## (?P<identifier>[SE]\d{2}) — (?P<title>\S.*)$"
)
H2_HEADING = re.compile(r"^## (?P<title>\S.*)$")
SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

JSONDict = dict[str, Any]
Clock = Callable[[], str]


class HarnessError(ValueError):
    pass


@dataclass
class LoadedSession:
    directory: Path
    document: JSONDict
    events: list[JSONDict]
    state: JSONDict
    workflow: JSONDict


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise HarnessError(f"cannot read {path}: {error}") from error
    return hashlib.sha256(payload).hexdigest()


def _markdown_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise HarnessError(f"cannot read UTF-8 Markdown {path}: {error}") from error


def _blocks(
    lines: Sequence[str],
    starts: Sequence[int],
) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        text = "\n".join(lines[start:end]).rstrip() + "\n"
        blocks.append((lines[start], text))
    return blocks


def index_passages(path: Path) -> dict[str, str]:
    lines = _markdown_lines(path)
    starts = [
        index
        for index, line in enumerate(lines)
        if PASSAGE_HEADING.fullmatch(line) is not None
    ]
    passages: dict[str, str] = {}
    for heading, block in _blocks(lines, starts):
        match = PASSAGE_HEADING.fullmatch(heading)
        if match is None:
            raise HarnessError(f"internal passage-index error at {heading!r}")
        identifier = match.group("identifier")
        if identifier in passages:
            raise HarnessError(f"duplicate passage {identifier} in {path}")
        passages[identifier] = block
    if not passages:
        raise HarnessError(f"no passage headings found in {path}")
    return passages


def index_rule_sections(path: Path) -> dict[str, str]:
    lines = _markdown_lines(path)
    starts = [
        index
        for index, line in enumerate(lines)
        if H2_HEADING.fullmatch(line) is not None
    ]
    sections: dict[str, str] = {}
    for heading, block in _blocks(lines, starts):
        match = H2_HEADING.fullmatch(heading)
        if match is None:
            raise HarnessError(f"internal rules-index error at {heading!r}")
        key = match.group("title").casefold()
        if key in sections:
            raise HarnessError(f"duplicate rules section {match.group('title')} in {path}")
        sections[key] = block
    if not sections:
        raise HarnessError(f"no rules sections found in {path}")
    return sections


def parse_named_integer(value: str) -> tuple[str, int]:
    match = re.fullmatch(r"([^=]+)=(-?\d+)", value)
    if match is None:
        raise HarnessError(f"expected NAME=VALUE, received {value!r}")
    return match.group(1).strip(), int(match.group(2))


def parse_named_bound(value: str) -> tuple[str, int, int]:
    match = re.fullmatch(r"([^=]+)=(-?\d+)/(-?\d+)", value)
    if match is None:
        raise HarnessError(
            f"expected NAME=CURRENT/MAXIMUM, received {value!r}"
        )
    return match.group(1).strip(), int(match.group(2)), int(match.group(3))
```

Do not let `index_passages` return the document introduction, adjacent
passages, a passage inventory, or author-facing files.

- [ ] **Step 4: Ignore all raw session material**

Insert this labelled section in `.gitignore` between local worktrees and
temporary files:

```gitignore
# Local playtest sessions
.playtest/
```

- [ ] **Step 5: Run the focused tests and inspect the diff**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
git status --short
```

Expected: four tests pass; only `.gitignore`, `tools/live_playtest.py`, and
`tests/test_live_playtest.py` are changed.

- [ ] **Step 6: Commit the Markdown boundary**

Run:

```bash
git add .gitignore tools/live_playtest.py tests/test_live_playtest.py
git diff --cached --check
git commit -m "feat: index live playtest markdown"
```

### Task 2: Add append-only session persistence, replay, drift checks, and recovery

**Files:**

- Modify: `tools/live_playtest.py`
- Modify: `tests/test_live_playtest.py`

**Interfaces:**

- Consumes: indexed story and rules Markdown, a readable sheet path, the
  version-1 state shape, and an injected RFC-3339 clock.
- Produces: `build_initial_state`, `start_session`, `read_events`,
  `replay_events`, `load_session`, `append_event`, and `recover_cache`.
  Every later mutation must load through `load_session` and write through
  `append_event`.

- [ ] **Step 1: Add failing persistence and recovery tests**

Extend the shared fixture with:

```python
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
```

Add cases that assert:

```python
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
```

Add `import json` to the test imports.

- [ ] **Step 2: Run the persistence tests and verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_live_playtest.PersistenceTests -v
```

Expected: failures naming the unimplemented state and session functions.

- [ ] **Step 3: Implement state validation and the version-1 session start**

Implement `build_initial_state` so that it:

1. requires at least one attribute;
2. requires every attribute value to be an integer from 0 through 20;
3. requires case-insensitively unique, non-empty attribute and resource names;
4. requires the resource set to contain exactly `Fortune` and `Stamina`;
5. requires each resource to satisfy `0 <= current <= maximum`;
6. requires non-empty pressure name and `0 <= current <= maximum`;
7. rejects case-insensitive duplicate possessions or story marks;
8. requires `start_passage` to match `[SE]\d{2}`; and
9. returns fresh lists and dictionaries in the exact state shape above.

Implement session creation with the following concrete sequence:

```python
def _snapshot(state: JSONDict, workflow: JSONDict) -> JSONDict:
    return {
        "state": copy.deepcopy(state),
        "workflow": copy.deepcopy(workflow),
    }


def _atomic_write_json(path: Path, payload: JSONDict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def _append_json_line(path: Path, payload: JSONDict) -> None:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded + "\n")
        handle.flush()
        os.fsync(handle.fileno())
```

`start_session` must validate the session ID, reject an existing directory,
require a non-empty purpose, reject a supplied blank hypothesis,
index the story and rules, require the starting passage to exist, require the
sheet to be readable, resolve all three paths to absolute paths, calculate all
three SHA-256 hashes, and create the first event before making the completed
session directory visible. Build the files in a temporary sibling directory
and rename that directory to the final session path only after both
`events.jsonl` and `session.json` have been flushed.

The `session_started` event stores purpose, hypothesis, reader-file records,
and modes in `data`; its `after` snapshot contains the initial state and
`{"choice": None, "roll": None}` workflow.

- [ ] **Step 4: Implement strict event replay and verified loading**

Implement `read_events` as UTF-8 JSON Lines parsing with line-numbered errors.
Implement `replay_events` with these exact invariants:

```python
def replay_events(events: Sequence[JSONDict]) -> JSONDict:
    if not events:
        raise HarnessError("event log is empty")

    previous: JSONDict | None = None
    for expected_number, event in enumerate(events, start=1):
        if event.get("number") != expected_number:
            raise HarnessError(
                f"event number mismatch: expected {expected_number}, "
                f"received {event.get('number')!r}"
            )
        if expected_number == 1:
            if event.get("type") != "session_started" or event.get("before") is not None:
                raise HarnessError("event 1 must be session_started with before null")
        elif event.get("before") != previous:
            raise HarnessError(
                f"event {expected_number} before snapshot does not match event "
                f"{expected_number - 1}"
            )
        after = event.get("after")
        if not isinstance(after, dict) or set(after) != {"state", "workflow"}:
            raise HarnessError(f"event {expected_number} has an invalid after snapshot")
        previous = after

    return copy.deepcopy(previous)
```

`load_session` must:

- read `session.json` and `events.jsonl`;
- reject unsupported `format_version` or `harness_version`;
- verify all three stored paths and hashes when `verify_hashes=True`;
- replay the complete log;
- compare replayed `state`, `workflow`, and last event number with the cache
  when `verify_cache=True`; and
- on cache mismatch, name `recover-cache` as the permitted next action.

- [ ] **Step 5: Implement ordered append and explicit cache recovery**

`append_event` must deep-copy the before and after snapshots, assign
`number = loaded.document["last_event"] + 1`, use the old current passage in
`passage`, append and flush the JSON line first, then atomically replace
`session.json`. Update the supplied `LoadedSession` in memory only after both
writes succeed.

`recover_cache` must call `load_session` with `verify_cache=False`, still
verify reader hashes and the complete event chain, then atomically replace only
the derived cache fields:

```python
document["current_state"] = snapshot["state"]
document["workflow"] = snapshot["workflow"]
document["last_event"] = len(events)
document["updated_at"] = clock()
```

It must not append a recovery event, rewrite `events.jsonl`, change initial
state, or bypass content drift.

- [ ] **Step 6: Run persistence and extraction tests**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

Expected: all extraction and persistence tests pass.

- [ ] **Step 7: Commit the session ledger**

Run:

```bash
git add tools/live_playtest.py tests/test_live_playtest.py
git diff --cached --check
git commit -m "feat: add live playtest session ledger"
```

### Task 3: Record reached prose, narration, rules lookups, choices, and transitions

**Files:**

- Modify: `tools/live_playtest.py`
- Modify: `tests/test_live_playtest.py`

**Interfaces:**

- Consumes: a verified active `LoadedSession`, current passage, reader rules,
  and explicit operator input.
- Produces: `show_current_passage`, `format_state`, `record_note`,
  `record_rules_lookup`, `record_choice`, and `goto_passage`.
  A choice remains in `workflow["choice"]` until `goto_passage` clears the
  workflow.

- [ ] **Step 1: Add failing observer-operation tests**

Add tests for:

```python
class ObserverOperationTests(HarnessTestCase):
    def test_show_returns_only_current_passage_and_logs_it(self) -> None:
        loaded = self.start()
        shown = lp.show_current_passage(loaded, self.fixed_clock)
        self.assertIn("## S01 — First", shown)
        self.assertIn("Reached text.", shown)
        self.assertNotIn("Unreached secret", shown)
        self.assertEqual(loaded.events[-1]["type"], "passage_shown")

    def test_notes_preserve_received_text_and_kind(self) -> None:
        loaded = self.start()
        text = "I don't trust that silence—yet."
        lp.record_note(loaded, "player", text, self.fixed_clock)
        self.assertEqual(loaded.events[-1]["data"]["text"], text)
        self.assertEqual(loaded.events[-1]["data"]["kind"], "player")

    def test_rules_lookup_is_case_insensitive_and_logged(self) -> None:
        loaded = self.start()
        section = lp.record_rules_lookup(loaded, "FORTUNE", self.fixed_clock)
        self.assertIn("Spend after the roll.", section)
        self.assertEqual(loaded.events[-1]["type"], "rules_lookup")
        self.assertEqual(loaded.events[-1]["data"]["section"], "Fortune")

    def test_choice_precedes_valid_referenced_transition(self) -> None:
        loaded = self.start()
        lp.record_choice(
            loaded,
            "Go on",
            None,
            "S02",
            self.fixed_clock,
        )
        lp.goto_passage(loaded, "S02", self.fixed_clock)
        self.assertEqual(loaded.state["current_passage"], "S02")
        self.assertEqual(loaded.workflow, {"choice": None, "roll": None})

    def test_unreferenced_or_undefined_destination_does_not_mutate(self) -> None:
        loaded = self.start()
        lp.record_choice(loaded, "Invent a route", None, "E01", self.fixed_clock)
        before_log = (loaded.directory / "events.jsonl").read_bytes()
        before_cache = (loaded.directory / "session.json").read_bytes()
        with self.assertRaisesRegex(lp.HarnessError, "not referenced"):
            lp.goto_passage(loaded, "E01", self.fixed_clock)
        self.assertEqual(
            (loaded.directory / "events.jsonl").read_bytes(),
            before_log,
        )
        self.assertEqual(
            (loaded.directory / "session.json").read_bytes(),
            before_cache,
        )
        with self.assertRaisesRegex(lp.HarnessError, "undefined passage S99"):
            lp.goto_passage(loaded, "S99", self.fixed_clock)
```

Also test rejection of an empty note, an unknown note kind, an unknown rules
heading, a second unresolved choice, and a transition before a choice.

- [ ] **Step 2: Run the observer tests and verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_live_playtest.ObserverOperationTests -v
```

Expected: failures naming the unimplemented observer functions.

- [ ] **Step 3: Implement active-session guards and passive records**

Add:

```python
def _require_active(loaded: LoadedSession, operation: str) -> None:
    status = loaded.state["status"]
    if status != "active":
        raise HarnessError(
            f"cannot {operation} while session status is {status}"
        )
```

`show_current_passage` must require active status, index only the stored story
path, fetch only `loaded.state["current_passage"]`, append a
`passage_shown` event with unchanged state and workflow, and return that one
block.

`record_note` accepts exactly `player`, `operator`, or `rules-question`;
requires non-whitespace text; stores it unchanged; and appends `player_note`,
`operator_note`, or `rules_question` respectively.

`record_rules_lookup` finds a case-insensitive exact `##` heading in the stored
rules file, records the canonical heading text and its SHA-256 digest, and
returns only that section.

`format_state` returns all sheet fields in this order:

```text
Passage: S01
Status: active
Attributes: AGI 12 | BRN 13 | CUN 12 | WIL 12
Fortune: 10/10
Stamina: 6/6
Exposure: 0/5
Possessions: Sword
Story marks: —
```

Sort attributes and resources by name for deterministic output, but preserve
possession and story-mark insertion order.

- [ ] **Step 4: Implement committed choice and destination sanity checking**

`record_choice` must:

- require active status and non-whitespace choice text;
- reject a second choice while `workflow["choice"]` is populated;
- if supplied, require `intended_destination` to match `[SE]\d{2}`;
- store text, method, destination, and the choice event number in workflow; and
- append `choice_committed` without changing reader state.

`goto_passage` must validate completely before `append_event`:

1. an active choice exists;
2. no ordinary roll is waiting for a Fortune decision;
3. the destination is defined in the story passage index;
4. the destination identifier occurs as a whole token within the current
   passage block; and
5. if the choice recorded an intended destination, it equals the supplied
   destination.

On success, copy state, set `current_passage`, append
`passage_transition` data containing `from`, `to`, and the choice-event number,
and reset workflow to `{"choice": None, "roll": None}`. This is a reference
sanity check only; do not interpret conditional prose or decide that an
authored result is legal.

- [ ] **Step 5: Run all tests and commit observer records**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
git add tools/live_playtest.py tests/test_live_playtest.py
git diff --cached --check
git commit -m "feat: record live playtest navigation"
```

### Task 4: Resolve physical dice and post-roll Fortune

**Files:**

- Modify: `tools/live_playtest.py`
- Modify: `tests/test_live_playtest.py`

**Interfaces:**

- Consumes: a committed choice, a named current sheet attribute or current
  Fortune, roll mode, reported physical faces, and a later explicit Fortune
  spend.
- Produces: pure `resolve_roll` and `apply_fortune` calculations plus
  event-recording `record_roll` and `record_fortune`. Later state and report
  code reads the resulting workflow keys exactly as asserted below.

- [ ] **Step 1: Add failing pure-mechanics tests**

Add table-driven cases:

```python
class RollMechanicsTests(unittest.TestCase):
    def test_standard_advantage_and_disadvantage_selection(self) -> None:
        standard = lp.resolve_roll("CUN", 12, "standard", [15])
        advantage = lp.resolve_roll("BRN", 13, "advantage", [6, 20])
        disadvantage = lp.resolve_roll("AGI", 12, "disadvantage", [3, 17])
        self.assertEqual(standard["selected_die"], 15)
        self.assertEqual(standard["provisional_margin"], -3)
        self.assertEqual(advantage["selected_die"], 6)
        self.assertEqual(advantage["selected_index"], 0)
        self.assertIsNone(advantage["natural"])
        self.assertEqual(disadvantage["selected_die"], 17)

    def test_only_the_selected_die_can_lock(self) -> None:
        result = lp.resolve_roll("BRN", 13, "advantage", [6, 20])
        self.assertIsNone(result["natural"])
        result = lp.resolve_roll("BRN", 13, "disadvantage", [1, 20])
        self.assertEqual(result["natural"], 20)
        self.assertEqual(result["provisional_margin"], -7)
        self.assertTrue(result["margin_is_resolution_inert"])

    def test_selected_natural_one_is_locked(self) -> None:
        result = lp.resolve_roll("BRN", 13, "standard", [1])
        self.assertEqual(result["natural"], 1)
        self.assertEqual(result["final_die"], 1)
        self.assertEqual(result["final_margin"], 12)
        self.assertEqual(result["fortune_status"], "forbidden")
        self.assertTrue(result["success"])

    def test_invalid_face_or_wrong_dice_count_is_rejected(self) -> None:
        for dice in ([0], [21], [2, 3]):
            with self.subTest(dice=dice):
                with self.assertRaises(lp.HarnessError):
                    lp.resolve_roll("CUN", 12, "standard", dice)
        with self.assertRaisesRegex(lp.HarnessError, "requires two dice"):
            lp.resolve_roll("CUN", 12, "advantage", [7])

    def test_fortune_recomputes_without_clamping_final_result(self) -> None:
        roll = lp.resolve_roll("CUN", 12, "standard", [15])
        result = lp.apply_fortune(roll, 3, 10)
        self.assertEqual(result["final_die"], 12)
        self.assertEqual(result["final_margin"], 0)
        self.assertTrue(result["success"])
        self.assertEqual(result["fortune_spent"], 3)

        deepened = lp.apply_fortune(
            lp.resolve_roll("BRN", 13, "standard", [2]),
            3,
            10,
        )
        self.assertEqual(deepened["final_die"], -1)
        self.assertEqual(deepened["final_margin"], 14)

    def test_locked_or_unaffordable_fortune_is_rejected(self) -> None:
        locked = lp.resolve_roll("BRN", 13, "standard", [20])
        with self.assertRaisesRegex(lp.HarnessError, "locked natural"):
            lp.apply_fortune(locked, 1, 10)
        ordinary = lp.resolve_roll("CUN", 12, "standard", [15])
        with self.assertRaisesRegex(lp.HarnessError, "only 2 Fortune"):
            lp.apply_fortune(ordinary, 3, 2)
```

Tie selection must deterministically keep the first physical die and record
`selected_index = 0`.

- [ ] **Step 2: Run the mechanics tests and verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_live_playtest.RollMechanicsTests -v
```

Expected: failures naming `resolve_roll` and `apply_fortune`.

- [ ] **Step 3: Implement die selection, locks, margin, and Fortune**

Use this exact calculation order:

```python
def resolve_roll(
    attribute: str,
    target: int,
    mode: str,
    dice: Sequence[int],
) -> JSONDict:
    expected_count = {"standard": 1, "advantage": 2, "disadvantage": 2}
    if mode not in expected_count:
        raise HarnessError(f"unknown roll mode {mode!r}")
    if len(dice) != expected_count[mode]:
        raise HarnessError(
            f"{mode} requires {expected_count[mode]} dice, received {len(dice)}"
        )
    if any(type(face) is not int or not 1 <= face <= 20 for face in dice):
        raise HarnessError(f"d20 faces must be integers from 1 through 20: {list(dice)}")

    if mode == "advantage":
        selected_die = min(dice)
    elif mode == "disadvantage":
        selected_die = max(dice)
    else:
        selected_die = dice[0]
    selected_index = list(dice).index(selected_die)
    natural = selected_die if selected_die in {1, 20} else None
    margin = target - selected_die

    return {
        "attribute": attribute,
        "target": target,
        "mode": mode,
        "dice": list(dice),
        "selected_die": selected_die,
        "selected_index": selected_index,
        "natural": natural,
        "provisional_margin": margin,
        "margin_is_resolution_inert": natural is not None,
        "fortune_status": "forbidden" if natural is not None else "pending",
        "fortune_spent": 0 if natural is not None else None,
        "final_die": selected_die if natural is not None else None,
        "final_margin": margin if natural is not None else None,
        "success": selected_die == 1 if natural is not None else None,
    }
```

`apply_fortune` must reject a non-integer or negative spend, any locked roll,
and any spend above available Fortune. It copies the roll and sets:

```python
result["fortune_status"] = "decided"
result["fortune_spent"] = spend
result["final_die"] = result["selected_die"] - spend
result["final_margin"] = result["target"] - result["final_die"]
result["success"] = result["final_die"] <= result["target"]
```

Do not change `selected_die`, `selected_index`, `natural`, or captured target.

- [ ] **Step 4: Add failing event-integration tests**

Using `HarnessTestCase`, assert:

- `record_roll` fails before `record_choice`;
- `record_roll(loaded, "CUN", "standard", [15], clock)` captures CUN 12 from
  current attributes;
- `record_roll(loaded, "Fortune", "standard", [8], clock)` captures current
  Fortune;
- ordinary `record_roll` leaves Fortune unchanged and stores
  `fortune_status="pending"`;
- `goto_passage` rejects an ordinary roll until `record_fortune` finalises it;
  a zero-spend decision counts as finalisation;
- `record_fortune(3)` changes Fortune from 10 to 7 and final die from 15 to 12;
- `record_fortune(0)` records a declined spend and finalises the roll;
- locked natural rolls are immediately final and any `record_fortune` call is
  rejected, while `goto_passage` remains available for the printed locked
  outcome;
- a second roll before transition is rejected; and
- invalid dice and invalid Fortune leave both files byte-for-byte unchanged.

- [ ] **Step 5: Implement target capture and event recording**

`record_roll` resolves the attribute name case-insensitively. Named attributes
capture their fixed current value. `Fortune` captures
`state["resources"]["Fortune"]["current"]`. Reject any other resource name,
unknown attribute, missing choice, or existing workflow roll.

Append `roll_recorded` with unchanged reader state and a copied workflow whose
`roll` is the pure result. Store `choice_event` in roll data.

`record_fortune` requires an ordinary pending roll. Call `apply_fortune`,
strictly validate the new Fortune resource value, copy state, deduct the
spend, store the final roll in workflow, and append `fortune_decided`. A zero
spend still creates the decision event. A locked roll is already final and
must not receive a Fortune event.

- [ ] **Step 6: Run all tests and commit mechanics**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
git add tools/live_playtest.py tests/test_live_playtest.py
git diff --cached --check
git commit -m "feat: resolve reported playtest rolls"
```

### Task 5: Apply sheet changes, lifecycle transitions, and compensating corrections

**Files:**

- Modify: `tools/live_playtest.py`
- Modify: `tests/test_live_playtest.py`

**Interfaces:**

- Consumes: explicit operator-entered authored changes and reasons, verified
  current state, an existing target event for corrections, and lifecycle
  commands.
- Produces: `change_resource`, `change_pressure`, `change_collection`,
  `correct_session`, `pause_session`, `resume_session`, and `finish_session`.
  Report generation consumes the exact event types and data created here.

- [ ] **Step 1: Add failing state-mutation tests**

Add tests that establish:

```python
class StateMutationTests(HarnessTestCase):
    def test_resource_pressure_possession_and_mark_changes(self) -> None:
        loaded = self.start()
        lp.change_resource(loaded, "Stamina", -1, "Printed injury", self.fixed_clock)
        lp.change_pressure(loaded, 7, "Printed disturbance", self.fixed_clock)
        lp.change_collection(
            loaded,
            "possessions",
            "add",
            "Guard's spear",
            "Taken at S04",
            clock=self.fixed_clock,
        )
        lp.change_collection(
            loaded,
            "story_marks",
            "add",
            "Read the strangling",
            "Discovery at S04",
            clock=self.fixed_clock,
        )
        self.assertEqual(loaded.state["resources"]["Stamina"]["current"], 5)
        self.assertEqual(loaded.state["pressure"]["current"], 5)
        self.assertIn("Guard's spear", loaded.state["possessions"])
        self.assertIn("Read the strangling", loaded.state["story_marks"])

    def test_consumption_is_preserved_as_an_event(self) -> None:
        loaded = self.start()
        lp.change_collection(
            loaded,
            "possessions",
            "add",
            "Guard's spear",
            "Taken",
            clock=self.fixed_clock,
        )
        lp.change_collection(
            loaded,
            "possessions",
            "consume",
            "Guard's spear",
            "Committed to the lion brace",
            clock=self.fixed_clock,
        )
        self.assertNotIn("Guard's spear", loaded.state["possessions"])
        self.assertEqual(loaded.events[-1]["data"]["action"], "consume")

    def test_invalid_change_leaves_files_unchanged(self) -> None:
        loaded = self.start()
        before_log = (loaded.directory / "events.jsonl").read_bytes()
        before_cache = (loaded.directory / "session.json").read_bytes()
        with self.assertRaisesRegex(lp.HarnessError, "outside 0/6"):
            lp.change_resource(
                loaded,
                "Stamina",
                -7,
                "Invalid",
                self.fixed_clock,
            )
        self.assertEqual((loaded.directory / "events.jsonl").read_bytes(), before_log)
        self.assertEqual((loaded.directory / "session.json").read_bytes(), before_cache)
```

Cover all of these cases explicitly:

- resource recovery within maximum succeeds;
- resource overflow and underflow fail;
- positive pressure overshoot saturates at 5 and records both requested and
  applied deltas;
- pressure underflow fails;
- duplicate add fails unless `allow_duplicate=True`;
- consume or remove absent possession/mark fails;
- add, consume, and remove preserve distinct event actions; and
- empty names or reasons fail.

- [ ] **Step 2: Run state tests and verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_live_playtest.StateMutationTests -v
```

Expected: failures naming the unimplemented change functions.

- [ ] **Step 3: Implement bounded sheet mutations**

`change_resource` must require active status, find the resource
case-insensitively, calculate `current + delta`, reject results outside
`0..maximum`, and append `resource_changed` with:

```json
{
  "name": "Stamina",
  "delta": -1,
  "before": 6,
  "after": 5,
  "reason": "Printed injury"
}
```

`change_pressure` uses the same structure but sets
`after = min(maximum, current + delta)` for non-negative outcomes. Store both
`requested_delta` and `applied_delta`. Reject a result below zero.

`change_collection` accepts only `possessions` or `story_marks` and only
`add`, `consume`, or `remove`. Match item names case-insensitively while
preserving the originally entered spelling. Add appends in order; duplicate
add requires `allow_duplicate=True`; consume and remove delete the first
matching item.
Append `possession_changed` or `story_mark_changed` with the action, name,
reason, and duplicate flag.

- [ ] **Step 4: Add failing correction and lifecycle tests**

Add cases proving:

```python
class LifecycleAndCorrectionTests(HarnessTestCase):
    def test_pause_resume_replays_equivalently(self) -> None:
        loaded = self.start()
        lp.pause_session(loaded, "Voice break", self.fixed_clock)
        self.assertEqual(loaded.state["status"], "paused")
        reloaded = lp.load_session(self.root / "sessions", "test-session")
        lp.resume_session(reloaded, self.fixed_clock)
        self.assertEqual(reloaded.state["status"], "active")
        self.assertEqual(lp.replay_events(reloaded.events)["state"], reloaded.state)

    def test_correction_preserves_original_and_compensates_state(self) -> None:
        loaded = self.start()
        original = lp.change_resource(
            loaded,
            "Stamina",
            -1,
            "Misheard loss",
            self.fixed_clock,
        )
        lp.correct_session(
            loaded,
            original["number"],
            "Player said no Stamina loss",
            "set-resource",
            name="Stamina",
            value=6,
            clock=self.fixed_clock,
        )
        self.assertEqual(loaded.events[-2]["type"], "resource_changed")
        self.assertEqual(loaded.events[-1]["type"], "correction")
        self.assertEqual(loaded.state["resources"]["Stamina"]["current"], 6)

    def test_finished_session_is_immutable(self) -> None:
        loaded = self.start()
        lp.finish_session(loaded, "E01 — theft abandoned", self.fixed_clock)
        before_log = (loaded.directory / "events.jsonl").read_bytes()
        with self.assertRaisesRegex(lp.HarnessError, "status is finished"):
            lp.record_note(loaded, "player", "One more thought", self.fixed_clock)
        self.assertEqual((loaded.directory / "events.jsonl").read_bytes(), before_log)
```

Also test:

- pausing except from active and resuming except from paused fail;
- resume rechecks reader hashes through normal verified loading;
- finish requires a non-empty outcome;
- `format_state` and report generation remain available after finish;
- correction target must exist;
- correction cannot run after finish;
- correction `annotate` leaves state unchanged;
- `set-resource`, `set-pressure`, `add-possession`, `remove-possession`,
  `add-mark`, `remove-mark`, `set-passage`, and `clear-workflow` each validate
  their required argument and resulting state; and
- `set-passage` requires a defined destination but deliberately does not
  require that destination to appear in the current passage because its
  purpose is to compensate an operator error.

- [ ] **Step 5: Implement lifecycle changes**

`pause_session` copies state, sets `status="paused"`, and appends
`session_paused` with the required reason. `resume_session` accepts only a
freshly verified paused `LoadedSession`, sets `status="active"`, and appends
`session_resumed`. `finish_session` accepts only active status, requires a
non-empty outcome, sets `status="finished"`, and appends `session_finished`.

All other event-recording operations must call `_require_active`. Read-only
`format_state`, `load_session`, `recover_cache`, `render_report`, and
`write_report` remain available for paused or finished sessions.

- [ ] **Step 6: Implement compensating correction operations**

`correct_session` requires an active session, a target event number present in
the current log, and a non-empty reason. Accept exactly one of these operation
contracts:

| Operation | Required values | Result |
| --- | --- | --- |
| `annotate` | `replacement_text` | State and workflow unchanged; records corrected wording |
| `set-resource` | resource `name`, integer `value` | Sets current value within 0..maximum |
| `set-pressure` | integer `value` | Sets pressure within 0..maximum |
| `add-possession` | string `name` | Adds one absent possession |
| `remove-possession` | string `name` | Removes one present possession |
| `add-mark` | string `name` | Adds one absent story mark |
| `remove-mark` | string `name` | Removes one present story mark |
| `set-passage` | passage ID in `value` | Sets a defined current passage |
| `clear-workflow` | no name, value, or replacement | Resets choice and roll |

Append one `correction` event containing target event, reason, operation,
arguments, and a compact `compensation` description. Do not alter the target
event or any earlier line.

- [ ] **Step 7: Run all tests and commit state/lifecycle support**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
git add tools/live_playtest.py tests/test_live_playtest.py
git diff --cached --check
git commit -m "feat: track live playtest state"
```

### Task 6: Derive a deterministic, readable playtest report

**Files:**

- Modify: `tools/live_playtest.py`
- Modify: `tests/test_live_playtest.py`

**Interfaces:**

- Consumes: immutable session metadata plus the complete ordered event log.
- Produces: pure `render_report` and atomic `write_report`. Report generation
  never appends an event or changes the session cache.

- [ ] **Step 1: Add failing report tests**

Build a compact eventful session in a test:

1. start and show S01;
2. record a player note and rules question;
3. look up Fortune;
4. choose, roll 15 against CUN 12, spend 3 Fortune, and go to S02;
5. add then consume `Guard's spear`;
6. add an operator note;
7. pause and resume;
8. append one annotation correction; and
9. finish with a named outcome.

Then assert:

```python
class ReportTests(HarnessTestCase):
    def test_report_is_deterministic_complete_and_derived(self) -> None:
        loaded = self.build_eventful_session()
        event_bytes = (loaded.directory / "events.jsonl").read_bytes()
        cache_bytes = (loaded.directory / "session.json").read_bytes()

        first = lp.render_report(loaded.document, loaded.events)
        second = lp.render_report(loaded.document, loaded.events)
        self.assertEqual(first, second)
        for heading in (
            "# Live Playtest Report",
            "## Session",
            "## Route",
            "## Player narration",
            "## Operator observations",
            "## Choices and tests",
            "## State history",
            "## Rules activity",
            "## Corrections and pauses",
            "## Timing",
            "## Final state",
            "## Limitations",
        ):
            self.assertIn(heading, first)
        self.assertIn("raw audio was not retained", first)
        self.assertIn("not a blind or controlled experiment", first)
        self.assertIn("Guard's spear", first)
        self.assertIn("consum", first.casefold())

        report_path = lp.write_report(loaded)
        first_bytes = report_path.read_bytes()
        report_path = lp.write_report(loaded)
        self.assertEqual(report_path.read_bytes(), first_bytes)
        self.assertEqual((loaded.directory / "events.jsonl").read_bytes(), event_bytes)
        self.assertEqual((loaded.directory / "session.json").read_bytes(), cache_bytes)
```

- [ ] **Step 2: Run the report tests and verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_live_playtest.ReportTests -v
```

Expected: failures naming `render_report` and `write_report`.

- [ ] **Step 3: Implement deterministic report sections**

`render_report` must use only stored metadata and events. It must not read
current story prose, current wall-clock time, or `report.md`. Produce these
sections in order:

1. `# Live Playtest Report`
2. `## Session` — ID, purpose, optional hypothesis, physical/neutral modes,
   created time, reader paths and hashes.
3. `## Route` — ordered `passage_shown` and `passage_transition` rows with
   event number, timestamp, from, and to.
4. `## Player narration` — verbatim `player_note` entries.
5. `## Operator observations` — verbatim `operator_note` entries, including
   observed ambiguity. Do not turn these observations into general findings.
6. `## Choices and tests` — choice text and method; every raw die, selected
   index/face, target, arithmetic provisional margin, natural status, Fortune
   decision, final die/margin, and success flag.
7. `## State history` — events whose before and after reader states differ,
   showing the event's printed reason and compact before/after sheet values.
8. `## Rules activity` — rules questions and named lookups.
9. `## Corrections and pauses` — correction target/reason/compensation plus
   pause/resume events.
10. `## Timing` — ordered event timestamps and the interval from each
   `passage_shown` to the next `choice_committed` when both timestamps parse;
   label these interaction intervals rather than hesitation times.
11. `## Final state` — `format_state` output plus the recorded finish outcome,
    or `Session unfinished` when no finish event exists.
12. `## Limitations` — state that raw audio was not retained, voice-derived
    text is stored as received, Codex was not blind to unread material, this
    was not a blind or controlled experiment, timing includes network/tool/
    transcription delay, and one player cannot establish general behaviour.

Use Markdown tables only when a section has rows; otherwise print `None
recorded.` Escape pipe characters and replace embedded newlines with `<br>` in
table cells. Do not polish, paraphrase, or summarise player notes.

`write_report` calls `render_report` and atomically writes UTF-8 text with LF
endings to `report.md` using:

```python
def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
```

Repeated writes from unchanged inputs must be byte-identical.

- [ ] **Step 4: Run all tests and commit reporting**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
git add tools/live_playtest.py tests/test_live_playtest.py
git diff --cached --check
git commit -m "feat: render live playtest reports"
```

### Task 7: Bind the exact operator CLI

**Files:**

- Modify: `tools/live_playtest.py`
- Modify: `tests/test_live_playtest.py`

**Interfaces:**

- Consumes: every core function from Tasks 1-6 and the exact CLI contract
  table above.
- Produces: `build_parser` and `main`; no command performs natural-language
  choice inference or authored-fiction adjudication.

- [ ] **Step 1: Add failing parser and command tests**

Use `contextlib.redirect_stdout`, `contextlib.redirect_stderr`, and
`io.StringIO` to test `main` without spawning a second interpreter. Cover:

- top-level `--help` contains all 16 command names;
- `start` with the exact Tower-style arguments creates a session;
- `show` prints S01 but not S02;
- `state` prints the complete sheet;
- `note`, `lookup`, `choose`, `roll`, `fortune`, all four `apply` families,
  `goto`, `correct`, `pause`, `resume`, `finish`, and `report` dispatch to the
  corresponding core operation;
- malformed `--attribute`, `--resource`, and `--pressure` values exit 2;
- wrong physical dice count exits 2 without mutation;
- an unknown session exits 2 with one `error:` line and no traceback; and
- no command has an RNG, prose-rewrite, AI, simulation, or passage-list option.

An exact start invocation in the test is:

```python
arguments = [
    "--sessions-dir", str(self.root / "sessions"),
    "start", "cli-session",
    "--story", str(self.story),
    "--rules", str(self.rules),
    "--sheet", str(self.sheet),
    "--purpose", "Natural calibration playthrough",
    "--start-passage", "S01",
    "--attribute", "BRN=13",
    "--attribute", "AGI=12",
    "--attribute", "CUN=12",
    "--attribute", "WIL=12",
    "--resource", "Fortune=10/10",
    "--resource", "Stamina=6/6",
    "--pressure", "Exposure=0/5",
    "--possession", "Sword",
]
self.assertEqual(lp.main(arguments), 0)
```

- [ ] **Step 2: Run CLI tests and verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_live_playtest.CliTests -v
```

Expected: failures naming `build_parser` or `main`.

- [ ] **Step 3: Build every parser with the locked option spelling**

Use one top-level `argparse.ArgumentParser`, global
`--sessions-dir=Path(".playtest/sessions")`, required command subparsers, and
nested required subparsers for `apply`. Use `action="append"` for attributes,
resources, possessions, marks, and dice.

The `correct` parser must require `--target-event` and `--reason`, then one
mutually exclusive required option:

```text
--annotate TEXT
--set-resource NAME=CURRENT
--set-pressure CURRENT
--add-possession NAME
--remove-possession NAME
--add-mark NAME
--remove-mark NAME
--set-passage PASSAGE_ID
--clear-workflow
```

Map these options to the correction operation names defined in Task 5. Reject
extra correction values in `correct_session`, not after an event append.

- [ ] **Step 4: Implement explicit dispatch and stable output**

`main` must:

1. parse arguments;
2. for `start`, reject duplicate attribute/resource names, build initial
   state, and call `start_session`;
3. for every other command, call `load_session` before dispatch, except
   `recover-cache`, which calls its dedicated function;
4. print Markdown for `show` and `lookup`;
5. print `format_state` for `state`;
6. print the event plus current state as deterministic indented UTF-8 JSON for
   event-recording commands;
7. print the path for `report` and recovered state for `recover-cache`;
8. return 0 on success; and
9. catch only `HarnessError`, print `error: <message>` to standard error, and
   return 2.

Let unexpected programming exceptions retain their traceback during
development; do not disguise them as user input failures.

End the module with:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run CLI help and the full suite**

Run:

```bash
python3 tools/live_playtest.py --help
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

Expected: help lists the locked commands; all tests pass.

- [ ] **Step 6: Commit the operator interface**

Run:

```bash
git add tools/live_playtest.py tests/test_live_playtest.py
git diff --cached --check
git commit -m "feat: add live playtest operator CLI"
```

### Task 8: Prove the audited Tower route and document live operation

**Files:**

- Modify: `tests/test_live_playtest.py`
- Create: `docs/playtesting/live-playtest.md`
- Read, unchanged:
  `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`
- Read, unchanged:
  `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`
- Read, unchanged:
  `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`

**Interfaces:**

- Consumes: all completed core and CLI operations plus the real reader files.
- Produces: one exact integration replay ending at S14 with
  Fortune/Stamina/Exposure `7/6/0`, Sword retained, spear consumed, and no
  marks; plus the operator protocol used for the natural live calibration.

- [ ] **Step 1: Add the failing real-Tower smoke replay**

Create `TowerSmokeReplayTests` with repository paths derived from
`Path(__file__).resolve().parents[1]`. Use a temporary sessions directory, the
real three reader files, and this exact operation sequence:

```python
loaded = lp.start_session(
    self.root / "sessions",
    "tower-smoke",
    tower / "slice-01.md",
    tower / "quick-rules.md",
    tower / "adventure-sheet.md",
    "Deterministic audited route replay",
    "The observer reproduces the existing 7/6/0 route",
    lp.build_initial_state(
        {"BRN": 13, "AGI": 12, "CUN": 12, "WIL": 12},
        {"Fortune": (10, 10), "Stamina": (6, 6)},
        ("Exposure", 0, 5),
        ["Sword"],
        [],
        "S01",
    ),
    self.fixed_clock,
)

def choose_and_go(text: str, destination: str) -> None:
    lp.show_current_passage(loaded, self.fixed_clock)
    lp.record_choice(
        loaded,
        text,
        None,
        destination,
        self.fixed_clock,
    )
    lp.goto_passage(loaded, destination, self.fixed_clock)

choose_and_go("Climb now", "S03")
choose_and_go("Examine the corpse", "S04")
lp.show_current_passage(loaded, self.fixed_clock)
lp.record_choice(loaded, "Take the guard's spear", None, "S05", self.fixed_clock)
lp.change_collection(
    loaded,
    "possessions",
    "add",
    "Guard's spear",
    "Printed S04 discovery",
    clock=self.fixed_clock,
)
lp.goto_passage(loaded, "S05", self.fixed_clock)

lp.show_current_passage(loaded, self.fixed_clock)
lp.record_choice(loaded, "Stalk the stranger", "Stalk", "S06", self.fixed_clock)
lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)
lp.record_fortune(loaded, 3, self.fixed_clock)
lp.goto_passage(loaded, "S06", self.fixed_clock)

choose_and_go("Hear the alliance", "S07")
choose_and_go("Accept Taurus", "S08")
choose_and_go("Cross the inner wall", "S09")
choose_and_go("Trust Taurus", "S10")
choose_and_go("Advance after the cloud", "S11")

lp.show_current_passage(loaded, self.fixed_clock)
lp.record_choice(
    loaded,
    "Brace the guard's spear",
    "Brace the guard's spear",
    "S12",
    self.fixed_clock,
)
lp.change_collection(
    loaded,
    "possessions",
    "consume",
    "Guard's spear",
    "Committed before the S11 roll",
    clock=self.fixed_clock,
)
lp.record_roll(loaded, "BRN", "advantage", [6, 20], self.fixed_clock)
lp.record_fortune(loaded, 0, self.fixed_clock)
lp.goto_passage(loaded, "S12", self.fixed_clock)
choose_and_go("Give Taurus room to finish the cast", "S14")
lp.show_current_passage(loaded, self.fixed_clock)
lp.finish_session(loaded, "S14 — slice complete", self.fixed_clock)
lp.write_report(loaded)

self.assertEqual(
    loaded.state["resources"],
    {
        "Fortune": {"current": 7, "maximum": 10},
        "Stamina": {"current": 6, "maximum": 6},
    },
)
self.assertEqual(
    loaded.state["pressure"],
    {"name": "Exposure", "current": 0, "maximum": 5},
)
self.assertEqual(loaded.state["possessions"], ["Sword"])
self.assertEqual(loaded.state["story_marks"], [])
self.assertEqual(loaded.state["current_passage"], "S14")
self.assertEqual(loaded.state["status"], "finished")
self.assertEqual(lp.replay_events(loaded.events)["state"], loaded.state)
report = (loaded.directory / "report.md").read_text(encoding="utf-8")
self.assertIn("15", report)
self.assertIn("-3", report)
self.assertIn("Fortune", report)
self.assertIn("6, 20", report)
self.assertIn("Guard's spear", report)
self.assertIn("S14", report)
```

This integration test intentionally does not claim slice coverage for
Disadvantage, WIL, Fortune tests, recovery, margin-specific branches, or
Stamina zero. Those remain covered only by focused engine tests because the
current slice contains no such route.

- [ ] **Step 2: Run the smoke replay and repair only real integration defects**

Run:

```bash
python3 -m unittest \
  tests.test_live_playtest.TowerSmokeReplayTests -v
```

Expected: one passing smoke replay. If a transition reference check fails,
compare it with the exact current passage rather than weakening destination
validation globally.

- [ ] **Step 3: Write the operator and evidence protocol**

Create `docs/playtesting/live-playtest.md` with these headings:

```markdown
# Live Playtest Observer

## Purpose
## What the tool does
## What the tool deliberately does not do
## Requirements
## Start a Tower session
## Live operating sequence
## Command reference
## Neutral-observer protocol
## Voice-derived notes
## Corrections
## Pause and resume
## Cache recovery
## Finish and report
## Evidence and privacy
## Calibration checklist
## Known limitations
```

Under `## Start a Tower session`, include this runnable command from repository
root:

```bash
python3 tools/live_playtest.py start tower-calibration-01 \
  --story stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md \
  --rules stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md \
  --sheet stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md \
  --purpose "Natural calibration playthrough" \
  --start-passage S01 \
  --attribute BRN=13 \
  --attribute AGI=12 \
  --attribute CUN=12 \
  --attribute WIL=12 \
  --resource Fortune=10/10 \
  --resource Stamina=6/6 \
  --pressure Exposure=0/5 \
  --possession Sword
```

Document the operational sequence exactly:

```text
show -> free narration and rules activity -> choose -> optional pre-roll apply
-> physical roll -> ordinary Fortune decision or locked natural
-> authored apply commands -> goto -> complete state -> next show
```

State that Codex may answer reader-facing procedure questions, must not
recommend or rank choices, enters only Barry's reported faces, applies only
printed results, and asks a neutral clarification only when an utterance maps
to multiple printed options.

State that no passage or rule edits occur during play; raw local material is
ignored; a future curated summary needs Barry's approval; repeat sessions need
a written purpose or hypothesis; and `recover-cache` repairs only a stale
derived cache when the event chain and reader hashes are intact.

- [ ] **Step 4: Verify the Python 3.10 floor and full repository gate**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
uv run --no-project --python 3.10 \
  python -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/live_playtest.py --help
git diff --check

test "$(git ls-files '.playtest/**' | wc -l | tr -d ' ')" -eq 0
git check-ignore -q .playtest/sessions/example/events.jsonl

git diff --exit-code -- \
  stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md
```

Expected:

- all tests pass under the installed Python and a `uv`-managed Python 3.10;
- CLI help succeeds;
- no whitespace errors;
- `.playtest/` is ignored and contains no tracked files; and
- all three reader-facing files are byte-for-byte unchanged.

- [ ] **Step 5: Perform one focused code and evidence-boundary review**

Inspect:

```bash
rg -n \
  'openai|anthropic|requests|httpx|urllib|socket|random|secrets|subprocess' \
  tools tests docs/playtesting/live-playtest.md

rg -n \
  'player_note|rules_question|choice_committed|roll_recorded|fortune_decided|correction' \
  tools/live_playtest.py tests/test_live_playtest.py

git diff --stat
git status --short --branch
```

Expected:

- no network, model, RNG, or subprocess integration in the runtime;
- every required evidence event has implementation and test coverage; and
- tracked changes are limited to the tool, tests, protocol, and `.gitignore`.

If this review finds a material defect, repair it and rerun the full gate once.
If it finds none, record that outcome and stop. Do not begin another pass when
further changes would only polish wording or formatting.

- [ ] **Step 6: Commit the verified implementation**

Run:

```bash
git add \
  .gitignore \
  tools/live_playtest.py \
  tests/test_live_playtest.py \
  docs/playtesting/live-playtest.md
git diff --cached --check
git commit -m "test: verify Tower playtest observer"
git status --short --branch
```

Expected: a clean implementation branch containing the incremental commits.
Do not push or merge until the implementation review required by the selected
execution workflow passes.

### Task 9: Conduct the natural live calibration session

**Files:**

- Create locally, ignored:
  `.playtest/sessions/tower-calibration-01/session.json`
- Create locally, ignored:
  `.playtest/sessions/tower-calibration-01/events.jsonl`
- Create locally, ignored:
  `.playtest/sessions/tower-calibration-01/report.md`
- Do not modify tracked passages, rules, sheet, audit, design, or protocol.

**Interfaces:**

- Consumes: the reviewed implementation, Barry as player, Codex as neutral
  operator, physical d20s, voice-transcribed free narration, and the current
  `slice-01.md`.
- Produces: one local report and a conversational debrief. It does not produce
  a tracked playtest summary or an automatic rules revision.

- [ ] **Step 1: Verify the live gate immediately before play**

Run:

```bash
git status --short --branch
python3 -m unittest discover -s tests -p 'test_*.py' -v
test ! -e .playtest/sessions/tower-calibration-01
```

Expected: clean reviewed implementation, all tests passing, and no reused
calibration ID. If the ID exists, choose a new sequential ID rather than
deleting prior evidence.

- [ ] **Step 2: Start the session with no target route**

Run the documented start command with purpose
`Natural calibration playthrough` and no `--hypothesis`. Then run:

```bash
python3 tools/live_playtest.py show tower-calibration-01
```

Codex presents only S01 and invites Barry to react or choose. Do not mention
unread options, route quality, balance expectations, or the audited smoke
route.

- [ ] **Step 3: Operate the session neutrally to a terminal or S14**

For every reached passage:

1. record Barry's free narration with `note --kind player`;
2. record reader-facing questions with `note --kind rules-question`;
3. use `lookup` only for the named relevant reader-rules section;
4. use `choose` only after Barry commits;
5. ask Barry to roll the printed number of physical d20s;
6. enter each reported face with one `--die`;
7. on an ordinary selected die, ask for the Fortune spend without suggesting
   an amount and record zero when declined;
8. on a selected natural 1 or 20, state that it is locked and do not run
   `fortune`;
9. enter every printed resource, pressure, possession, or mark change with its
   passage-grounded reason;
10. run `goto` only after all printed changes are recorded;
11. show the complete sheet and then only the newly reached passage; and
12. use `correct` only for a genuine transcription or operator mistake.

Pause rather than compressing or inventing play if Barry needs to stop.

- [ ] **Step 4: Finish, generate the local report, and verify evidence**

At E01, E02, E03, or S14, run:

```bash
python3 tools/live_playtest.py finish tower-calibration-01 \
  --outcome "REACHED PASSAGE — printed outcome"
python3 tools/live_playtest.py report tower-calibration-01
python3 tools/live_playtest.py state tower-calibration-01
git status --short --branch
git check-ignore -q \
  .playtest/sessions/tower-calibration-01/events.jsonl
```

Replace the outcome text with the actual reached passage and outcome. Confirm
that the report contains route, narration, choices, raw/selected dice,
margins, Fortune, state history, rules activity, corrections/pauses, timing,
final state, and limitations. Git must remain clean because all raw evidence
is ignored.

- [ ] **Step 5: Debrief and stop at the approval boundary**

Discuss with Barry:

- where choices felt meaningful or cosmetic;
- whether stakes and consequences were clear before rolling;
- whether physical-dice reporting and Fortune decisions stayed fluid;
- whether complete-state displays helped or interrupted play;
- whether the authored tactical exchange felt richer than a repeated combat
  loop;
- where Codex needed clarification or risked steering;
- what the report captured well or missed; and
- whether another session has a specific new hypothesis worth testing.

Do not commit a summary, change mechanics or prose, run a second session, add
features, select a permanent passage schema, or design an AI facilitator
without Barry's next explicit approval.

## Completion gate

The increment is complete only when:

1. the current branch contains the approved design and all implementation
   commits;
2. the runtime uses only Python 3.10+ standard-library facilities;
3. all tests pass under installed Python and `uv`-managed Python 3.10;
4. current-passage display and named rules lookup reveal no adjacent prose;
5. invalid operations are proven byte-for-byte non-mutating;
6. replay always reproduces cache, explicit recovery repairs only stale cache,
   and hash drift blocks mutation/resume;
7. standard, Advantage, Disadvantage, selected naturals, arithmetic margins,
   and post-roll Fortune are covered;
8. Fortune, Stamina, Exposure, possessions, and story marks obey the approved
   bounds and event semantics;
9. correction retains original events, pause/resume is equivalent, finished
   sessions are immutable, and report regeneration is deterministic;
10. the real Tower `7/6/0` spear-consumed route passes in a temporary session;
11. no `.playtest/` evidence is tracked and the three reader files remain
    unchanged;
12. the implementation receives the review required by the selected execution
    workflow before merge or push;
13. one natural live calibration session is completed with Barry, physical
    dice, free think-aloud narration, and Codex neutral;
14. the local report is verified and the conversational debrief is completed;
    and
15. work stops for approval before any tracked playtest conclusion, rules or
    passage revision, targeted repeat, permanent schema, or AI-guided layer.
