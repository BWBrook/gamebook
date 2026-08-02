# Reader-first player primer rewrite implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite *The Tower of the Elephant* front matter as a warm, self-contained introduction that a first-time gamebook reader can follow, while preserving every settled mechanic and preparing a fresh, small-chunk live calibration.

**Architecture:** Keep the Tower primer in one authoritative Markdown file whose four H2 sections remain the observer-harness lookup boundary. Teach the portable rules in Part I, then introduce Conan and the Tower-specific rules in Part II. Keep the writable Adventure Sheet separate, repair the internal Exposure description at its source, and update only the facilitation protocol for the next live session. Human prose is accepted through reader-first editorial review; existing tests protect the software-consumed headings, reader links, and numbered story bytes.

**Tech Stack:** Markdown, Python 3.10+ standard-library `unittest`, the existing `tools/live_playtest.py` read/lookup surface, Git.

**Approved specification:** `docs/superpowers/specs/2026-08-01-reader-first-player-primer-rewrite-design.md`

## Global Constraints

- Work in an isolated Git worktree on a feature branch. Do not implement on `main`.
- Use the approved specification as the source of truth. Preserve the mechanics; change their order, voice, examples, and reader-facing names only as the specification permits.
- Keep `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md` as the single authoritative Tower primer.
- Keep exactly these unique H2 headings, in this order: `Before You Begin`; `Part I: How to Play`; `Part II: Rules for This Adventure`; `Rules at a Glance`. Use H3 or lower for their internal subdivisions.
- Assume a capable reader of about twelve who has never read Howard, played a gamebook, or encountered *Sinew & Steel*. Address the reader as `you` and introduce every term before another rule depends on it.
- Keep Part I portable. Before Part II introduces the Tower labels, call the number used for a test its `score`; do not use Brawn, Agility, Cunning, Will, or their abbreviations there.
- Keep Conan's fixed profile unchanged: `BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6`. He starts with the Sword, Exposure 0, and no story marks.
- Keep the settled core unchanged: roll one d20; equal to or below the relevant score succeeds; Margin is score minus final die; Fortune lowers an ordinary die one point per point spent; Advantage keeps the lower of two d20s; Disadvantage keeps the higher; a selected natural 1 or 20 cannot be altered with Fortune.
- A Fortune test uses the current Fortune score fixed when the passage calls for the test. Later spending can lower the die without changing that fixed score.
- Passages apply Stamina loss directly; Stamina 0 reaches the death ending. The current material restores no Fortune, Stamina, or Exposure.
- Exposure is capped at 5. Values 3 and 4 create unease and urgency in the fiction without universally removing choices. Exposure 5 reaches the discovery crisis named by the current passage.
- Possessions and story marks are awarded, consulted, and crossed off only when a passage instructs. Tactical action uses passage choices and consequences rather than repeated opponent-stat rounds.
- Keep the prose original. Do not copy or closely paraphrase wording, examples, procedures, tables, stat packages, or layouts from *Fighting Fantasy*, *Lone Wolf*, or another proprietary system.
- Apply the `audit-ai-writing` skill as an editorial method. Rebuild purpose, order, and examples rather than swapping synonyms. Prefer concrete, affirmative prose; use rhetorical negation sparingly under the agreed saffron rule; remove generic AI cadence and designer jargon.
- Player-facing prose must omit `authored`, `captured target`, `capture the target`, `resolution-inert`, `terminal` as a noun for an ending, `slice` for the adventure, `state and effect`, and internal directions such as `resolve E02` outside an actual reached passage.
- Preserve progressive disclosure. Before the story reveals them, do not name specific allies, enemies, obstacles, tactics, routes, passage identifiers, or outcomes. Premise material and starting equipment are allowed.
- Do not modify `tools/live_playtest.py`, dependency files, build tooling, `README.md`, or story prose and route logic from S01 onward.
- The SHA-256 of `slice-01.md` from the first UTF-8 byte of `## S01 — The Outer Wall` through EOF must remain `2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496`.
- Keep the pre-S01 reader links in rules-then-sheet order. Keep `.playtest/` evidence ignored and untracked. Do not resume `tower-calibration-02` or start `tower-calibration-03` during implementation.
- Add no brittle assertions over human prose. Add or change tests only if real software-consumed behaviour changes; no such change is expected in this plan.
- Commit each implementation task separately. Do not push or merge the feature branch before the user has reviewed the revised primer.
- Treat passing tests as structural evidence. Reader comprehension remains open until the subsequent live calibration.

