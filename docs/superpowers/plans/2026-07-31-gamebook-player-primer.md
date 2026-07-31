# Gamebook Player Primer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the approved player-primer design into self-contained, publishable Tower front matter that teaches a new reader everything needed before S01, with a modular Adventure Sheet and a primer-first live-calibration protocol.

**Architecture:** Keep one authoritative Tower rules document. Its four unique H2 sections form the facilitator lookup boundary; H3 subsections carry the detailed teaching. Keep the writable sheet separate, change only the story preamble before S01, and verify the reader-facing contract with standard-library tests. The thin observer harness remains mechanically unchanged and merely presents the new sections in order.

**Tech Stack:** Markdown, Python 3.10+ standard-library `unittest`, the existing `tools/live_playtest.py` APIs, Git.

## Global Constraints

- Implement the approved specification in `docs/superpowers/specs/2026-07-31-gamebook-player-primer-design.md`.
- Work from approved base commit `c27a3f616395a3305b13a53ba24efc4dc71021a8` or its reviewed descendant.
- Keep `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md` as the single authoritative Tower primer. Do not introduce includes, templates, generated copies, or a generic rules source.
- Use exactly these unique H2 headings, in this order, because the observer indexes H2 blocks for `lookup`: `Before You Begin`, `Part I: How to Play`, `Part II: Rules for This Adventure`, `Rules at a Glance`. Use H3 or lower for every internal subsection.
- Keep all reader-facing mechanics self-contained. Knowledge of the full *Sinew & Steel* rules must never be required.
- Keep the instructional prose original. Borrow the established function of self-contained gamebook rules and a writable record sheet, but do not copy proprietary wording, examples, tables, or distinctive layouts.
- Retain the four capability meanings and the selected Tower labels consistently: Brawn (`BRN`) 13, Agility (`AGI`) 12, Cunning (`CUN`) 12, Will (`WIL`) 12.
- Keep the approved fixed starting state: Fortune 10/10, Stamina 6/6, Exposure 0/5, Sword, and no starting story marks.
- Keep Exposure inside the Tower-specific module. It is the title's only primary story track and must be fully explained before S01.
- Do not modify `tools/live_playtest.py`, dependency files, build tooling, publishing infrastructure, or `README.md`.
- Do not change numbered passage prose, choices, destinations, identifiers, or edges. The SHA-256 of `slice-01.md` from the first `## S01` byte through EOF must remain `2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496`.
- Keep local session material under `.playtest/` ignored and untracked. Preserve `tower-calibration-01`; do not start `tower-calibration-02` during implementation.
- Aim for 1,800–2,000 reader-facing words across `quick-rules.md` and `adventure-sheet.md`, excluding Markdown link destinations, HTML comments, box glyphs, and writable blank lines.
- Use test-driven development for changed behaviour: add each focused contract test, observe the intended failure, make the smallest complete editorial change, then run the focused and full suites. A narrowly scoped characterization test may begin green when it proves compatibility with deliberately unchanged harness code.
- Commit after each completed task. Do not push implementation commits until the reviewed implementation is accepted for integration.
- Treat the tracked result as ready for acceptance calibration, not as proof of reader comprehension. Starting the live `tower-calibration-02` session is a separate, user-gated follow-up.

---

## Task 1: Teach the Reusable Core

**Files:**

