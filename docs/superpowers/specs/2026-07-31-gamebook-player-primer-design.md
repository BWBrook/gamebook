# Gamebook Player Primer Design

**Date:** 2026-07-31

**Status:** Approved for implementation

**First title:** Robert E. Howard's *The Tower of the Elephant*

## Purpose

Every published gamebook must teach its own rules. A reader needs no prior
knowledge of *Sinew & Steel*, tabletop role-playing games, or another gamebook
series.

This requirement emerged from the first live Tower calibration. The reader
reached S01, saw a choice that added Exposure, and immediately needed to know
what Exposure meant and what its consequences were. The session stopped before
the reader made a choice. That was a successful diagnostic result: the book
needs a deliberate onboarding sequence before the story begins.

The next increment will create that sequence as publishable front matter and
use it as the first material in a fresh live calibration.

## Design goals

The primer must:

- make the gamebook self-contained;
- take a reader from no system knowledge to confident entry into S01;
- explain every term before the story uses it;
- teach through one concrete, non-canonical worked example featuring the
  current book's protagonist;
- separate the reusable system core from rules specific to one adventure;
- serve as both tutorial and complete rules reference;
- end with a compact lookup spread and a writable Adventure Sheet;
- use plain, modern instructional prose;
- carry atmosphere through the worked example and story-specific orientation;
- remain portable across genres, protagonists, and public-domain sources; and
- stay compact enough to preserve anticipation for the story.

## Non-goals

This increment will not:

- change passage outcomes or the approved Tower mechanics;
- require the full *Sinew & Steel* rules;
- duplicate wording, layouts, tables, or distinctive expression from an
  existing proprietary gamebook system;
- create a Markdown include system, template engine, or publishing stack;
- extract a generic rules file before a second adaptation provides real reuse
  evidence;
- build a new primer parser or rules engine into the thin harness; or
- complete rules for the unwritten upper portion of the Tower adaptation.

## Reader contract

The book contains everything required to play. A reader needs:

- the gamebook;
- its Adventure Sheet;
- a pen or pencil;
- one twenty-sided die; and
- optionally, a second d20 for convenient Advantage and Disadvantage rolls.

The opening explicitly states that character creation is unnecessary and that
the book supplies the protagonist's profile and starting state.

The first reference to *Sinew & Steel* will be brief and non-dependent:

> These gamebook rules are adapted from *Sinew & Steel*, a d20 tabletop
> role-playing game by Barry W. Brook. You need no knowledge of that system;
> everything required to play appears here.

## Front-matter sequence

The reader encounters five components in this order:

1. **Before You Begin**
2. **Part I: How to Play**
3. **Part II: Rules for This Adventure**
4. **Rules at a Glance**
5. **Adventure Sheet**

S01 follows the facing Adventure Sheet spread.

The digital facilitator follows the same sequence. It does not jump directly
to the first numbered passage.

## Length and allocation

The editorial target is approximately 1,800–2,000 reader-facing words across
the primer, Rules at a Glance, and sheet instructions. Writable blank space is
excluded.

| Component | Target |
| --- | ---: |
| Before You Begin | 100–150 words |
| Part I: How to Play | 850–950 words |
| Part II: Rules for This Adventure | 450–550 words |
| Rules at a Glance | 250–300 words |
| Adventure Sheet labels and instructions | approximately 100 words |

These are editorial allocations rather than independent quotas. The complete
sequence matters more than forcing each section to an exact count.

## Part I: How to Play

Part I teaches the reusable system in the order a reader uses it:

1. understand the Adventure Sheet;
2. read a passage and its available choices;
3. record immediate printed changes;
4. read the stakes before a consequential test;
5. choose a method;
6. capture the named target;
7. roll and select the die;
8. check for a selected natural result;
9. calculate margin;
10. decide whether to spend Fortune;
11. apply the authored result;
12. update the sheet; and
13. turn to the printed destination.

Its content covers:

- attributes and their use;
- d20 roll-under resolution;
- Advantage and Disadvantage;
- selected natural 1 and natural 20 results;
- margin;
- Fortune as both a spendable reserve and, when printed, a test target;
- Stamina;
- possessions;
- semantic story marks;
- authored tactical exchanges; and
- explicit terminal outcomes.

The primer states that margin has no additional effect unless the current
passage explicitly reads it. It also explains that withdrawal, escape, or
evasion from a tactical exchange is available only when the passage offers
that authored option.