---

## Task 1: Rewrite the welcome and portable rules

**Files:**

- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`

### Step 1: Record the protected baseline

- [ ] Record the current commit and H2 lookup surface in the task report:

```bash
git rev-parse HEAD
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from pathlib import Path
from tools import live_playtest as lp

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md")
print(list(lp.index_rule_sections(path)))
PY
```

- [ ] Confirm that this task changes only `quick-rules.md`. Preserve the existing Part II and Rules at a Glance material until Task 2 rewrites it.

### Step 2: Rewrite Before You Begin

- [ ] Write roughly 200-250 words that welcome the reader and do these jobs in a natural order:

  - identify this as a *Sinew & Steel* gamebook adaptation of a classic story and explain the project in one brief paragraph;
  - promise the thief-city of Zamora, Yara's silver tower, the Heart of the Elephant, and Conan's decision to steal it without disclosing later encounters;
  - introduce Conan of Cimmeria as about seventeen, unusually formidable after a harsh upbringing, hard travel, and early violence;
  - use Howard's line `a thief, a reaver, a slayer, with gigantic melancholies and gigantic mirth` exactly once, attribute it to the imagined Nemedian chroniclers in *The Phoenix on the Sword*, and present it as a glimpse of the man Conan will become; and
  - list the book, Adventure Sheet, pen or pencil, one d20, and optional second d20, then say plainly that this book contains every rule needed to play.

- [ ] Briefly identify *Sinew & Steel* as Barry W. Brook's d20 tabletop role-playing game without assuming that the reader knows it.

### Step 3: Rebuild Part I in teaching order

- [ ] Target 950-1,100 words and use this H3 sequence:

```markdown
### Your Adventure Sheet

### Reading the Adventure

### When the Story Calls for a Test

### Margin

### Fortune

### Advantage and Disadvantage

### Natural Results

### A Worked Conan Example

### Stamina, Possessions, and Story Marks

