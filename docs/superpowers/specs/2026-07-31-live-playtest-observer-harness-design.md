# Live Playtest Observer Harness Design

## Status

Approved in collaborative design on 31 July 2026. This document records the
agreed design for a thin live-play observer and awaits review as a written
specification before implementation planning.

## Purpose

Create a small local Python tool that lets Barry W. Brook play the current
*Tower of the Elephant* slice live through Codex while Codex observes the
experience as it happens.

The tool supports the pen-and-paper experience rather than replacing it.
Barry makes choices, rolls physical dice, decides whether to spend Fortune,
and narrates his reactions by voice. Codex acts as a neutral operator: it
presents only the reached reader-facing material, records Barry's
voice-transcribed comments, enters the reported dice, applies the printed
authored result, and shows the updated state.

The first use is one natural calibration session. Further sessions may follow
when an earlier run gives them a stated purpose.

## Relationship to the longer-term companion

The approved solo-core architecture eventually calls for:

1. a stable machine-readable passage and state representation;
2. deterministic play and validation tools; and
3. a bounded AI facilitator.

This observer is deliberately earlier and smaller. It helps gather the live
evidence needed to design those layers well. It is not the first version of
the permanent passage schema or AI facilitator.

Markdown remains authoritative. The tool reads the current gamebook passages
and reader rules but does not encode all legal choices, authored outcomes, or
hidden conditions in a second format. Runtime choices and consequences remain
operator-controlled from the reached passage.

Reusable dice, state, logging, and reporting behaviour may inform the future
harness. No compatibility promise is made for this playtest-only command
interface or session format.

## Goals

- Let Barry and Codex conduct a fluid live playthrough in chat.
- Preserve physical dice as the default player experience.
- Display only the currently reached passage.
- Keep Codex neutral: procedural help is allowed; choice advice is not.
- Capture free think-aloud narration without interrupting every decision.
- Record choices, reported dice, Fortune decisions, state changes, rules
  lookups, transitions, timing, corrections, pauses, and session purpose.
- Validate generic roll and state operations without adjudicating authored
  fiction.
- Save and resume a session from an auditable local record.
- Generate a readable report that can support a later debrief.
- Keep raw voice-derived material local and untracked.
- Learn from one calibration session before adding features or changing the
  gamebook.

## Non-goals

This increment will not:

- choose a permanent passage or state schema;
- encode every choice and consequence from `slice-01.md`;
- infer legal intent from natural language;
- recommend a choice or play Conan on Barry's behalf;
- invent, rewrite, or extend prose;
- reveal unread passages or author-facing material;
- automatically adjudicate an authored success, failure, cost, or ending;
- replace physical dice as the live default;
- provide a player-facing terminal menu, TUI, web interface, or application;
- add a model API, provider integration, or autonomous agent;
- run probabilistic balance simulations;
- author the upper-tower continuation;
- modify rules or passages during a live session; or
- commit raw session logs or voice-transcribed feedback automatically.

## Interaction model

### Player

Barry is the player. He:

- hears or reads the reached passage;
- narrates his reactions as freely as he wishes;
- commits each choice;
- rolls physical dice when instructed;
- reports each die face;
- decides whether to spend Fortune; and
- may ask reader-facing rules questions or pause the session.

Voice input reaches Codex as transcribed text. The harness stores that text as
received. It does not retain raw audio and must not describe the record as an
audio transcript.

### Codex

Codex is a neutral observer and harness operator. It:

- presents only the current passage;
- records Barry's narration without polishing it during play;
- asks for clarification only when intent or a reported value is genuinely
  ambiguous;
- records a committed choice before resolving it;
- enters reported dice and Fortune decisions;
- applies only the consequence printed in the reached passage;
- answers spoiler-safe procedural questions from the reader-facing rules;
- shows the updated sheet and next reached passage; and
- avoids recommending, ranking, or interpreting choices for Barry.