### Teaching pattern

Each concept follows the same compact pattern:

1. **Purpose:** what the rule represents.
2. **Procedure:** exactly what the reader does.
3. **Example:** one concrete application.
4. **Record:** what changes on the Adventure Sheet.

Rules prose uses plain modern English. Flavour belongs in the worked example,
the protagonist introduction, and the adventure orientation.

## Worked Conan example

Part I contains one non-canonical Conan vignette immediately after tests and
Fortune are explained. It is a fully worked example, not a live practice roll,
and it tells the reader not to mark the real Adventure Sheet.

The example demonstrates this complete loop:

1. the passage states meaningful stakes;
2. Conan chooses a method;
3. the method captures an attribute target of 12;
4. the selected ordinary d20 result is 15;
5. the provisional margin is `12 - 15 = -3`;
6. the reader spends 3 Fortune;
7. the final result becomes 12 and the final margin becomes 0;
8. Conan succeeds;
9. Fortune changes from 10 to 7; and
10. the reader follows the authored successful outcome.

A short contrast explains that a selected natural 20 is locked and cannot be
changed with Fortune.

The vignette uses Tower-appropriate atmosphere without reproducing an actual
passage, revealing an unread event, or creating a route that the real story
must honour. Future titles replace the vignette while retaining its teaching
function.

## Part II: Rules for This Adventure

Part II is the title-specific module. For the current Tower slice it includes:

- Conan's fixed profile;
- his starting Fortune, Stamina, possessions, and story marks;
- any aliases or presentation labels used for the four attributes;
- Exposure and its full 0–5 scale;
- the consequence at each material Exposure threshold;
- the events that can raise Exposure;
- recovery availability within the current playable material;
- Tower-specific tactical reminders;
- crisis ordering and explicit endings; and
- concise hints for practical play; and
- **Rumours of the Tower**, a short atmospheric orientation.

The Exposure explanation precedes every actionable reference to Exposure. A
small example shows Exposure moving from 2 to 3, the player marking the new
value, the watch becoming uneasy, and lingering choices beginning to close.

The module states only rules supported by the playable material. It expands as
the full adaptation develops.

### Hints for play

The hints remind the reader to read every available method and its stakes,
keep the current passage marked, apply printed state changes immediately,
check conditions before selecting an option, and trust explicit terminal
instructions. They do not reveal an optimal route or advise particular story
choices.

## Rules at a Glance

Rules at a Glance is a facing spread and a lookup aid. It does not become a
second rules chapter.

### Left page: reusable action flow

The left page presents the resolution sequence:

1. read the stakes;
2. choose a method;
3. capture the target;
4. roll and select the die;
5. check natural 1 or natural 20;
6. compute `target - selected die`;
7. optionally spend Fortune;
8. apply the printed result; and
9. update the sheet before turning.

It also gives one-line reminders for Advantage and Disadvantage.

### Right page: adventure module

The Tower page summarises:

- Fortune timing and cost;
- Fortune tests using the captured current Fortune target;
- Stamina loss and the 0-Stamina instruction;
- Exposure thresholds;
- possessions and story marks;
- tactical exchanges; and
- the order for resolving crisis conditions before following a destination.

Future titles retain the left-page grammar and replace the right-page
reminders.

## Adventure Sheet

The Adventure Sheet is a facing two-page spread immediately before S01.

### Left page: reusable character and resources

The left page contains:

- protagonist name;
- the four attributes and current title-facing labels;
- fixed attribute values;
- the Fortune track;
- the Stamina track; and
- concise marking instructions.

### Right page: adventure state

The Tower page contains:

- the Exposure track and compact threshold cues;
- possessions, with starting equipment printed;
- story marks; and
- a small notes area.

The two-page grammar remains stable while either page can be adjusted when a
future title has materially different needs.

## Portability contract

The stable system is a semantic contract, not a demand that every book use
identical surface vocabulary.

The portable core contains:

- authored passage choices and consequences;
- four broad capability axes;
- d20 roll-under tests;
- Advantage and Disadvantage;
- selected natural results;
- Fortune and Stamina;
- possessions and semantic story marks; and
- authored tactical exchanges.

The four capability axes retain their underlying meanings. A title may publish
one-to-one synonyms appropriate to its setting, as *Sinew & Steel* skins do.
The primer, Adventure Sheet, passages, Rules at a Glance, and facilitator must
use the selected labels consistently. A synonym changes presentation, not the
capability's mechanical scope, unless the adventure module explicitly declares
a tested variant.