### Tactical Exchanges and Endings
```

- [ ] Explain the Adventure Sheet as the place that remembers abilities, condition, equipment, and discoveries. Teach the reached-passage loop: read, choose an available action, follow its printed destination, and mark changes immediately.

- [ ] Introduce the roll-under test before modifiers or resources. A passage names the ability, the reader finds its score, and one d20 equal to or below that score succeeds. Give the immediate example that score 13 succeeds on 13 or less and fails on 14 or more. Say plainly that low rolls are better.

- [ ] Teach Margin before Fortune. Explain degree as well as arithmetic: score minus die; positive is success, zero is the narrowest success, negative is failure, and distance from zero can let a passage distinguish stronger or weaker outcomes. State that many passages need only success or failure.

- [ ] Teach Fortune as a limited reserve that lowers an ordinary die after it is seen. Include one conversational ordinary-test example with the old die, points spent, new die, new Margin, outcome, and Fortune remaining.

- [ ] Explain a Fortune test through a separate small example. Fix the current Fortune score before rolling; spending after the roll may lower the die, while the fixed score stays the same. Avoid implementation language.

- [ ] Remind the reader that low is good before Advantage and Disadvantage: roll two d20s and keep the lower with Advantage; keep the higher with Disadvantage. Ground each in a short possible Conan action.

- [ ] After the kept die has been chosen, teach natural 1 as the best printed result and natural 20 as the worst credible printed result. Fortune changes ordinary results only, so either natural result stands as rolled.

### Step 4: Teach one complete example and the remaining sheet fields

- [ ] Address the reader directly throughout the worked example. Open with: `Use the figures printed in this example and leave your Adventure Sheet unchanged.`

- [ ] Use a spoiler-safe Tower situation outside the real numbered adventure and include this complete loop:

  1. the imaginary passage presents a situation and offers actions;
  2. you choose Conan's method;
  3. the relevant score is 12;
  4. you roll 15;
  5. Margin is `12 - 15 = -3`;
  6. you spend 3 Fortune to lower the roll to 12;
  7. the final Margin is 0 and the attempt succeeds;
  8. Fortune falls from 10 to 7; and
  9. you follow the successful destination printed by the imaginary passage.

- [ ] Follow with a short natural-20 continuation in plain language.

- [ ] Explain Stamina as Conan's ability to keep going after injury; passages print the loss and the consequence at zero. Recovery occurs only when printed, and the current Tower adventure gives none.

- [ ] Identify the Sword plainly as Conan's starting possession. Teach the lifecycle of a possession: a passage awards it, you write it down, a later choice may require it, and a passage may tell you to cross it off when used.

- [ ] Teach story marks with the spoiler-safe phrase `Recognised the temple seal`: a passage tells you to write it, a later choice checks the exact phrase, and the mark is crossed off only when instructed.

- [ ] Teach tactical action with a brief invented threat. A passage presents methods that may use different abilities, possessions, or consequences; you choose once, roll if asked, apply the result, and follow the destination.

- [ ] Describe endings in familiar language: the adventure ends, Conan dies, Conan withdraws, or this part of the adventure is complete.

### Step 5: Perform the prose and structural checks

- [ ] Read Before You Begin and Part I aloud. Confirm that each paragraph has a reader-facing job, every term appears after its explanation, no sentence assumes knowledge of Part II, and the tone sounds like an experienced Custodian teaching across a table.

- [ ] Use the `audit-ai-writing` skill and its manual rubric. Scan for generic significance, decorative triplets, negative parallelism, repeated openings, over-helpful service tone, inflated verbs, synonym churn, and AI-favoured vocabulary. Repair clusters through structural edits, then re-read.

- [ ] Confirm the exact four-section lookup surface remains intact:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from pathlib import Path
from tools import live_playtest as lp

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md")
assert list(lp.index_rule_sections(path)) == [
    "before you begin",
    "part i: how to play",
    "part ii: rules for this adventure",
    "rules at a glance",
]
print("Task 1 lookup surface: OK")
PY
```

- [ ] Run the focused regression and whitespace check:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
git diff --check
```

### Step 6: Commit Task 1

- [ ] Commit only the welcome and Part I rewrite:

```bash
git add stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
git commit -m "docs: rewrite the reader-first gamebook core"
```

---

## Task 2: Rewrite the Tower module and quick reference

**Files:**

- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`

### Step 1: Rewrite Part II for a first-time reader

- [ ] Target 450-600 words. Introduce Conan as a person before showing statistics. Include his approximate age, Cimmerian origin, physical presence, hard-won experience, outsider's view of civilisation, and reason for entering the tower.

- [ ] Print the fixed profile exactly:

```text
BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6
```

- [ ] Explain the four abilities without repetitive sentence frames: Brawn concerns force and endurance; Agility governs speed and physical precision; Cunning draws on observation, stealth, and guile; Will measures courage and self-command.

- [ ] Tell the reader to record the four abilities, Fortune 10, Stamina 6, the Sword under Possessions, and an empty Story Marks area. Introduce Exposure in the next subsection before asking the reader to record 0.

### Step 2: Teach Exposure through fiction and example

- [ ] Define Exposure as the growing risk that Conan's intrusion will be noticed. Say that a passage may add it after delay, disturbance, or evidence, and that the reader marks each increase immediately. Then ask the reader to begin at 0.

- [ ] Use connected prose for the main lesson:

  - at 0-2, night still hides the intrusion;
  - at 3, the watch grows uneasy;
  - at 4, a search begins and later passages become more urgent; and
  - at 5, the intruders are discovered and the current passage sends the reader to the resulting crisis.