Codex's prior knowledge of the source, graph, or unread prose cannot be erased.
The operational safeguard is behavioural: normal play commands expose only
the current passage, and Codex does not use hidden knowledge to steer play.

### Harness

The harness is an observer and deterministic calculator. It:

- extracts a requested passage from the Markdown file;
- maintains the session's current passage and recorded state;
- validates and resolves reported dice mechanically;
- records operator-entered authored changes and transitions;
- rejects invalid values before mutation;
- persists events and a current-state cache;
- detects content drift; and
- renders a readable report.

The harness does not decide what a passage means. A destination's existence
and appearance in the current passage are sanity checks, not proof that every
condition for that transition was satisfied.

## Live-session flow

### 1. Start

The operator starts a session with:

- a unique local session identifier;
- the passage, quick-rules, and adventure-sheet paths;
- hashes of those three reader-facing files;
- starting passage `S01`;
- Conan's initial attributes and resources;
- starting possessions and story marks;
- physical-dice mode;
- neutral-observer mode;
- a plain-language session purpose; and
- an optional hypothesis for a targeted repeat.

The first session purpose is a natural calibration playthrough. It has no
target route.

### 2. Present

The harness displays only the current passage. Codex presents that reached
material to Barry and records a `passage_shown` event.

### 3. Observe

Barry may narrate impressions, uncertainty, expectations, or rules questions
by voice. Codex records the transcribed text as `player_note` or
`rules_question` events.

There is no compulsory reason or confidence question at each choice. Event
timestamps preserve the interaction interval between passage display and
choice commitment, but the report must not treat network, transcription, or
tool latency as a precise measure of cognitive hesitation.

### 4. Commit

Barry commits a choice. Codex records the choice text, any named method, and
the intended destination or test before dice are entered.

If Barry's statement could map to more than one printed option, Codex asks a
neutral clarification. It does not infer a preferred option.

### 5. Resolve

For a direct choice, Codex applies any printed state change and records the
transition.

For a test:

1. the operator captures the attribute target and roll mode from the reached
   passage;
2. Barry rolls one or two physical d20s and reports every face;
3. the harness validates the values and selects the die required by standard,
   Advantage, or Disadvantage mode;
4. the harness identifies a locked selected natural 1 or natural 20;
5. for an ordinary selected die, it calculates the provisional margin;
6. Barry decides whether to spend Fortune when the passage permits it;
7. the harness validates the spend, lowers the selected die, and recalculates
   the final margin; and
8. Codex applies the printed authored result and records the transition.

The harness may also generate auditable dice for automated tests and later
replay work. Generated dice are not the default for the live calibration
session.

### 6. Continue, pause, or correct

After every resolved action, Codex shows the complete current sheet and the
next passage.

Barry may pause at any point. Resume requires the same reader-file hashes and
reconstructs the state from the local session record.

A genuine operator or transcription error may be corrected. The original
event remains in the append-only log and a compensating `correction` event
records what changed and why. A correction is not permission to rewind an
unfavourable choice or roll.

### 7. Finish and debrief

At an ending or the `S14` slice boundary, the operator closes the session and
generates a report containing:

- session purpose and limitations;
- route and passage timestamps;
- player narration;
- choices and methods;
- raw and selected dice;
- margins and Fortune decisions;
- state before and after each change;
- rules questions and lookups;
- corrections and pauses;
- final state or ending; and
- observed ambiguities or operator notes.

Barry and Codex then debrief in conversation. No gamebook change is made or
committed automatically. Any curated evidence summary, additional session, or
revision becomes a separately approved action.

## Tracked components

Implementation will add:

- `tools/live_playtest.py` — the Python 3.10+ standard-library operator CLI;
- `tests/test_live_playtest.py` — deterministic unit and session tests;
- `docs/playtesting/live-playtest.md` — operating and evidence protocol; and
- a `.gitignore` entry for `.playtest/`.

