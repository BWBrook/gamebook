# Reader-first player primer rewrite design

**Date:** 2026-08-01

**Status:** Approved for implementation

**First title:** Robert E. Howard's *The Tower of the Elephant*

**Supersedes:** The presentation and teaching-order requirements in
`2026-07-31-gamebook-player-primer-design.md`. The settled game mechanics,
portable core, title-module boundary, Adventure Sheet structure, and protected
story boundary remain in force.

## Purpose

The first primer calibration showed that the rules contain the right material
in the wrong voice. They read like a compact specification for designers and
testers. A new reader needs a welcome, a sense of the adventure ahead, and a
patient explanation of each rule at the moment it becomes useful.

This rewrite will teach the same *Sinew & Steel* gamebook system from the
reader's side of the table. It will assume that the reader has never played a
gamebook, has never read Robert E. Howard, and knows nothing about *Sinew &
Steel*. Familiarity with other role-playing games may create one particular
source of confusion: many popular systems reward high rolls, while this system
uses roll-under tests and therefore favours low rolls.

The resulting primer should be clear to a capable reader of about twelve while
remaining lively and satisfying for an adult. Clarity must never become
condescension.

## Evidence from `tower-calibration-02`

The live reader identified a connected set of presentation failures:

- Conan appeared before the book had introduced him or the story.
- Internal terms such as `captured target`, `resolution-inert`, `authored`,
  `terminal`, and `slice` reached the player;
- the rules mentioned Fortune before teaching it and introduced other concepts
  in dependency-breaking order;
- the worked example watched a third-person player perform arithmetic instead
  of guiding `you` through an adventure;
- the explanation assumed knowledge of how possessions and story marks enter
  play;
- the Tower module exposed future names, encounters, and passage codes before
  those references meant anything;
- the Exposure table resembled program state rather than a danger gathering in
  the fiction;
- repeated negation, repeated sentence patterns, and conspicuously common AI
  vocabulary made the voice feel synthetic; and
- presenting a whole rules part at once made careful reader feedback harder.

The session is paused before the story. Its event log is useful evidence and
must remain local and unchanged. Rewriting the reader files will invalidate its
recorded hashes, so the rewritten primer will receive a fresh calibration
session.

## Audience

The primary reader:

- may be new to Conan, Howard, gamebooks, tabletop role-playing, or all four;
- wants to begin an adventure rather than study a system;
- can follow arithmetic once its purpose is concrete;
- needs every term introduced before it appears in an instruction;
- should understand what to write on the Adventure Sheet and why;
- should see rules demonstrated through situations before relying on the
  reference spread; and
- should reach the first passage with anticipation intact.

Existing Howard readers remain an important audience. Source fidelity,
atmosphere, and the character of Conan should reward their knowledge without
making it a prerequisite.

## Approaches considered

### 1. Correct the existing reference-first primer

This approach would replace the most opaque terms, move a few subsections, and
add a story blurb. It would be quick, but the current taxonomy and cadence would
still govern the result. The live feedback shows that the structure itself is
the problem.

### 2. Build a reader-first guided primer

This approach begins with the series, the story, and Conan. It teaches rules in
the order a reader uses them, speaks directly to `you`, and returns repeatedly
to concrete examples and the Adventure Sheet. A compact reference follows the
tutorial.

This is the approved approach.

### 3. Teach the rules inside the opening story passages

An in-fiction tutorial could feel immediate, but it would burden the adaptation
with compulsory instructional scenes, disturb the source-derived passage graph,
and make later books repeat tutorial logic inside their stories. It would also
blur the boundary between an example and canonical play.

## Reader journey

The five-part front-matter sequence remains:

1. **Before You Begin**
2. **Part I: How to Play**
3. **Part II: Rules for This Adventure**
4. **Rules at a Glance**
5. **Adventure Sheet**

The function of each part is sharper:

- **Before You Begin** invites the reader into the series and this story.
- **Part I** teaches the portable action grammar through direct explanation and
  examples.
- **Part II** introduces Conan's profile and the rules that belong to this
  adventure.
- **Rules at a Glance** refreshes rules the reader has already learned.
- **Adventure Sheet** gives the reader a physical place for every changing
  value, possession, and remembered fact.

