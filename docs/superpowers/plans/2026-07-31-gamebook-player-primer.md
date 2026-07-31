# Gamebook Player Primer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Turn the approved player-primer design into self-contained, publishable Tower front matter that teaches a new reader everything needed before S01, with a modular Adventure Sheet and a primer-first live-calibration protocol.

**Architecture:** Keep one authoritative Tower rules document. Its four unique H2 sections form the facilitator lookup boundary; H3 subsections carry the detailed teaching. Keep the writable sheet separate, change only the story preamble before S01, and verify software-consumed boundaries with standard-library integration tests. Validate human-facing prose through a focused editorial review and the subsequent live calibration.

**Tech Stack:** Markdown, Python 3.10+ standard-library unittest, the existing tools/live_playtest.py APIs, Git.

**Execution ruling:** Before implementation, the user selected the behavioural-hybrid test boundary. Permanent tests cover harness-consumed rules structure, reader-link resolution, and the protected S01 byte range. Exact prose, editorial length, atmosphere, clarity, and instructional completeness are reviewed directly and then tested with the user in tower-calibration-02; they are not frozen with source-text assertions.

## Global Constraints

- Implement the approved specification in docs/superpowers/specs/2026-07-31-gamebook-player-primer-design.md, subject to the behavioural-hybrid testing ruling above.
- Work from approved base commit b6d60c021372aea4526a218e46ca9fc64af17946 or its reviewed descendant.
- Keep stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md as the single authoritative Tower primer. Do not introduce includes, templates, generated copies, or a generic rules source.
- Use exactly these unique H2 headings, in this order, because the observer indexes H2 blocks for lookup: Before You Begin; Part I: How to Play; Part II: Rules for This Adventure; Rules at a Glance. Use H3 or lower for every internal subsection.
- Keep all reader-facing mechanics self-contained. Knowledge of the full Sinew & Steel rules must never be required.
- Keep the instructional prose original. Borrow the established function of self-contained gamebook rules and a writable record sheet, but do not copy proprietary wording, examples, tables, or distinctive layouts.
- Retain the four capability meanings and the selected Tower labels consistently: Brawn (BRN) 13, Agility (AGI) 12, Cunning (CUN) 12, Will (WIL) 12.
- Keep the approved fixed starting state: Fortune 10/10, Stamina 6/6, Exposure 0/5, Sword, and no starting story marks.
- Keep Exposure inside the Tower-specific module. It is the title's only primary story track and must be fully explained before S01.
- Do not modify tools/live_playtest.py, dependency files, build tooling, publishing infrastructure, or README.md.
- Do not change numbered passage prose, choices, destinations, identifiers, or edges. The SHA-256 of slice-01.md from the first UTF-8 byte of the S01 heading through EOF must remain 2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496.
- Keep local session material under .playtest/ ignored and untracked. Preserve tower-calibration-01; do not start tower-calibration-02 during implementation.
- Aim for 1,800–2,000 reader-facing words across quick-rules.md and adventure-sheet.md, excluding Markdown link destinations, HTML comments, box glyphs, and writable blank lines.
- Use TDD for new executable behavior. For human-facing prose, follow the user's behavioural-hybrid ruling: run existing regressions and behavioural characterizations, then use editorial and live acceptance rather than source-text unit tests.
- Commit after each completed task. Do not push implementation commits until the reviewed branch is accepted for integration.
- Treat the tracked result as ready for acceptance calibration, not as proof of reader comprehension. Starting tower-calibration-02 is a separate, user-gated follow-up.

---

## Task 1: Teach the Reusable Core

**Files:**

- Modify: stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md

### Step 1: Record the editorial baseline

- [ ] Record the current H2 lookup surface and rules word count in the task report:

~~~bash
python3 - <<'PY'
import re
from pathlib import Path
from tools import live_playtest as lp

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md")
print("sections:", list(lp.index_rule_sections(path)))
print("words:", len(re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*", path.read_text())))
PY
~~~

- [ ] Note in the report that this is editorial work under the approved behavioural-hybrid ruling: no static prose test should be added. The existing suite is the regression baseline.

### Step 2: Rewrite Before You Begin and Part I

- [ ] Replace the current reference-style opening with this exact top-level and subsection structure:

~~~markdown
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
~~~

- [ ] Write 100–150 words under Before You Begin. State that the reader needs the book, its Adventure Sheet, a pen or pencil, one d20, and optionally a second d20. State that there is no character creation and the book supplies the protagonist and starting state.

- [ ] Include this attribution verbatim, with the title italicised:

    These gamebook rules are adapted from *Sinew & Steel*, a d20 tabletop role-playing game by Barry W. Brook. You need no knowledge of that system; everything required to play appears here.

- [ ] Write 850–950 words under Part I using the approved purpose → procedure → example → record teaching pattern. Explain how to read a fixed profile supplied by a title, but keep Conan's exact values, Tower labels, and Exposure in Part II.

- [ ] Teach these portable concepts:

  - four broad attributes and their use as captured targets;
  - passage choices, printed conditions, and immediate state updates;
  - d20 roll-under tests, with an ordinary selected result succeeding at or below the captured target;
  - Advantage as two d20s keeping the lower, and Disadvantage as two d20s keeping the higher;
  - selected natural 1 and 20 as locked results before Fortune;
  - margin as target minus selected die, with no independent effect unless the passage explicitly reads it;
  - Fortune spending after an ordinary selected die, and Fortune as the captured target when a passage calls for a Fortune test;
  - authored Stamina loss and the passage's explicit instruction at 0 Stamina;
  - possessions and semantic story marks;
  - authored tactical exchanges rather than repeated enemy-stat rounds;
  - escape, evasion, or withdrawal only when printed; and
  - explicit death, withdrawal, crisis, and slice-complete endings.

### Step 3: Write the worked Conan example

- [ ] Place one non-canonical Conan vignette immediately after tests and Fortune are explained. Give it Tower atmosphere without reproducing or foreshadowing a numbered passage. Tell the reader not to mark the real sheet.

- [ ] State this complete loop unambiguously:

  1. the passage gives meaningful stakes;
  2. Conan chooses a method;
  3. the captured attribute target is 12;
  4. the selected ordinary die is 15;
  5. provisional margin is 12 - 15 = -3;
  6. the reader spends 3 Fortune;
  7. final die is 12 and final margin is 0;
  8. Conan succeeds;
  9. Fortune falls from 10 to 7; and
  10. the reader follows the printed success.

- [ ] Add a short contrast: a selected natural 20 is locked and cannot be changed with Fortune.

### Step 4: Preserve the interim title module

- [ ] Move the existing Tower-specific material below Part II and demote every internal heading to H3. Do not add another H2. Task 2 will edit and reorganise this material.

- [ ] Ensure Part I contains neither the exact Conan profile nor Exposure.

### Step 5: Verify the Task 1 boundary

- [ ] Run this production-index check:

~~~bash
python3 - <<'PY'
from pathlib import Path
from tools import live_playtest as lp

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md")
assert list(lp.index_rule_sections(path)) == [
    "before you begin",
    "part i: how to play",
    "part ii: rules for this adventure",
]
print("Task 1 lookup surface: OK")
PY
~~~

- [ ] Read Before You Begin and Part I once in order. Confirm every portable concept above is taught, the arithmetic is correct, the example is non-canonical, and the prose is plain, direct, and original.

- [ ] Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
~~~

Expected: the lookup check prints OK, the full suite passes, and the diff has no whitespace errors.

### Step 6: Commit the reusable core

- [ ] Commit:

~~~bash
git add stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
git commit -m "docs: teach the reusable gamebook core"
~~~

---

## Task 2: Complete the Tower Module and Rules at a Glance

**Files:**

- Modify: stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md

### Step 1: Author the final Tower module

- [ ] Rewrite Part II to 450–550 words with exactly these H3 sections:

~~~markdown
### Conan

### Exposure

### Injury, Recovery, and Death

### Tactical Exchanges and Crises

### Hints for Play

### Rumours of the Tower
~~~

- [ ] Under Conan:

  - identify the young but seasoned fixed protagonist;
  - print BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6;
  - define Brawn (BRN), Agility (AGI), Cunning (CUN), and Will (WIL);
  - state Fortune 10, Stamina 6, Exposure 0, Sword, and no starting story marks.

- [ ] Under Exposure:

  - define it before any actionable use;
  - state that it starts at 0 and is capped at 5;
  - give visible table rows for 0–2, 3, 4, and 5;
  - pair each state with its mechanic: 0–2 unconfirmed/all choices; 3 uneasy/lingering closes; 4 search/immediate advance or withdrawal only; 5 discovered/resolve E02;
  - preserve only the increases already printed in the playable slice: another patrol interval, loud or avoidable disturbance, failed Taurus standoff, natural 20 in that standoff, and the printed lion-tactic amount;
  - state that no ordinary event lowers Exposure; and
  - include the micro-example 2 → 3: mark 3, the watch becomes uneasy, and lingering choices begin to close.

- [ ] Under Injury, Recovery, and Death, state authored 1- or 2-point losses, mortal hazards, immediate E03 at 0 Stamina, maxima, and no Fortune, Stamina, or Exposure recovery in this slice.

- [ ] Under Tactical Exchanges and Crises, explain authored tactical choices, consumption timing, and this order: apply printed costs; resolve Stamina 0 or Exposure 5; follow a surviving destination.

- [ ] Hints for Play must advise process only: read every method and stake, mark the current passage, check conditions, update immediately, and trust explicit terminals. Do not identify a safe, efficient, canonical, or optimal route.

- [ ] Rumours of the Tower must provide brief atmospheric orientation from opening knowledge only. Do not reveal unread events, creatures, allies, solutions, or passage outcomes.

### Step 2: Author Rules at a Glance

- [ ] Add the fourth and final H2, Rules at a Glance, targeting 250–300 words.

- [ ] Under H3 Core Action Flow, give this numbered sequence:

  1. Read the stakes.
  2. Choose a method.
  3. Capture the target.
  4. Roll and select the die.
  5. Check natural 1 or natural 20.
  6. Compute target - selected die.
  7. Spend Fortune if allowed.
  8. Apply the printed result.
  9. Update the sheet before turning to the destination.

- [ ] Follow with one-line Advantage and Disadvantage reminders.

- [ ] Under H3 Tower Reminders, summarise Fortune timing/cost, Fortune tests, 0 Stamina, Exposure thresholds, possessions, story marks, tactical exchanges, and crisis-before-destination order. Keep this a lookup aid rather than a second tutorial.

### Step 3: Verify module boundaries and editorial allocation

- [ ] Run the production-index check:

~~~bash
python3 - <<'PY'
from pathlib import Path
from tools import live_playtest as lp

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md")
assert list(lp.index_rule_sections(path)) == [
    "before you begin",
    "part i: how to play",
    "part ii: rules for this adventure",
    "rules at a glance",
]
print("Final lookup surface: OK")
PY
~~~

- [ ] Use this one-off editorial counter and record all four H2 counts in the task report:

~~~bash
python3 - <<'PY'
import re
from pathlib import Path
from tools import live_playtest as lp

word_re = re.compile(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*")
path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md")
for heading, block in lp.index_rule_sections(path).items():
    print(heading, len(word_re.findall(block)))
PY
~~~

- [ ] Read Part II and Rules at a Glance against every requirement above. Confirm Exposure first appears in Part II, all four thresholds pair fiction with mechanics, Hints contain no route advice, and Rumours contain no unread information.

- [ ] Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
~~~

Expected: the full suite passes and the diff is clean.

### Step 4: Commit the Tower module

- [ ] Commit:

~~~bash
git add stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
git commit -m "docs: add the Tower adventure rules module"
~~~

---

## Task 3: Build the Modular Adventure Sheet and Pre-S01 Entry

**Files:**

- Create: tests/test_player_primer.py
- Modify: stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md
- Modify: stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md

### Step 1: Add behavioural characterization tests

- [ ] Create tests/test_player_primer.py with these tests. Each names a real integration break: the harness lookup surface becomes unusable, a reader link does not resolve or is reordered, or a numbered-passage byte changes.

~~~python
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
~~~

- [ ] Run the characterization tests before editing the sheet or story:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
~~~

Expected: all three pass against the completed Tasks 1–2 and the protected existing story. Record this GREEN characterization explicitly; no RED is expected because the user approved tests for unchanged integration boundaries rather than source-text tests for prose.

### Step 2: Rewrite the two-page Adventure Sheet

- [ ] Use this exact structure:

~~~markdown
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
~~~

- [ ] On the left page, print the fixed profile and blank ten-box Fortune and six-box Stamina tracks. Tell the reader to cross off from the right and never exceed the printed maxima.

- [ ] On the right page, print a circleable 0–5 Exposure line and compact cues: 0–2 — Unconfirmed; 3 — Uneasy; 4 — Search; 5 — Discovered. Print Sword as starting equipment, then writable lines for possessions, story marks, and notes.

- [ ] Keep instructions concise, approximately 100 reader-facing words, and do not repeat the primer's full rules.

### Step 3: Replace only the story preamble

- [ ] Replace the text above S01 with this sequence, retaining the existing title:

~~~markdown
# *The Tower of the Elephant*: Outer Wall Playtest

Read the complete [player's rules](quick-rules.md), from **Before You Begin**
through **Rules at a Glance**. Then copy or print the two-page
[Adventure Sheet](adventure-sheet.md), prepare its starting values, and begin
at **S01**.
~~~

- [ ] Do not touch any byte from the S01 heading through EOF.

### Step 4: Verify the reader files

- [ ] Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
~~~

Expected: all tests pass, including link resolution and the raw-byte digest.

- [ ] Run the one-off reader-visible word counter and record the exact value:

~~~bash
python3 - <<'PY'
import re
from pathlib import Path

tower = Path("stories/public_domain/howard/tower_of_the_elephant/playtest")
texts = [
    (tower / "quick-rules.md").read_text(encoding="utf-8"),
    (tower / "adventure-sheet.md").read_text(encoding="utf-8"),
]
visible = "\n".join(texts)
visible = re.sub(r"<!--.*?-->", " ", visible, flags=re.DOTALL)
visible = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", visible)
visible = re.sub(r"https?://\S+", " ", visible)
words = re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*", visible)
print(len(words))
assert 1800 <= len(words) <= 2000
PY
~~~

Expected: 1,800–2,000 words. If outside the range, add useful clarification or remove repetition in the relevant rules section; do not pad the sheet.

### Step 5: Commit the sheet and entry sequence

- [ ] Commit:

~~~bash
git add tests/test_player_primer.py \
  stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md
git commit -m "docs: add the modular Tower adventure sheet"
~~~

---

## Task 4: Make Live Calibration Primer-First

**Files:**

- Modify: tests/test_live_playtest.py
- Modify: docs/playtesting/live-playtest.md

### Step 1: Add the real-file observer characterization

- [ ] Immediately before TowerSmokeReplayTests in tests/test_live_playtest.py, add:

~~~python
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
~~~

- [ ] Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_live_playtest.TowerPrimerCalibrationTests -v
~~~

Expected: the characterization passes before the protocol edit, proving the unchanged harness supports the approved sequence and does not mutate state.

### Step 2: Rewrite the start and primer-first operating sequence

- [ ] In docs/playtesting/live-playtest.md, update the worked start command to session ID tower-calibration-02, purpose Primer-first natural calibration, and this hypothesis verbatim:

    A reader with no knowledge of Sinew & Steel can prepare the Adventure Sheet, understand the routine play loop and Tower-specific state, and enter S01 without external explanation.

- [ ] Keep all fixed state arguments unchanged.

- [ ] Insert H2 Primer-first calibration before H2 Live operating sequence and give these commands in this order:

~~~bash
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Before You Begin"
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Part I: How to Play"
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Part II: Rules for This Adventure"
python3 tools/live_playtest.py lookup tower-calibration-02 --section "Rules at a Glance"
python3 tools/live_playtest.py note tower-calibration-02 --kind operator \
  --text "Adventure Sheet presented; reader says they are ready for S01"
python3 tools/live_playtest.py show tower-calibration-02
~~~

- [ ] State the operating rule directly: record each spontaneous rules question or confusion before answering; answer only from reached reader material and the primer; pause before S01 if a procedural question remains unresolved; show S01 only after the reader says they are ready.

- [ ] Keep the existing passage-play sequence after this prerequisite. Update the Calibration Checklist so its first entries require the four lookups, sheet preparation, and reader readiness before S01.

- [ ] State that this second run calibrates clarity and usability rather than complete blindness because the first reader has already seen S01 and Exposure. Later testing needs readers unfamiliar with both S&S and this slice.

### Step 3: Verify and commit the protocol

- [ ] Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_live_playtest.TowerPrimerCalibrationTests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
~~~

Expected: all tests pass and the diff is clean.

- [ ] Manually compare every documented lookup/start/note/show argument with tools/live_playtest.py --help. Do not create a real .playtest session.

- [ ] Commit:

~~~bash
git add docs/playtesting/live-playtest.md tests/test_live_playtest.py
git commit -m "docs: require primer-first live calibration"
~~~

---

## Task 5: Perform the Focused Editorial and Technical Acceptance Pass

**Files:**

- Review: stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
- Review: stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md
- Review: stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md
- Review: docs/playtesting/live-playtest.md
- Review: tests/test_player_primer.py
- Review: tests/test_live_playtest.py

### Step 1: Read the reader journey as a book

- [ ] Read, in order: Before You Begin; Part I; the worked Conan example; Part II; Rumours; Rules at a Glance; Adventure Sheet; story preamble; S01.

- [ ] Check manually:

  - every term in S01 is defined before use;
  - the worked example reconstructs the complete resolution loop without outside explanation;
  - all approved arithmetic and resource changes are correct;
  - Part I contains no Tower-only rule and Part II contains no implied universal rule;
  - all four capability labels, abbreviations, values, and scopes are consistent;
  - every tracked state has a consumer in the playable slice;
  - Exposure has all four thresholds and is explained before actionable use;
  - the Adventure Sheet can be prepared from the primer alone;
  - Hints provide process advice without route advice;
  - Rumours add atmosphere without revealing an unread event;
  - Rules at a Glance works as a lookup aid rather than duplicate instruction;
  - the protocol presents all front matter before S01; and
  - the language is direct, concrete, modern, and original.

- [ ] Make one focused repair pass for material findings only. Do not continue polishing after a clean reread.

### Step 2: Record the final editorial measures

- [ ] Run the combined word-count command from Task 3 and record the exact 1,800–2,000 result.

- [ ] Run the H2 counter from Task 2 and record the allocation for Before You Begin, Part I, Part II, and Rules at a Glance.

- [ ] Record any reader-comprehension question that remains for tower-calibration-02; do not answer it by silently adding outside S&S knowledge.

### Step 3: Run the current-Python acceptance suite

- [ ] Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/live_playtest.py --help
~~~

Expected: both test commands end in OK; CLI help exits 0.

### Step 4: Run Python 3.10 compatibility

- [ ] Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python 3.10 \
  python -m unittest discover -s tests -p 'test_*.py' -v
~~~

Expected: the suite ends in OK. A benign uv --no-project warning does not change the result.

### Step 5: Verify protected boundaries

- [ ] Run:

~~~bash
git diff --check b6d60c021372aea4526a218e46ca9fc64af17946..HEAD
git diff --exit-code b6d60c021372aea4526a218e46ca9fc64af17946..HEAD -- tools/live_playtest.py
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
~~~

Expected:

- no whitespace errors;
- no diff for tools/live_playtest.py;
- no tracked .playtest files;
- the repository ignore rule is reported; and
- the digest is 2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496.

### Step 6: Record final evidence without starting calibration

- [ ] Run:

~~~bash
git status --short --branch
git log --oneline b6d60c021372aea4526a218e46ca9fc64af17946..HEAD
git diff --stat b6d60c021372aea4526a218e46ca9fc64af17946..HEAD
~~~

- [ ] If the editorial pass changed tracked files, rerun Steps 2–5 and commit a narrowly named repair. Otherwise leave the four implementation commits as the completed tracked result.

- [ ] Report the branch as ready for acceptance calibration, with test evidence, exact word counts, protected-boundary checks, and residual limitations. Explicitly state that static checks and editorial review do not establish reader comprehension, that tower-calibration-02 has not started, and that the user-gated live playtest is the next increment after review and integration.