- [ ] State clearly that values 3 and 4 remove no choices by themselves; the current passage prints any restriction it applies.

- [ ] Add a small spoiler-safe example of an increase and its immediate mark on the sheet. Keep the main teaching in prose rather than a state/effect table.

- [ ] Omit future names, creatures, patrol timing, tactics, encounter outcomes, `E02`, and all other internal passage codes.

### Step 3: Complete the adventure-specific advice

- [ ] Explain Tower-specific Stamina and recovery facts: maximum 6, printed loss, death at zero, and no recovery during this continuous intrusion. State that printed Stamina and Exposure changes are applied before following the next destination.

- [ ] Add a spoiler-safe tactical illustration that makes the sequence concrete: read the situation and available methods, choose one, roll if called for, mark the printed consequence, then follow the destination.

- [ ] Give practical advice in the voice of an experienced player: keep a finger or marker at the current passage, read all available actions, and update the sheet before turning the page.

- [ ] Retain a short, atmospheric Rumours section about Yara, the silver tower, and the Heart of the Elephant. Add anticipation without repeating the opening blurb or revealing the tower's discoveries.

### Step 4: Rewrite Rules at a Glance

- [ ] Target 220-280 words. Use only terms already taught.

- [ ] On the reusable side, summarise in learned order: the roll-under test, Margin, Fortune, Advantage, Disadvantage, and natural results.

- [ ] On the Tower side, summarise Conan's starting sheet, Stamina, the Sword and later possessions, story marks, and Exposure thresholds. A compact list or table is allowed here after the prose lesson.

- [ ] Keep internal passage codes, future encounter names, and every banned player-facing term off the spread.

### Step 5: Audit the complete rules document

- [ ] Confirm the editorial allocations and report the counts. Use H2 boundaries rather than treating headings as prose:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import re
from pathlib import Path

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md")
text = path.read_text(encoding="utf-8")
sections = re.split(r"(?m)^## ", text)[1:]
for section in sections:
    heading, body = section.split("\n", 1)
    words = re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*", body)
    print(f"{heading}: {len(words)}")
PY
```

- [ ] Aim for these proportions without padding: Before You Begin 200-250; Part I 950-1,100; Part II 450-600; Rules at a Glance 220-280. Record and justify any small departure in the task report.

- [ ] Search player-facing prose for banned jargon and inspect every rhetorical negation rather than mechanically deleting it:

```bash
rg -n -i 'authored|captured target|capture the target|resolution-inert|\bterminal\b|\bslice\b|state and effect|resolve E0[0-9]' stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
rg -n -i '\bnot\b|not only|not just|rather than' stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
```

- [ ] Read the complete rules document aloud once. Check that Conan's age and quotation are contextualised, the roll-low convention is unmistakable, the worked arithmetic is correct, each sheet field has a lifecycle, and the reader encounters no unexplained designer language.

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
git diff --check
```

### Step 6: Commit Task 2

- [ ] Commit the Tower module and quick-reference rewrite:

```bash
git add stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
git commit -m "docs: rewrite the Tower adventure module"
```

---

## Task 3: Align the sheet and internal Exposure source

**Files:**

- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md`

### Step 1: Make the Adventure Sheet self-explanatory

- [ ] Keep the existing two-page grammar, fixed profile, boxes, and writable space.

- [ ] Adjust only the short instructions needed to match the rewritten primer. Identify the Sword as a starting possession; explain that passages award later possessions and story marks; tell the reader when to write or cross them off; and define Exposure in plain words beside the track before its starting value is used.

- [ ] Keep Exposure 0 unmistakable as the starting value. Keep the threshold reminders accurate and compact: hidden at 0-2, unease at 3, search at 4, discovery at 5. Do not imply automatic choice removal at 3 or 4.

- [ ] Keep the instructional prose near the specification's roughly 100-word allocation and preserve practical writing room.

### Step 2: Repair the stale Exposure rule at its source

- [ ] In `adaptation/story-profile.md`, change the Exposure 3 and 4 descriptions so they describe unease and search urgency without universally closing choices.

- [ ] Inspect the rest of the profile for any second statement of that stale restriction and correct only direct contradictions. Preserve internal designer terminology, passage codes, graph edges, encounter details, and every other settled adaptation decision.

### Step 3: Verify protected story and software boundaries

- [ ] Confirm the pre-S01 links still resolve in rules-then-sheet order and the numbered story bytes are unchanged:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
```