Each title supplies:

- its protagonist and fixed profile;
- title-facing capability labels;
- starting resources and possessions;
- its worked example;
- recovery availability;
- title-specific hazards and procedures;
- rumours and setting orientation;
- sheet customisation; and
- an optional named story track.

A story track such as Exposure is not universally required. A title uses at
most one primary story track, and only when later passages materially consume
its states. Another adaptation might use pursuit, cohesion, suspicion,
temporal instability, or no story track.

This contract must accommodate historical adventure, sword and sorcery,
weird fiction, scientific romance, and other suitable adaptations without
forcing Tower-specific concerns into them.

## Source of truth

For this first implementation:

- `quick-rules.md` becomes the complete Tower primer and Rules at a Glance;
- `adventure-sheet.md` remains the separate writable spread;
- the story opening points to both in the approved order; and
- the live-playtest protocol makes completion of the primer sequence a
  prerequisite for showing S01.

Part I is written as the stable core, with clear boundaries around replaceable
title content. One authoritative Tower rules document avoids premature
templating and duplicated rule sources.

When a second gamebook enters development, the project will compare its real
needs with Tower's Part I. That is the appropriate point to extract a shared
source or introduce an assembly mechanism.

## Live primer calibration

The existing `tower-calibration-01` session remains a local diagnostic record.
It ended before the first choice with the outcome that a self-contained primer
was required. Its report remains local and untracked.

After the primer implementation and review, the project starts
`tower-calibration-02` with this hypothesis:

> A reader with no knowledge of Sinew & Steel can prepare the Adventure Sheet,
> understand the routine play loop and Tower-specific state, and enter S01
> without external explanation.

The facilitator presents:

1. Before You Begin and How to Play;
2. the worked Conan example;
3. Rules for This Adventure and Rumours;
4. Rules at a Glance;
5. the Adventure Sheet; and
6. S01 after the reader says they are ready.

The reader may react freely throughout. The facilitator records confusion
before answering it, and any procedural answer must be grounded in the primer.
No outside *Sinew & Steel* knowledge fills a gap silently.

The calibration assesses:

- whether every term is introduced before use;
- whether the worked example can be followed without assistance;
- whether the sheet is easy to prepare and update;
- whether Exposure and its implications are understood;
- whether Rules at a Glance supports rapid lookup;
- whether the front matter feels proportionate; and
- whether the reader can enter S01 without an unresolved procedural question.

Because the first reader has now encountered Exposure and S01, the second
session tests clarity and usability rather than complete blindness. Later
testing should include readers unfamiliar with both *Sinew & Steel* and the
Tower slice.

## Implementation scope

The expected tracked work is limited to:

- the Tower quick rules;
- the Tower Adventure Sheet;
- the pre-passage reading instruction in the Tower slice;
- the live-playtest operating protocol; and
- focused tests for the reader-material contract.

The implementation should verify:

- required headings and their order;
- the editorial word envelope;
- the worked example's arithmetic and Fortune update;
- complete Exposure thresholds;
- consistent attribute terminology;
- primer and sheet links before S01;
- Rules at a Glance content;
- unchanged numbered passage prose and edges;
- unchanged harness mechanics; and
- continued Python 3.10 compatibility for the repository test suite.

Changing the rules and sheet will intentionally change their reader hashes.
The completed first calibration remains represented by its generated report.
The fresh second session records the revised files and their new hashes.

## Originality guardrail

Classic gamebooks establish the reader expectation of self-contained rules,
play advice, and a writable record sheet. This design adopts those functions.
Its instructional sequence, terminology, d20 mechanics, worked-example method,
modular adventure layer, story state, spreads, and prose will be original to
this project.

## Acceptance criteria

The design is implemented successfully when:

- a reader can begin without prior *Sinew & Steel* knowledge;
- the complete front matter follows the approved five-part order;
- combined reader-facing guidance remains near the 1,800–2,000-word target;
- the routine resolution loop can be reconstructed from the worked example;
- all Tower-specific state is defined before S01;
- Rules at a Glance and the Adventure Sheet use the selected modular layouts;
- all terminology is internally consistent;
- numbered passage content and route logic remain unchanged;
- the repository tests pass on the installed Python and Python 3.10; and
- a new live calibration begins with the primer rather than S01.