The implementation uses a local Python 3.10 or newer interpreter and no
third-party runtime dependency. It does not add a package manifest,
application framework, database, network service, or model integration.

## Command surface

The CLI is command-oriented rather than a player-facing interactive menu.
Each invocation reads the named session, validates one operation, records it,
and exits with a clear result.

The command surface will cover:

- `start` — create a session with reader files, starting state, and purpose;
- `show` — display the current passage only;
- `state` — display the complete recorded sheet;
- `note` — append voice-transcribed player commentary;
- `lookup` — record and display a reader-rules section;
- `choose` — record a committed direct choice or tactical method;
- `roll` — accept physical dice and resolve die selection and natural locks;
- `fortune` — record and validate a post-roll Fortune decision;
- `apply` — apply an explicitly authored resource, possession, or mark change;
- `goto` — record a validated passage transition;
- `correct` — append a compensating correction with a reason;
- `recover-cache` — explicitly rebuild a stale state cache from the
  authoritative event log after an interrupted write;
- `pause` and `resume` — close and reopen an unfinished session;
- `finish` — record the ending or slice-complete state; and
- `report` — regenerate the readable session report.

Exact option spelling belongs in the implementation plan. These operations are
the required behavioural contract.

## Session storage

Raw runtime material lives below:

```text
.playtest/sessions/<session-id>/
```

Each session contains:

```text
session.json
events.jsonl
report.md
```

### `session.json`

Stores:

- format and harness version;
- session identifier and purpose;
- reader-file paths and hashes;
- dice and observer modes;
- initial state;
- current passage;
- cached current state;
- lifecycle status; and
- creation and update timestamps.

### `events.jsonl`

Is the append-only evidential record. Every line has:

- a monotonic event number;
- event type;
- wall-clock timestamp;
- current passage;
- operation-specific data;
- relevant state before and after; and
- operator reason where required.

The event log is authoritative for audit. `session.json` is an atomic
current-state cache. On resume, the harness checks that replaying events
reproduces the cached state. A mismatch stops with a diagnostic; it is not
silently repaired. The operator may then run `recover-cache`, which rebuilds
only the derived cache from the unchanged event log before play resumes.

### `report.md`

Is derived from the event log. Regeneration must produce the same substantive
route, rolls, state history, narration, and final result.

## State model

The observer tracks only the current reader sheet:

- named attributes and their values;
- current and maximum Fortune;
- current and maximum Stamina;
- Pressure name, current value, and maximum value;
- possessions;
- story marks; and
- current passage and lifecycle status.

It does not encode enemies, authored outcome tables, hidden story flags,
source-map annotations, or unreached choices.

Resource changes require an explicit amount and reason. Possession and mark
changes require an explicit add, consume, or remove operation. The harness
rejects:

- d20 faces outside 1-20;
- the wrong number of dice for the selected roll mode;
- Fortune expenditure on a locked selected natural;
- Fortune spending above the recorded current value;
- Stamina, Fortune, or Pressure outside their recorded bounds;
- consuming an absent possession or mark;
- duplicate additions unless explicitly permitted;
- transitions to undefined passage identifiers;
- mutation after a finished session; and
- resumption after reader-file hash drift.

## Passage and rules extraction

The passage reader indexes headings of the form:

```markdown
## S01 — The Outer Wall
```

or:

```markdown
## E01 — The Theft Abandoned
```

`show` returns the current heading and its body up to the next passage
heading. It does not dump the whole story file or list unreached prose.

The rules reader indexes `##` sections in `quick-rules.md`. A logged rules
lookup can display a named reader-facing section without consulting the
author-facing story profile.

The extractor validates duplicate identifiers and missing current passages at
session start. It does not attempt to parse Markdown prose into a permanent
choice schema.

## Integrity and error handling

Every mutating command follows this order:

1. read the session and event log;
2. verify reader-file hashes and cached-state consistency;
3. validate the requested operation completely;
4. construct the event and resulting state;
5. append the event;
6. atomically replace the state cache; and
7. return the event and complete current state.

