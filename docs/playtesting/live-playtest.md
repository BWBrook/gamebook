# Live Playtest Observer

## Purpose

Use this local, preliminary harness to record a live physical-dice playthrough
of the current *Tower of the Elephant* slice. It preserves the reached route,
reported dice faces, printed consequences, and final sheet state for later
review; it is not a replacement gamebook or permanent companion tool.

## What the tool does

The tool starts a session against the three authoritative reader files, hashes
them, shows only the reached passage, records explicit choices and physical
d20 faces, applies explicitly supplied authored changes, maintains a local
event chain and state cache, and renders a report from that evidence.

## What the tool deliberately does not do

It does not roll dice, recommend or rank choices, infer legal choices or
authored outcomes from prose, alter passages or rules, reveal unread passages,
adjudicate the fiction, run balance simulations, retain raw audio, or create a
curated publication record.

## Requirements

Run commands from the repository root with Python 3.10 or later. Have the
current three Tower reader files, the paper adventure sheet, a pen, and one or
two physical d20s available. The default session location is
`.playtest/sessions`, which is local and Git-ignored.

## Start a Tower session

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

For a repeat session, use a new session ID and a written `--purpose` or
`--hypothesis` that states the question being revisited.

## Live operating sequence

```text
show -> free narration and rules activity -> choose -> optional pre-roll apply
-> physical roll -> ordinary Fortune decision or locked natural
-> authored apply commands -> goto -> complete state -> next show
```

Use `show` before reading the reached passage. Record free narration with
`note`, and retrieve a reader-facing rules section with `lookup` when needed.
Commit the selected choice before a roll or transition. If printed preparation
consumes an item, use `apply` before recording the physical roll. Enter only
the faces Barry reports; for an ordinary selected die, record the Fortune
decision (including zero) before `goto`. Apply only the printed consequences,
then inspect `state` before continuing.

## Command reference

All commands accept `--sessions-dir PATH` before the command when a nondefault
local session directory is required.

```text
python3 tools/live_playtest.py show SESSION_ID
python3 tools/live_playtest.py state SESSION_ID
python3 tools/live_playtest.py note SESSION_ID --kind player|operator|rules-question --text TEXT
python3 tools/live_playtest.py lookup SESSION_ID --section HEADING
python3 tools/live_playtest.py choose SESSION_ID --text TEXT [--method TEXT] [--destination S01]
python3 tools/live_playtest.py roll SESSION_ID --attribute NAME --mode standard|advantage|disadvantage --die FACE [--die FACE]
python3 tools/live_playtest.py fortune SESSION_ID --spend INTEGER
python3 tools/live_playtest.py apply resource SESSION_ID NAME --delta INTEGER --reason TEXT
python3 tools/live_playtest.py apply pressure SESSION_ID --delta INTEGER --reason TEXT
python3 tools/live_playtest.py apply possession SESSION_ID add|consume|remove NAME --reason TEXT
python3 tools/live_playtest.py apply mark SESSION_ID add|consume|remove NAME --reason TEXT
python3 tools/live_playtest.py goto SESSION_ID PASSAGE_ID
python3 tools/live_playtest.py correct SESSION_ID --target-event INTEGER --reason TEXT CORRECTION
python3 tools/live_playtest.py recover-cache SESSION_ID
python3 tools/live_playtest.py pause SESSION_ID --reason TEXT
python3 tools/live_playtest.py resume SESSION_ID
python3 tools/live_playtest.py finish SESSION_ID --outcome TEXT
python3 tools/live_playtest.py report SESSION_ID
```

Use `python3 tools/live_playtest.py --help` for the complete correction forms
and option spelling. `apply` records a result already printed by the reached
passage; it is not an instruction for Codex to invent a result.

## Neutral-observer protocol

Codex may answer reader-facing procedure questions from the reached passage
and rules. It must not recommend or rank choices. It enters only Barry's
reported physical faces and applies only printed results. If an utterance maps
to multiple printed options, it asks one neutral clarification; it does not
suggest which option to take. No passage or rule edits occur during play.

## Voice-derived notes

Use `note --kind player` for voice-derived text and preserve it as received.
Use `operator` for a factual observation and `rules-question` for a question.
The harness retains text, not raw audio; do not present a transcript as an
audio recording.

## Corrections

Do not rewrite the event log. If an entry was mistaken or a statement needs
clarification, use `correct` with the target event, a reason, and exactly one
compensating correction. Check `state` afterward and retain the original event
as part of the evidence.

## Pause and resume

Use `pause` with a factual reason before an interruption. On return, use
`resume`; it reloads the session and verifies the reader hashes before a new
event can be recorded. A finished session is read-only apart from `state` and
`report`.

## Cache recovery

`recover-cache` repairs only a stale derived cache. It is appropriate only
when the authoritative event chain and all three reader hashes are intact. If
either check fails, preserve the material and investigate rather than forcing
recovery.

## Finish and report

At the printed terminal or slice-complete point, use `finish` with the
authored outcome, then use `report`. The Markdown report is derived from the
event chain and can be regenerated without changing that chain.

## Evidence and privacy

The event log, cache, voice-derived notes, timings, and reports stay local
under `.playtest/` and are ignored by Git. Do not add them to Git. A future
curated summary requires Barry's explicit approval. The report records hashes
of the reader files so a session can be tied to the exact material it used.

## Calibration checklist

- Start with a written purpose or hypothesis and the current reader files.
- Confirm the session starts at S01 with Conan's fixed attributes, Fortune
  10/10, Stamina 6/6, Exposure 0/5, and Sword.
- At every test, show the reached passage, commit the choice, enter Barry's
  physical faces, and record the Fortune decision before a transition.
- Apply possession, story-mark, Stamina, and Exposure changes only where the
  reached text prints them; consume a required item before its roll.
- Inspect the complete state after each passage and generate a report at the
  slice end.
- Retain the local evidence; seek explicit approval before extracting any
  curated summary.

## Known limitations

This calibration route demonstrates only mechanics reached by that route. It
does not establish slice coverage for Disadvantage, WIL tests, Fortune tests,
recovery, margin-specific branches, or Stamina zero, because the audited route
does not encounter them. The observer is not blind to the reader files, timing
includes local interaction and transcription delay, and one player/session is
not a controlled or generalisable study.