The story begins only after the reader has completed that journey and says they
are ready.

## Before You Begin

The opening should run to roughly 200-250 words. It has four jobs.

First, it identifies the work as part of a developing *Sinew & Steel* gamebook
series that adapts classic stories into solo adventures. This is a concise
project description, not finished marketing copy or a commitment to a final
series logo.

Second, it gives the reader a short, spoiler-light story blurb: the thief-city
of Zamora, Yara's silver tower, the fabulous Heart of the Elephant, and Conan's
decision to steal it. The paragraph should feel like the promise on a back
cover.

Third, it introduces the protagonist. Howard's story calls Conan a `tall,
strongly made youth`; in a 10 March 1936 letter to P. Schuyler Miller, Howard
placed him at `about seventeen` and described him as unusually mature for a
civilised youth of that age. The primer will use `about seventeen`, as approved,
and show that hard travel, Cimmerian upbringing, and early violence have already
made him formidable.

Howard's career-spanning description will appear once as a short attributed
line:

> a thief, a reaver, a slayer, with gigantic melancholies and gigantic mirth

The phrase comes from the Nemedian Chronicles epigraph in *The Phoenix on the
Sword*. The primer must present it as a glimpse of the man Conan will become,
not a quotation from *The Tower of the Elephant* and not a literal summary of
his experience at seventeen.

Source notes for implementation:

- the local Tower text introduces the `tall, strongly made youth` in
  [`source.md`](../../../stories/public_domain/howard/tower_of_the_elephant/source.md);
- [*The Phoenix on the Sword*, Chapter I](https://en.wikisource.org/wiki/The_Phoenix_on_the_Sword/Chapter_I)
  supplies the Nemedian Chronicles line; and
- the Howard archive reproduces the age statement from the
  [10 March 1936 Miller letter](https://reh.world/stories/the-tower-of-the-elephant/),
  which is catalogued in the
  [REH Foundation Press collected letters](https://howardworks.com/CollectedLettersofREHV3-2nd-REH_Foundation_Press.html).

Fourth, the section lists what play requires: this book, the Adventure Sheet, a
pen or pencil, one d20, and an optional second d20. It briefly identifies
*Sinew & Steel* and assures the reader that this book contains the complete
rules needed for the adventure.

## Teaching order in Part I

Part I follows the reader's real sequence of action.

Its function and mechanics are portable; its surface prose is allowed to belong
to the current book. Future titles retain the teaching order and rule meanings
while replacing Conan, the worked situations, and any title-facing synonyms.
Portability comes from a stable semantic core, not from making every primer
sound generic.

Part I refers to the number used for a test as the relevant `score`. It can say
that the Adventure Sheet holds four broad abilities, but it does not use Brawn,
Agility, Cunning, Will, or their abbreviations before Part II has introduced
those names and values.

### 1. The Adventure Sheet and numbered passages

Explain that the sheet remembers Conan's abilities, condition, equipment, and
important discoveries. Show how to read the reached passage, choose among its
available actions, follow the printed destination, and update the sheet as soon
as the book instructs.

Use `you` throughout. `You play Conan`, `you choose`, `you roll`, and `you mark
the sheet` are the normal constructions.

### 2. Tests: roll low

Introduce the core test before any modifier or resource:

- the passage tells you which ability Conan is using;
- find that ability's score on the Adventure Sheet;
- roll one d20;
- a result equal to or below that score succeeds;
- a higher result fails; and
- low rolls are therefore better.

The first numerical example should be immediate: with a score of 13, a roll of
13 or less succeeds and a roll of 14 or more fails. Terms such as `capture the
target` and `selected ordinary result` have no place in the player primer.

### 3. Margin

Margin explains how well or badly the attempt went. Subtract the die from the
attribute. A positive margin shows success; zero is success by the narrowest
amount; a negative margin shows failure. The farther the number lies from zero,
the greater the degree of success or failure.

Many passages need only the simple success or failure. Some use the margin to
create a more exact outcome. Fortune also changes the margin by lowering the
die. Examples must give the idea before presenting the arithmetic.

### 4. Fortune

Fortune is a limited reserve that lets the reader lower an ordinary roll after
seeing it. Each point spent lowers the die by one. Show the updated roll, new
margin, outcome, and remaining Fortune in one conversational example.

When a passage calls for a Fortune test, the reader writes down the current
Fortune score before rolling and uses that number for this test. Spending
Fortune after the roll can lower the die; it does not rewrite the number already
written down. The primer should teach this with a small example rather than the
phrase `current Fortune is the captured target`.

### 5. Advantage and Disadvantage

Remind the reader that low rolls are good before giving the procedure.
Advantage means rolling two d20s and using the lower. Disadvantage means rolling
two and using the higher. A one-sentence fictional example should explain why
Conan has the better or worse position.

### 6. Natural 1 and natural 20

After Advantage or Disadvantage has chosen the die to use, check that die for a
natural result. A natural 1 is the best result and a natural 20 is the worst
credible result described by the passage. Fortune changes ordinary rolls only;
a natural 1 or 20 stands as rolled. This direct explanation replaces `locked`
unless the word is first defined in equally plain language and demonstrably
helps the reader.

### 7. A complete Conan example

The worked example speaks to the reader as a friendly Custodian would across a
table. It says what you see, what the book offers, what you choose, what number
you need, what you roll, and what each mark on the sheet means.

The example remains separate from the numbered adventure. A direct instruction
does the work: `Use the figures printed in this example and leave your Adventure
Sheet unchanged.`

It must demonstrate:

- a Tower-appropriate situation that does not reproduce a real encounter;
- an attribute of 12;
- a d20 roll of 15;
- margin `12 - 15 = -3`;
- spending 3 Fortune to lower the roll to 12;
- final margin 0 and success;
- Fortune falling from 10 to 7; and
- following the successful destination printed by the imaginary passage.

A short continuation shows how a natural 20 differs, using plain language and
no rhetorical detour.

### 8. Stamina, possessions, and story marks

Stamina is Conan's capacity to keep going after injury. Passages state the loss
and tell the reader what happens at zero. Recovery occurs only where a passage
gives it; this Tower material supplies none.

The Sword is explicitly identified as Conan's starting possession. Explain the
life of a possession: a passage may give it to you, you write it down, a later
choice may require it, and the book may tell you to cross it off when used.

Story marks record something Conan has learned, done, or changed. Give a
spoiler-safe invented example, such as `Recognised the temple seal`, and show a
later choice checking that exact phrase. Explain when to write and cross off a
mark.

### 9. Tactical exchanges and endings

Explain combat through one brief situation. A passage presents several ways
Conan might meet a threat; each method can call for a different attribute,
possession, or consequence. You choose once, roll if asked, apply the result,
and continue where the book sends you.

Use familiar language for endings. Say `the adventure ends here`, `Conan dies`,
`Conan withdraws`, or `this part of the adventure is complete`. Player-facing
prose must omit `terminal`, `slice`, `authored exchange`, and implementation
language about combat loops.

## Part II: rules for this adventure

Part II applies the learned system to *The Tower of the Elephant*.

### Conan and his starting sheet

Introduce Conan as a person before displaying his profile. State his
approximate age, Cimmerian origin, physical presence, experience, outsider's
view of civilisation, and motive for entering the tower.

Then give his fixed values:

`BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6`

Vary the sentences naturally while keeping meanings precise. Brawn concerns
force and endurance. Agility governs speed and physical precision. Cunning
draws on observation, stealth, and guile. Will measures courage and
self-command.

Tell the reader exactly what to mark: four attributes, Fortune 10, Stamina 6,
the Sword under Possessions, and an empty Story Marks area. Introduce Exposure
in the following subsection before asking the reader to record its starting
value.

### Exposure

Exposure is the growing risk that Conan's intrusion will be noticed. A passage
may add Exposure when he delays, makes a disturbance, or leaves evidence. The
reader marks each increase immediately and begins at 0.

Teach the track as rising fictional danger:

- at 0-2, the night still hides Conan's intrusion;
- at 3, the watch grows uneasy;
- at 4, a search begins and later passages become more urgent; and
- at 5, the intruders are discovered and the current instruction sends the
  reader to the resulting crisis.

The main Exposure lesson must use connected prose and a small example. It must
not return to the rejected `State and effect` table form. Rules at a Glance may
use a compact threshold list or table after the reader has learned the track,
provided every label remains plain and familiar.

Exposure 3 and 4 do not remove choices automatically. The current passage
states any restriction it actually applies. The primer must not mention
Taurus, lions, patrol intervals, `E02`, or other future material while teaching
the track. Those details belong to reached passages and internal adaptation
documents.

The existing `adaptation/story-profile.md` contains stale language saying that
Exposure 3 closes lingering choices and Exposure 4 leaves only immediate
advance or withdrawal. The protected playable slice and ratified rule instead
use narrative unease and urgency without automatic choice removal. The
supporting profile must be corrected during implementation so future work does
not reintroduce the stale rule.

### Injury, recovery, tactical exchanges, and practical advice

Restate only Tower-specific facts the reader needs: maximum Stamina, the lack
of recovery in this continuous intrusion, the consequences of reaching zero,
and the need to apply Stamina or Exposure before following the next
destination.

Give a spoiler-safe tactical illustration. Avoid names and situations that the
reader has not reached. Practical advice should sound like guidance from an
experienced player: keep a finger or marker at the current passage, read all
available actions, and update the sheet before turning the page.

### Rumours and anticipation

Retain a brief atmospheric orientation to Yara, the silver tower, and the Heart
of the Elephant. Coordinate it with the opening blurb so each paragraph adds
something. The rules should leave the tower mysterious.

## Rules at a Glance

This spread is a memory aid. It uses the same plain words taught in the primer
and introduces no new terminology.

The reusable side contains the roll-under test, Margin, Fortune, Advantage,
Disadvantage, and natural results in learned order. The Tower side contains
Conan's starting sheet, Stamina, possessions, story marks, and the Exposure
thresholds.

Reference density may be higher here because the reader has already learned
the rules. Clarity still governs. Passage codes, future encounter names,
`captured target`, `resolution-inert`, `terminal`, `slice`, and `authored` stay
off the player-facing spread.

## Adventure Sheet

The existing two-page grammar remains. The rewrite may adjust its short
instructions so they use the primer's vocabulary and voice.

The sheet must:

- identify the Sword as a starting possession;
- define Exposure in plain words before or beside the 0-5 track;
- make the starting value 0 unambiguous;
- explain that passages award possessions and story marks; and
- keep enough writable space for paper play.

## Voice and style rules

The primer should sound warm, direct, and bookish, with a current of pulp
adventure. It should feel like a good Custodian explaining a new game across a
table.

Apply these rules throughout:

- address the reader as `you`;
- prefer concrete verbs and ordinary nouns;
- explain one new idea at a time;
- define a term before using it in another rule;
- ground procedures in Conan's possible actions;
- vary sentence length and openings naturally;
- use rhetorical negation sparingly, under the agreed `saffron rule`;
- use `quiet`, `genuine`, `stakes`, and `honest` only when they are the most
  exact words;
- avoid generic AI cadence, decorative triplets, symmetrical contrast, and
  conspicuous synonym swapping; and
- read the finished prose aloud as part of editorial acceptance.

The following terms are banned from player-facing prose unless a later review
finds an unavoidable and clearly defined use:

- `authored`;
- `captured target` or `capture the target`;
- `resolution-inert`;
- `terminal` as a noun for an ending;
- `slice` for the playable adventure;
- `state and effect`; and
- `resolve E02` or comparable internal directions outside a passage that
  actually sends the reader there.

## Progressive disclosure and spoilers

The primer may reveal the premise, Conan's starting condition, the existence
of danger, and the rules needed to play. It must preserve the discovery of
specific allies, enemies, obstacles, tactics, and routes.

Before a named person, creature, item, mark, or event appears in the story, the
primer may mention it only when it belongs to the premise or starting sheet.
Internal passage identifiers appear solely as real navigation instructions.

Every sheet field should be taught as a lifecycle:

1. where its starting value or empty space comes from;
2. how a passage can change it;
3. how a later passage may consult it; and
4. when the reader crosses it off or updates it.

## Length

The rewrite should remain near the established scale while allowing the prose
room to teach:

| Component | Editorial range |
| --- | ---: |
| Before You Begin | 200-250 words |
| Part I: How to Play | 950-1,100 words |
| Part II: Rules for This Adventure | 450-600 words |
| Rules at a Glance | 220-280 words |
| Adventure Sheet instructions | about 100 words |

The reader-facing total should usually fall around 2,000-2,300 words. These
ranges guide proportion. Comprehension and pace govern the final cut.

## Mechanics that must remain unchanged

- Conan's profile is `BRN 13`, `AGI 12`, `CUN 12`, `WIL 12`, Fortune `10/10`,
  and Stamina `6/6`.
- Conan starts with the Sword, Exposure 0, and no story marks.
- An ordinary test succeeds when the final d20 is equal to or below the named
  attribute.
- Advantage keeps the lower of two d20s; Disadvantage keeps the higher.
- A selected natural 1 and natural 20 use their printed special outcomes and
  cannot be changed with Fortune.
- Margin is attribute minus final die.
- Each Fortune spent lowers an ordinary selected die by one.
- A Fortune test uses the current Fortune value fixed at the moment the test is
  called for.
- Passages apply Stamina loss directly; Stamina 0 reaches the death ending.
- The current material supplies no Fortune, Stamina, or Exposure recovery.
- Exposure is capped at 5. Values 3 and 4 add narrative unease and urgency but
  impose no universal choice restriction. Exposure 5 reaches the discovery
  crisis.
- Possessions and story marks are recorded and consumed only when passages say
  so.
- Tactical action is resolved through passage choices and consequences rather
  than repeated opponent-stat combat rounds.

## Originality guardrail

The rewrite adopts established genre functions: self-contained rules, friendly
play advice, examples, a quick reference, and a writable sheet. Its wording,
teaching order, examples, terminology, mechanics, page organisation, and
adventure module remain original to this project.

No sentence, example, table, stat package, random-number procedure, combat
loop, or play-aid design will be copied or closely paraphrased from *Fighting
Fantasy*, *Lone Wolf*, or another proprietary system. Their value here is
evidence that a gamebook can teach itself naturally.

## Implementation scope

Expected tracked changes are limited to:

- `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`;
- small vocabulary and instruction adjustments in
  `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`;
- the stale Exposure description in
  `stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md`;
- `docs/playtesting/live-playtest.md` for the fresh session and smaller review
  chunks;
- focused structural or behavioural tests only where a software-consumed
  contract changes; and
- this specification and its implementation plan.

The implementation must not change:

- numbered passage prose or route logic from S01 onward;
- `tools/live_playtest.py`;
- the four H2 lookup blocks exposed by the harness;
- the pre-S01 rules-then-sheet link order; or
- the local evidence from `tower-calibration-01` or `tower-calibration-02`.

Human-facing prose does not receive brittle source-text assertions. Existing
tests continue to protect lookup structure, reader links, and numbered passage
bytes. New tests must exercise real software behaviour rather than freeze
sentences.

## Editorial and technical acceptance

Before the rewritten primer is offered for another live calibration:

- every mechanic in the invariant list is present and accurate;
- every player-facing term appears after its explanation;
- the worked example's arithmetic is correct and understandable when read
  aloud;
- the opening identifies the series concept, story, Conan, and play materials;
- Conan is described as about seventeen, with the Howard quotation correctly
  attributed and contextualised;
- the Sword is plainly identified as a possession;
- Exposure contains no future encounter spoilers or internal passage code;
- possessions, story marks, tactical exchanges, and endings each have a
  concrete example;
- a manual prose audit checks voice, rhetorical negation, repeated sentence
  forms, AI-favoured vocabulary, and designer jargon;
- the four rules lookups remain available in their approved order;
- the S01-through-EOF digest remains unchanged;
- the full test suite passes on the current Python and Python 3.10; and
- the worktree is clean apart from the intended commits.

## Next calibration

`tower-calibration-02` remains paused as the record of the rejected
presentation. Its rules hash will no longer match after the rewrite, so it must
not be resumed.

The next session will be `tower-calibration-03`. It will begin again at
**Before You Begin** and present no more than one or two subsections at a time.
The facilitator records each reaction before answering and proceeds only after
the reader has had room to comment. S01 remains hidden until all primer parts,
Rules at a Glance, and the Adventure Sheet have been reviewed and the reader
says they are ready.