- Create: `tests/test_player_primer.py`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`
- Test: `tests/test_player_primer.py`

### Step 1: Add the reader-material test helpers

- [ ] Create `tests/test_player_primer.py` with this standard-library foundation:

```python
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOWER = ROOT / "stories/public_domain/howard/tower_of_the_elephant/playtest"
RULES = TOWER / "quick-rules.md"
SHEET = TOWER / "adventure-sheet.md"
STORY = TOWER / "slice-01.md"
PROTOCOL = ROOT / "docs/playtesting/live-playtest.md"
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*")
H2_RE = re.compile(r"^## (?P<title>.+)$", re.MULTILINE)
S01_HEADING = "## S01 — The Outer Wall"
NUMBERED_BODY_SHA256 = (
    "2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def h2_headings(text: str) -> list[str]:
    return [match.group("title") for match in H2_RE.finditer(text)]


def h2_section(text: str, heading: str) -> str:
    matches = list(H2_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group("title") != heading:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[match.start():end].rstrip() + "\n"
    raise AssertionError(f"missing H2 section: {heading}")


def reader_word_count(*texts: str) -> int:
    visible = "\n".join(texts)
    visible = re.sub(r"<!--.*?-->", " ", visible, flags=re.DOTALL)
    visible = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", visible)
    visible = re.sub(r"https?://\S+", " ", visible)
    return len(WORD_RE.findall(visible))


def normalised_prose(text: str) -> str:
    return " ".join(text.split())


class PlayerPrimerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = read_text(RULES)
        cls.sheet = read_text(SHEET)
        cls.story = read_text(STORY)
        cls.protocol = read_text(PROTOCOL)

    def assert_occurs_in_order(self, text: str, *markers: str) -> None:
        position = -1
        for marker in markers:
            next_position = text.find(marker, position + 1)
            self.assertNotEqual(next_position, -1, f"missing marker: {marker}")
            self.assertGreater(next_position, position, f"out-of-order marker: {marker}")
            position = next_position

    def assert_matches_concepts(self, text: str, *patterns: str) -> None:
        prose = normalised_prose(text)
        for pattern in patterns:
            self.assertRegex(prose, re.compile(pattern, re.IGNORECASE))
```

### Step 2: Write the failing core-contract tests

- [ ] Add these tests to `PlayerPrimerContractTests`. Keep exact assertions for approved facts and arithmetic; use semantic assertions for prose so later copy-editing remains possible.

```python
    def test_core_primer_sections_are_unique_and_ordered(self) -> None:
        self.assertEqual(
            h2_headings(self.rules),
            [
                "Before You Begin",
                "Part I: How to Play",
                "Part II: Rules for This Adventure",
            ],
        )

    def test_before_you_begin_states_the_self_contained_contract(self) -> None:
        before = h2_section(self.rules, "Before You Begin")
        for phrase in [
            "Adventure Sheet",
            "*Sinew & Steel*",
            "Barry W. Brook",
            "You need no knowledge of that system",
            "everything required to play appears here",
        ]:
            self.assertIn(phrase, before)
        self.assert_matches_concepts(
            before,
            r"pen or pencil",
            r"one (?:twenty-sided die|d20)",
            r"(?:optional second d20|second d20.*optional)",
            r"(?:no character creation|do not create.*character)",
        )

    def test_part_one_teaches_the_routine_play_loop_in_use_order(self) -> None:
        core = h2_section(self.rules, "Part I: How to Play")
        self.assert_occurs_in_order(
            core,
            "### Your Adventure Sheet",
            "### Reading the Adventure",
            "### When the Story Calls for a Test",
            "### Advantage and Disadvantage",
            "### Natural Results",
            "### Margin and Fortune",
            "### A Worked Conan Example",
            "### Stamina, Possessions, and Story Marks",
            "### Tactical Exchanges and Endings",
        )
        self.assert_matches_concepts(
            core,
            r"equal to or (?:below|lower than)",
            r"Advantage.*(?:lower|lowest)",
            r"Disadvantage.*(?:higher|highest)",
            r"target\s*-\s*selected die",
            r"margin.*(?:no|without).*effect.*unless.*passage",
            r"(?:escape|evasion|withdraw).*only.*passage",
            r"0 Stamina",
            r"(?:explicit|printed).*(?:ending|ends|terminal)",
        )

    def test_part_one_keeps_title_specific_state_out_of_the_core(self) -> None:
        core = h2_section(self.rules, "Part I: How to Play")
        self.assertNotIn("BRN 13 | AGI 12", core)
        self.assertNotIn("Exposure", core)

    def test_worked_conan_example_matches_the_approved_arithmetic(self) -> None:
        core = h2_section(self.rules, "Part I: How to Play")
        self.assert_occurs_in_order(
            core,
            "target of 12",
            "selected die is 15",
            "12 - 15 = -3",
            "spend 3 Fortune",
            "final die is 12",
            "final margin is 0",
            "Fortune falls from 10 to 7",
            "Conan succeeds",
        )
        self.assertIn("do not mark", core.casefold())
        self.assertIn("selected natural 20", core)
        self.assertIn("cannot be changed with Fortune", core)

```

### Step 3: Run the focused tests and confirm RED

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
```

Expected: the new tests fail because the current reference begins with `What you need`, lacks the approved H2 boundary, and does not contain the full worked tutorial. Any import or helper error is a test defect and must be fixed before editing the reader files.

### Step 4: Rewrite Before You Begin and Part I

- [ ] Replace the current reference-style opening with the following exact top-level and subsection structure:

```markdown
# *The Tower of the Elephant* Player's Rules

## Before You Begin

## Part I: How to Play

### Your Adventure Sheet

### Reading the Adventure

### When the Story Calls for a Test

### Advantage and Disadvantage

### Natural Results

### Margin and Fortune

### A Worked Conan Example

### Stamina, Possessions, and Story Marks

### Tactical Exchanges and Endings

## Part II: Rules for This Adventure
```

- [ ] Write 100–150 words under `Before You Begin`. Include the required equipment and fixed-protagonist contract. Use this approved attribution verbatim:

```text
These gamebook rules are adapted from *Sinew & Steel*, a d20 tabletop role-playing game by Barry W. Brook. You need no knowledge of that system; everything required to play appears here.
```

- [ ] Write 850–950 words under Part I using the approved purpose → procedure → example → record teaching pattern. Explain how to read the fixed profile supplied by a title, but keep Conan's exact values, Tower labels, and Exposure in Part II. Part I must teach:

  - attributes as the four broad capabilities printed on a supplied protagonist profile, without fixing their title-facing names or values in the reusable core;
  - passage choices, printed conditions, and immediate state updates;
  - d20 roll-under tests with an ordinary selected result succeeding at or below the captured target;
  - Advantage as two d20s keeping the lower, and Disadvantage as two d20s keeping the higher;
  - selected natural 1 and 20 as locked results before Fortune;
  - margin as `target - selected die`, with no independent effect unless the passage explicitly reads it;
  - Fortune spending after an ordinary selected die, and Fortune as the captured target when a passage calls for a Fortune test;
  - authored Stamina loss and the passage's explicit instruction at 0 Stamina;
  - possessions and semantic story marks;
  - authored tactical exchanges rather than repeated enemy-stat rounds;
  - escape, evasion, or withdrawal only when printed; and
  - explicit death, withdrawal, crisis, and slice-complete endings.

- [ ] Give the worked example Tower atmosphere without reproducing or foreshadowing a numbered passage. Tell the reader not to mark the real sheet. State the exact arithmetic and resource transition required by the test, then add a one-sentence natural-20 contrast.

- [ ] Move the existing Tower-specific material below `## Part II: Rules for This Adventure` and demote its internal headings to H3 as an interim module. Do not add any additional H2 headings. Task 2 will edit and reorganise that module.

### Step 5: Run focused and regression tests

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all Task 1 tests pass and the existing suite remains `OK`.

### Step 6: Commit the reusable core

- [ ] Inspect the diff for accidental Tower spoilers or extra H2 headings, then commit:

```bash
git add tests/test_player_primer.py \
  stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
git commit -m "docs: teach the reusable gamebook core"
```

---

## Task 2: Complete the Tower Module and Rules at a Glance

**Files:**

- Modify: `tests/test_player_primer.py`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`
- Test: `tests/test_player_primer.py`

### Step 1: Tighten the four-section contract

- [ ] Change `test_core_primer_sections_are_unique_and_ordered` to require the final exact list:

```python
        self.assertEqual(
            h2_headings(self.rules),
            [
                "Before You Begin",
                "Part I: How to Play",
                "Part II: Rules for This Adventure",
                "Rules at a Glance",
            ],
        )
```

### Step 2: Add failing Tower-module tests

- [ ] Add:

```python
    def test_tower_module_defines_the_fixed_profile_and_labels(self) -> None:
        tower = h2_section(self.rules, "Part II: Rules for This Adventure")
        profile = "BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6"
        self.assertIn(profile, tower)
        for name, abbreviation in [
            ("Brawn", "BRN"),
            ("Agility", "AGI"),
            ("Cunning", "CUN"),
            ("Will", "WIL"),
        ]:
            self.assert_matches_concepts(tower, rf"{name}.*\({abbreviation}\)")
        self.assertIn("Sword", tower)

    def test_tower_module_defines_the_complete_exposure_scale(self) -> None:
        tower = h2_section(self.rules, "Part II: Rules for This Adventure")
        self.assert_matches_concepts(
            tower,
            r"Exposure.*start.*0",
            r"Exposure.*cap.*5",
            r"another patrol interval",
            r"call.*loud",
            r"failed standoff",
            r"natural 20",
            r"lion tactic",
            r"no ordinary event.*lower.*Exposure",
        )
        for row in [
            r"(?mi)^\|\s*0–2\s*\|.*unconfirmed.*all.*choices.*\|$",
            r"(?mi)^\|\s*3\s*\|.*uneasy.*lingering.*close.*\|$",
            r"(?mi)^\|\s*4\s*\|.*search.*(?:advance|withdraw).*\|$",
            r"(?mi)^\|\s*5\s*\|.*discovered.*E02.*\|$",
        ]:
            self.assertRegex(tower, row)
        self.assert_matches_concepts(
            tower,
            r"Exposure.*2.*(?:to|→).*3",
            r"mark.*3",
            r"watch.*uneasy",
            r"lingering choices.*close",
        )

    def test_exposure_is_introduced_only_in_the_tower_module(self) -> None:
        part_two_start = self.rules.index("## Part II: Rules for This Adventure")
        first_exposure = self.rules.index("Exposure")
        self.assertGreaterEqual(first_exposure, part_two_start)

    def test_tower_module_covers_recovery_crises_hints_and_rumours(self) -> None:
        tower = h2_section(self.rules, "Part II: Rules for This Adventure")
        self.assert_occurs_in_order(
            tower,
            "### Conan",
            "### Exposure",
            "### Injury, Recovery, and Death",
            "### Tactical Exchanges and Crises",
            "### Hints for Play",
            "### Rumours of the Tower",
        )
        self.assert_matches_concepts(
            tower,
            r"no Fortune recovery",
            r"no Stamina recovery",
            r"resolve.*crisis.*before.*destination",
            r"read.*available method",
            r"apply.*printed state changes.*immediate",
            r"keep.*current passage.*marked",
        )

    def test_rules_at_a_glance_covers_flow_and_tower_reminders(self) -> None:
        glance = h2_section(self.rules, "Rules at a Glance")
        self.assert_occurs_in_order(
            glance,
            "### Core Action Flow",
            "Read the stakes",
            "Choose a method",
            "Capture the target",
            "Roll and select",
            "Check natural 1 or natural 20",
            "target - selected die",
            "Spend Fortune",
            "Apply the printed result",
            "Update the sheet",
            "### Tower Reminders",
        )
        for phrase in [
            "Fortune test",
            "captured current Fortune",
            "0 Stamina",
            "Exposure",
            "Possessions",
            "Story marks",
            "Tactical exchanges",
            "crisis",
        ]:
            self.assertIn(phrase, glance)
```

### Step 3: Run the focused tests and confirm RED

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
```

Expected: failures report the missing `Rules at a Glance` H2 and incomplete Tower-module wording.

### Step 4: Author the final Tower module

- [ ] Rewrite Part II to 450–550 words with exactly these H3 sections and responsibilities:

  - `Conan`: identify the young but seasoned fixed protagonist; print the complete profile; define the selected capability labels; state Fortune 10, Stamina 6, Exposure 0, Sword, and no starting marks.
  - `Exposure`: define the track before any actionable use; give the complete 0–5 table; list only the increases printed in the current playable slice; include the approved 2→3 micro-example; state the cap and E02 resolution.
  - `Injury, Recovery, and Death`: state authored 1- or 2-point losses, mortal hazards, immediate E03 at 0 Stamina, maxima, and the absence of Fortune/Stamina/Exposure recovery in this slice.
  - `Tactical Exchanges and Crises`: explain authored tactical choices, consumption timing, and the order `apply printed costs → resolve Stamina 0 or Exposure 5 crisis → follow a surviving destination`.
  - `Hints for Play`: offer process advice only—read all methods and stakes, mark the current passage, check conditions, update immediately, and trust explicit terminals. Do not identify a safe, efficient, canonical, or optimal route.
  - `Rumours of the Tower`: provide a brief atmospheric orientation based only on facts available at the opening. Do not reveal unread events, creatures, allies, solutions, or passage outcomes.

- [ ] Use `0–2`, `3`, `4`, and `5` as the visible Exposure table rows. Pair the states and mechanics explicitly: at 0–2 the intrusion is unconfirmed and all listed choices remain; at 3 the watch is uneasy and lingering choices close; at 4 a search begins and only immediate advance or withdrawal remains; at 5 the breach is discovered and E02 resolves. Preserve the approved increases from the existing rules rather than inventing new events.

### Step 5: Author Rules at a Glance

- [ ] Add `## Rules at a Glance` at the end of `quick-rules.md`, targeting 250–300 words.

- [ ] Under `### Core Action Flow`, give an explicitly numbered nine-step list:

```text
1. Read the stakes.
2. Choose a method.
3. Capture the target.
4. Roll and select the die.
5. Check natural 1 or natural 20.
6. Compute target - selected die.
7. Spend Fortune if allowed.
8. Apply the printed result.
9. Update the sheet before turning to the destination.
```

- [ ] Follow the list with one-line Advantage and Disadvantage reminders.

- [ ] Under `### Tower Reminders`, summarise Fortune timing/cost, Fortune tests, 0 Stamina, Exposure thresholds, possessions, story marks, tactical exchanges, and crisis-before-destination order. This is a lookup spread, not a second tutorial.

### Step 6: Run focused and regression tests

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all tests pass.

### Step 7: Commit the Tower module

- [ ] Review Part I for reusable language and Part II for Tower-only language, then commit:

```bash
git add tests/test_player_primer.py \
  stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
git commit -m "docs: add the Tower adventure rules module"
```

---

## Task 3: Build the Modular Adventure Sheet and Pre-S01 Entry

**Files:**

- Modify: `tests/test_player_primer.py`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`
- Test: `tests/test_player_primer.py`

### Step 1: Add failing sheet, front-matter, word-count, and passage-integrity tests

- [ ] Add:

```python
    def test_front_matter_and_story_links_follow_the_approved_order(self) -> None:
        self.assertEqual(
            h2_headings(self.rules),
            [
                "Before You Begin",
                "Part I: How to Play",
                "Part II: Rules for This Adventure",
                "Rules at a Glance",
            ],
        )
        self.assertIn("# *The Tower of the Elephant* Adventure Sheet", self.sheet)
        preamble = self.story[:self.story.index(S01_HEADING)]
        self.assert_occurs_in_order(
            preamble,
            "quick-rules.md",
            "Before You Begin",
            "Rules at a Glance",
            "adventure-sheet.md",
            "prepare its starting values",
            "S01",
        )

    def test_adventure_sheet_has_two_modular_pages(self) -> None:
        self.assert_occurs_in_order(
            self.sheet,
            "## Left Page: Character and Resources",
            "BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6",
            "Fortune",
            "Stamina",
            "## Right Page: Adventure State",
            "Exposure",
            "0–2 — Unconfirmed",
            "3 — Uneasy",
            "4 — Search",
            "5 — Discovered",
            "Possessions",
            "Sword",
            "Story marks",
            "Notes",
        )

    def test_combined_reader_guidance_is_within_the_editorial_envelope(self) -> None:
        count = reader_word_count(self.rules, self.sheet)
        self.assertGreaterEqual(count, 1800)
        self.assertLessEqual(count, 2000)

    def test_numbered_passage_prose_and_edges_are_unchanged(self) -> None:
        story_bytes = STORY.read_bytes()
        marker = S01_HEADING.encode("utf-8")
        self.assertEqual(story_bytes.count(marker), 1)
        numbered_body = story_bytes[story_bytes.index(marker):]
        self.assertEqual(
            hashlib.sha256(numbered_body).hexdigest(),
            NUMBERED_BODY_SHA256,
        )
```

### Step 2: Run the focused tests and confirm RED

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
```

Expected: the modular-page and likely word-envelope tests fail. The numbered-body digest must already pass; if it fails before editing, stop and reconcile the execution base rather than updating the constant.

### Step 3: Rewrite the two-page Adventure Sheet

- [ ] Use this exact top-level structure:

```markdown
# *The Tower of the Elephant* Adventure Sheet

## Left Page: Character and Resources

### Conan

### Fortune

### Stamina

## Right Page: Adventure State

### Exposure

### Possessions

### Story marks

### Notes
```

- [ ] On the left page, print the fixed profile and blank ten-box Fortune and six-box Stamina tracks. Tell the reader to cross off from the right and never exceed the printed maxima.

- [ ] On the right page, print a circleable 0–5 Exposure line and compact cues `0–2 — Unconfirmed`, `3 — Uneasy`, `4 — Search`, `5 — Discovered`. Print Sword as starting equipment, then writable lines for possessions, story marks, and notes.

- [ ] Keep instructions concise—approximately 100 reader-facing words—and do not repeat the primer's full rules.

### Step 4: Replace only the story preamble

- [ ] Replace the text above S01 with this sequence, retaining the existing title:

```markdown
# *The Tower of the Elephant*: Outer Wall Playtest

Read the complete [player's rules](quick-rules.md), from **Before You Begin**
through **Rules at a Glance**. Then copy or print the two-page
[Adventure Sheet](adventure-sheet.md), prepare its starting values, and begin
at **S01**.
```

- [ ] Do not touch any byte from `## S01 — The Outer Wall` through EOF.

### Step 5: Tune the editorial word envelope

- [ ] Run just the word-count test:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_player_primer.PlayerPrimerContractTests.test_combined_reader_guidance_is_within_the_editorial_envelope -v
```

Expected: `OK` with 1,800–2,000 words under the test's reader-visible counter. If under, add useful clarification in the relevant teaching section; if over, remove repetition. Do not pad or compress the writable sheet to manipulate the count.

### Step 6: Run focused and regression tests

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all tests pass, including the fixed numbered-body digest.

### Step 7: Commit the modular sheet and entry sequence

- [ ] Commit:

```bash
git add tests/test_player_primer.py \
  stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md
git commit -m "docs: add the modular Tower adventure sheet"
```

---

## Task 4: Make Live Calibration Primer-First

**Files:**

- Modify: `tests/test_player_primer.py`
- Modify: `tests/test_live_playtest.py`
- Modify: `docs/playtesting/live-playtest.md`
- Test: `tests/test_player_primer.py`
- Test: `tests/test_live_playtest.py`

### Step 1: Add the failing protocol contract

- [ ] Add this static contract test:

```python
    def test_live_protocol_requires_calibration_02_primer_before_s01(self) -> None:
        hypothesis = (
            "A reader with no knowledge of Sinew & Steel can prepare the "
            "Adventure Sheet, understand the routine play loop and "
            "Tower-specific state, and enter S01 without external explanation."
        )
        self.assertIn("tower-calibration-02", self.protocol)
        self.assertIn(hypothesis, " ".join(self.protocol.split()))
        self.assert_occurs_in_order(
            self.protocol,
            'lookup tower-calibration-02 --section "Before You Begin"',
            'lookup tower-calibration-02 --section "Part I: How to Play"',
            'lookup tower-calibration-02 --section "Part II: Rules for This Adventure"',
            'lookup tower-calibration-02 --section "Rules at a Glance"',
            "Adventure Sheet",
            "reader says they are ready",
            "show tower-calibration-02",
        )
        self.assert_matches_concepts(
            self.protocol,
            r"record.*confusion.*before.*answer",
            r"answer.*(?:from|grounded in).*primer",
        )
```

### Step 2: Add a real-file observer characterization test

- [ ] In `tests/test_live_playtest.py`, immediately before `TowerSmokeReplayTests`, add this integration class. It proves that the existing observer can present the four H2 blocks and only then show S01, without changing state:

```python
class TowerPrimerCalibrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(__file__).resolve().parents[1]

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def fixed_clock(self) -> str:
        return "2026-07-31T10:00:00Z"

    def test_primer_sections_precede_s01_without_changing_state(self) -> None:
        tower = self.root / "stories/public_domain/howard/tower_of_the_elephant/playtest"
        hypothesis = (
            "A reader with no knowledge of Sinew & Steel can prepare the "
            "Adventure Sheet, understand the routine play loop and "
            "Tower-specific state, and enter S01 without external explanation."
        )
        loaded = lp.start_session(
            Path(self.temporary_directory.name) / "sessions",
            "tower-calibration-02",
            tower / "slice-01.md",
            tower / "quick-rules.md",
            tower / "adventure-sheet.md",
            "Primer-first natural calibration",
            hypothesis,
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
        initial_state = json.loads(json.dumps(loaded.state))

        for heading in [
            "Before You Begin",
            "Part I: How to Play",
            "Part II: Rules for This Adventure",
            "Rules at a Glance",
        ]:
            found = lp.record_rules_lookup(loaded, heading, self.fixed_clock)
            self.assertTrue(found.startswith(f"## {heading}\n"))

        lp.record_note(
            loaded,
            "operator",
            "Adventure Sheet presented; reader ready for S01",
            self.fixed_clock,
        )
        shown = lp.show_current_passage(loaded, self.fixed_clock)

        self.assertTrue(shown.startswith("## S01 — The Outer Wall\n"))
        self.assertEqual(loaded.state, initial_state)
        self.assertEqual(
            [event["type"] for event in loaded.events],
            [
                "session_started",
                "rules_lookup",
                "rules_lookup",
                "rules_lookup",
                "rules_lookup",
                "operator_note",
                "passage_shown",
            ],
        )
```

### Step 3: Run the focused tests and confirm the intended split

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_player_primer.PlayerPrimerContractTests.test_live_protocol_requires_calibration_02_primer_before_s01 \
  tests.test_live_playtest.TowerPrimerCalibrationTests -v
```

Expected: the real-file characterization passes if Tasks 1–3 are complete, proving the deliberately unchanged harness already supports the four-section flow. The protocol contract fails because the current operating guide still starts at S01 with `tower-calibration-01`.

### Step 4: Rewrite the start and primer-first operating sequence

- [ ] In `docs/playtesting/live-playtest.md`, update the worked start command to session ID `tower-calibration-02`, purpose `Primer-first natural calibration`, and the approved hypothesis verbatim. Keep all fixed state arguments unchanged.

- [ ] Insert `## Primer-first calibration` before `## Live operating sequence` and give these commands in this order:

```bash
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Before You Begin"
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Part I: How to Play"
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Part II: Rules for This Adventure"
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Rules at a Glance"
python3 tools/live_playtest.py note tower-calibration-02 --kind operator \
  --text "Adventure Sheet presented; reader says they are ready for S01"
python3 tools/live_playtest.py show tower-calibration-02
```

- [ ] State the operating rule directly: record each spontaneous rules question or confusion before answering; answer only from reached reader material and the primer; pause before S01 if a procedural question remains unresolved; show S01 only after the reader says they are ready.

- [ ] Keep the existing passage-play sequence after this prerequisite. Update the Calibration Checklist so its first entries require the four lookups, sheet preparation, and reader readiness before S01.

- [ ] Do not claim that this second run is blind: the first reader has already seen S01 and Exposure. State that it calibrates clarity/usability and that later testing needs readers unfamiliar with both S&S and this slice.

### Step 5: Run focused and full tests

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_player_primer.PlayerPrimerContractTests.test_live_protocol_requires_calibration_02_primer_before_s01 \
  tests.test_live_playtest.TowerPrimerCalibrationTests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all tests pass.

### Step 6: Commit the primer-first protocol

- [ ] Commit:

```bash
git add docs/playtesting/live-playtest.md \
  tests/test_player_primer.py tests/test_live_playtest.py
git commit -m "docs: require primer-first live calibration"
```

---

## Task 5: Perform the Focused Editorial and Technical Acceptance Pass

**Files:**

- Review: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`
- Review: `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`
- Review: `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`
- Review: `docs/playtesting/live-playtest.md`
- Review: `tests/test_player_primer.py`
- Review: `tests/test_live_playtest.py`

### Step 1: Run the current-Python acceptance suite

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/live_playtest.py --help
```

Expected: both test commands end in `OK`; CLI help exits 0.

### Step 2: Run the Python 3.10 compatibility suite

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python 3.10 \
  python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: the full suite ends in `OK`. A benign `uv --no-project` warning does not change the result.

### Step 3: Verify the protected boundaries

- [ ] Run:

```bash
git diff --check c27a3f616395a3305b13a53ba24efc4dc71021a8..HEAD
git diff --exit-code c27a3f616395a3305b13a53ba24efc4dc71021a8..HEAD -- tools/live_playtest.py
git ls-files '.playtest/**'
git check-ignore -v .playtest/sessions/example/report.md
python3 - <<'PY'
import hashlib
from pathlib import Path

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md")
payload = path.read_bytes()
marker = "## S01 — The Outer Wall".encode("utf-8")
numbered = payload[payload.index(marker):]
print(hashlib.sha256(numbered).hexdigest())
PY
```

Expected:

- no whitespace errors;
- no diff for `tools/live_playtest.py`;
- `git ls-files` prints nothing under `.playtest/`;
- `git check-ignore` identifies the repository ignore rule; and
- the digest is `2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496`.

### Step 4: Perform one editorial repair pass

- [ ] Read the five front-matter components in their intended order, then read S01. Check:

  - every term in S01 is defined before use;
  - the worked example reconstructs the complete resolution loop without outside explanation;
  - Part I contains no Tower-only rule and Part II contains no implied universal rule;
  - every tracked state has a consumer in the playable slice;
  - the Adventure Sheet can be prepared from the primer alone;
  - Hints provide process advice without route advice;
  - Rumours add atmosphere without revealing an unread event;
  - Rules at a Glance works as a lookup aid rather than duplicate instruction; and
  - the language is direct, concrete, modern, and original.

- [ ] Make one focused repair pass for material findings only. If edits change a contractual fact, add or adjust the narrow test first. Do not continue polishing after a clean reread.

### Step 5: Record final evidence without starting the calibration

- [ ] Run:

```bash
git status --short --branch
git log --oneline c27a3f616395a3305b13a53ba24efc4dc71021a8..HEAD
git diff --stat c27a3f616395a3305b13a53ba24efc4dc71021a8..HEAD
```

- [ ] If the editorial pass changed tracked files, rerun Steps 1–3 and commit a narrowly named repair. Otherwise leave the four implementation commits as the complete result.

- [ ] Report the tracked implementation as ready for acceptance calibration, with test evidence, the exact reader-word count, protected-boundary checks, and any residual limitation. Explicitly state that static tests and editorial review do not establish reader comprehension, that `tower-calibration-02` has not yet been started, and that beginning the user-gated live playtest is the next increment after review and integration.