If a command fails validation, it changes neither file.

Errors name the invalid value, current passage or state, and permitted next
action. The tool never guesses an intended die, Fortune spend, state change,
or destination.

## Evidence and privacy boundary

`.playtest/` is ignored by Git. Raw voice-transcribed comments, local timing,
and complete session reports remain there by default.

The live transcript is human playtest evidence but not:

- retained raw audio;
- a controlled experiment;
- a blind session for Codex;
- proof of how an unfamiliar reader would respond; or
- authority to generalise from one player.

Barry may later approve a curated summary for the tracked audit. The summary
must preserve material criticism and limitations while omitting raw comments
that Barry does not want published.

## Testing

The standard-library test suite will cover:

- passage and rules-section extraction;
- duplicate and missing identifiers;
- current-passage-only display;
- session creation and initial state;
- standard, Advantage, and Disadvantage die selection;
- selected natural 1 and natural 20;
- ordinary margin calculation;
- permitted and forbidden Fortune spending;
- Fortune, Stamina, and Pressure bounds;
- possession and mark addition and consumption;
- direct choices and passage transitions;
- invalid operations leaving state and log unchanged;
- pause and resume equivalence;
- interrupted-write detection and explicit cache recovery;
- content-hash drift refusal;
- compensating corrections retaining prior events;
- event ordering and state replay;
- deterministic report regeneration; and
- finished-session immutability.

An integration smoke replay will reproduce the existing reader-only route:

- start at `S01` with Fortune 10, Stamina 6, Exposure 0, and Sword;
- climb, examine, take the guard's spear, and stalk Taurus;
- report 15 against CUN 12 and spend 3 Fortune;
- accept Taurus and reach the silent lion;
- report Advantage dice 6 and 20, selecting 6;
- consume the spear; and
- finish at `S14` with Fortune 7, Stamina 6, Exposure 0, Sword retained,
  spear consumed, and no story marks.

## Implementation and calibration sequence

1. Implement passage/rules extraction and session persistence.
2. Implement state, roll, Fortune, correction, and transition operations.
3. Implement report generation and command help.
4. Add the standard-library tests and smoke replay.
5. Document the neutral-observer operating protocol.
6. Verify the repository and commit the tool increment.
7. Start one natural live calibration session with Barry using physical dice
   and free think-aloud narration.
8. Generate the local report and debrief together.
9. Stop for approval before committing a playtest summary, modifying the
   gamebook, running targeted repeats, or designing the permanent schema.

## Acceptance criteria

The increment is complete when:

1. the CLI uses only the Python standard library and runs locally;
2. `.playtest/` is ignored and no raw session data is tracked;
3. the extractor displays one current passage and named reader-rules sections;
4. invalid dice, Fortune, state, possession, mark, and destination operations
   fail before mutation;
5. physical standard, Advantage, and Disadvantage rolls resolve correctly;
6. selected natural results and post-roll Fortune follow the solo-core rules;
7. event replay reproduces the cached state after every tested operation;
8. pause/resume and report regeneration are deterministic;
9. the existing `7/6/0`, spear-consumed smoke route passes;
10. all automated tests and repository checks pass;
11. one live natural calibration session is completed with Barry as player,
    Codex neutral, physical dice, and free think-aloud narration;
12. the local report records route, comments, rolls, decisions, state, rules
    lookups, corrections, timing, and limitations; and
13. the increment stops for review without silently changing passages, rules,
    or the future companion architecture.

## Deliberate deferrals

Later approved increments may decide:

- the permanent machine-readable passage/state representation;
- full legal-choice and authored-outcome validation;
- agent-callable deterministic operations;
- seeded simulations and route analysis;
- a bounded conversational AI facilitator;
- player-facing terminal, web, or application interfaces;
- durable cross-story saves; and
- publication of curated human playtest evidence.

The calibration session informs those decisions; it does not prejudge them.