- [ ] Independently print the protected digest:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import hashlib
from pathlib import Path

path = Path("stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md")
payload = path.read_bytes()
marker = "## S01 — The Outer Wall".encode("utf-8")
assert payload.count(marker) == 1
digest = hashlib.sha256(payload[payload.index(marker):]).hexdigest()
print(digest)
assert digest == "2f4926bbc3fef29a3db0d6aa4087c0d6a3c33f322f5b41896333ccb3bafc8496"
PY
```

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

### Step 4: Commit Task 3

- [ ] Commit the aligned reader aid and source correction:

```bash
git add stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md
git commit -m "docs: align the Tower sheet and Exposure guidance"
```

---

## Task 4: Prepare the third live primer calibration

**Files:**

- Modify: `docs/playtesting/live-playtest.md`

### Step 1: Retire the old launch path without deleting its evidence

- [ ] State that `tower-calibration-02` remains the paused record of the rejected presentation and cannot be resumed after the reader-file hashes change.

- [ ] Change active start, lookup, note, show, pause, resume, and finish examples to the fresh session ID `tower-calibration-03`. Retain references to `tower-calibration-02` only where the document explains its preserved historical status.

- [ ] Use a purpose and hypothesis centred on the reader-first primer: a new reader can enter the story after learning the rules through warm, concrete explanation and examples, without prior knowledge of Howard, gamebooks, or *Sinew & Steel*.

### Step 2: Encode the small-chunk review protocol

- [ ] Keep the four H2 lookups in their approved order. Explain that lookup records the source section while the facilitator presents no more than one or two H3 subsections to the reader at a time.

- [ ] Require the facilitator to pause after each chunk, record the reader's first reaction before explaining anything, answer only what the reader has actually reached, and continue when the reader is ready.

- [ ] Present the Adventure Sheet after Rules at a Glance. Keep S01 hidden until every primer part and the sheet have been reviewed and the reader explicitly says they are ready.

- [ ] Do not change `tools/live_playtest.py` or start a session. This task changes operating instructions only.

### Step 3: Verify the documented protocol

- [ ] Inspect every calibration identifier and confirm that executable examples use `tower-calibration-03`:

```bash
rg -n 'tower-calibration-0[123]' docs/playtesting/live-playtest.md
```

- [ ] Confirm the harness still exposes the required lookup surface:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_player_primer -v
```

- [ ] Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python 3.10 python -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

### Step 4: Commit Task 4

- [ ] Commit the calibration handoff:

```bash
git add docs/playtesting/live-playtest.md
git commit -m "docs: prepare the third primer calibration"
```

---

## Final acceptance gate

After all four tasks have passed their task-scoped reviews, the controller must request one independent whole-branch review and apply at most one focused fix wave under the subagent-driven-development workflow.

The final reviewer must verify:

- every invariant in the approved specification is present and accurate;
- teaching order, second-person voice, term-before-use, and the complete worked arithmetic;
- correct treatment of Conan's approximate age and the Nemedian Chronicles quotation;
- no premature names, encounters, creatures, tactics, passage codes, or outcomes in player-facing material;
- no banned jargon or stale automatic Exposure 3/4 restriction;
- exact H2 lookup order and pre-S01 rules-then-sheet links;
- unchanged S01-through-EOF digest and no diff in `tools/live_playtest.py`;
- no tracked `.playtest/` material;
- successful full suites on the current Python and Python 3.10; and
- a clean `git diff --check` and intended-only branch diff.

The controller must leave the feature branch unmerged and unpushed. The handoff begins the user's small-chunk primer review; `tower-calibration-03` starts only after that prose has been accepted.
