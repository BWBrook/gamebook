# *Tower* Source Map and Paper Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Map *The Tower of the Elephant* as a source-grounded directed graph, then build and paper-playtest a self-contained infiltration slice that exercises the approved Authored S&S solo core.

**Architecture:** Represent Howard's linear source first as an 18-node canonical spine, with tables overlaying invariants, seams, elastic intervals, and counterfactual boundaries. Derive one actual passage graph from the outer-wall beat at the end of `TT-04` through `TT-08`: local choices branch, sparse state preserves their consequences, and routes reconverge at the rope ascent or terminate explicitly. Keep every deliverable in human-readable Markdown and stop before selecting a machine-readable passage schema or building runtime tools.

**Tech Stack:** Markdown, Mermaid flowchart syntax, POSIX/macOS shell tools, ripgrep, awk, Git, paper, pen, and d20s

## Global Constraints

- Treat `stories/public_domain/howard/tower_of_the_elephant/source.md` as read-only reference text with SHA-256 `416115fed82458a855d2c2c7f37f29c3b4c8b2747618ef18bcbed2d821d0df1f`.
- Preserve the approved Authored S&S solo core: d20 roll-under, natural 1 and natural 20, Advantage and Disadvantage, functional margin, post-roll Fortune expenditure, authored Stamina loss, one visible 0-5 Pressure track, sparse semantic state, and authored tactical exchanges.
- Use Conan's approved fixed profile exactly: `BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6`.
- Keep *Tower* between mixed consequences and hard pulp. State lethal stakes before the roll; provide no universal rescue, death save, or automatic recovery.
- Roll only when execution remains genuinely uncertain and both success and failure have meaningful authored outcomes.
- Every recorded possession or story mark must have a reachable producer and a reachable consumer.
- Preserve a canonical centre while allowing credible, earned alternatives. Reconverged routes must retain a changed cost, possession, knowledge, position, available choice, or prose acknowledgement.
- The paper slice must contain at least one direct choice, one consequential roll, one post-roll Fortune decision, one state dependency, and one authored tactical exchange.
- Use only Markdown documents in this increment. Do not select YAML, JSON, TOML, a database, or another machine-readable passage schema.
- Do not add Python, JavaScript, application code, dependencies, build tooling, graph validators, deterministic play tools, or AI-facilitator instructions.
- Do not change `source.md`, its provenance record, or its rights assessment.
- Edge weights, route frequencies, and balance statistics require play data and remain outside the source map. Do not invent them.

---

## Graph model

The increment deliberately produces two related views.

1. **Canonical source graph:** Each `TT-nn` node is a scene or beat in Howard's
   story. Solid directed edges record causal and chronological dependence. The
   graph is a spine because the source is linear; classifications and tables
   identify where an adaptation may branch.
2. **Playable slice graph:** Each `Snn` node is a reader-facing passage and each
   `Enn` node is an explicit ending. Directed edges are actual choices or
   authored result transitions. Conditional edges read only the sparse state
   defined in the slice profile.

This borrows the states-and-transitions clarity of Christian Swinehart's
[CYOA visualisations](https://samizdat.co/cyoa/) without confusing analysis of
an existing short story with analysis of an already-authored gamebook.

## File map

- Create `stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md`
  — whole-source canonical graph, node catalogue, adaptation classifications,
  cross-cutting pressures, and selected slice boundary.
- Create `stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md`
  — fixed Conan profile, *Tower* lethality, `Exposure` Pressure definition,
  slice state, passage blueprint, and playable slice graph.
- Create `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`
  — concise reader-facing rules needed by the slice.
- Create `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`
  — printable record sheet for Conan, resources, `Exposure`, possessions, and
  story marks.
- Create `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`
  — second-person, paper-playable outer-wall and garden passages.
- Create `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01-audit.md`
  — source crosswalk, passage/link audit, state producer-consumer audit,
  deterministic route rehearsals, and the first paper-procedure play record.
- Modify `stories/public_domain/howard/tower_of_the_elephant/README.md`
  — index the source, adaptation, and playtest artefacts without weakening the
  provenance or rights record.
- Modify `README.md` — replace the obsolete establishment status with links to
  the approved solo-core design and the first playable increment.
- Retain `docs/superpowers/specs/2026-07-30-authored-sinew-steel-solo-core-design.md`
  — approved governing design.
- Retain `docs/superpowers/plans/2026-07-30-tower-source-map-and-paper-slice.md`
  — implementation sequence and verification record.

### Task 1: Build the whole-source adaptation map

**Files:**

- Create: `stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md`
- Read: `stories/public_domain/howard/tower_of_the_elephant/source.md`
- Read: `docs/research/gamebook-systems-background.md`
- Read: `docs/superpowers/specs/2026-07-30-authored-sinew-steel-solo-core-design.md`

**Interfaces:**

- Consumes: the immutable 329-line source text and the approved four-part
  adaptation vocabulary.
- Produces: stable source nodes `TT-01` through `TT-18`, their canonical edges,
  classification evidence, cross-cutting candidate state, and the evidence for
  selecting source lines 72-188—the outer-wall beat at the end of `TT-04`
  through `TT-08`—as the representative slice.

- [ ] **Step 1: Verify the source baseline before analysis**

Run:

```bash
shasum -a 256 \
  stories/public_domain/howard/tower_of_the_elephant/source.md
wc -l -w \
  stories/public_domain/howard/tower_of_the_elephant/source.md
git status --short --branch
```

Expected:

```text
416115fed82458a855d2c2c7f37f29c3b4c8b2747618ef18bcbed2d821d0df1f  stories/public_domain/howard/tower_of_the_elephant/source.md
     329    9722 stories/public_domain/howard/tower_of_the_elephant/source.md
```

The branch must be clean apart from this implementation plan. Stop if the
source checksum differs because every line anchor below then requires review.

- [ ] **Step 2: Create the canonical graph and node catalogue**

Create `adaptation/map.md` with these sections in this order:

```markdown
# *The Tower of the Elephant* Adaptation Map

## Purpose and scope
## Legend
## Canonical source graph
## Node catalogue
## Narrative invariants
## Decision seams and elastic intervals
## Counterfactual boundaries
## Hazards, information, and relationships
## State and recovery candidates
## Pressure candidates
## Representative slice
## Conclusions carried into passage design
```

Under `## Canonical source graph`, add one Mermaid `flowchart TD`. Place the
nodes in three chapter subgraphs and connect every consecutive pair from
`TT-01` through `TT-18` with a solid arrow. Use node labels short enough to
remain readable when GitHub renders the graph.

The node catalogue must contain exactly these source spans:

| ID | Lines | Opening anchor | Closing anchor | Scene |
| --- | ---: | --- | --- | --- |
| `TT-01` | 7-25 | `TORCHES flared murkily` | `secret of his magic` | The Maul, Conan, and the first account of the Heart |
| `TT-02` | 27-49 | `The barbarian digested` | `desire be coupled with courage` | Conan proposes the upper route and is mocked |
| `TT-03` | 51-57 | `The Kothian chose` | `killed his man` | The tavern quarrel and death in darkness |
| `TT-04` | 62-76 | `THE lurid lights` | `Elephant's Tower` | Temple quarter, Conan's worldview, and Yara lore |
| `TT-05` | 78-84 | `The Cimmerian, engrossed` | `choked out the soldier's life` | Outer wall, vanished patrol, and dead guard |
| `TT-06` | 86-134 | `Straining his eyes` | `Conan followed him` | Conan stalks, recognises, and allies with Taurus |
| `TT-07` | 136-168 | `I see no light` | `waste the night in discussion` | Inner garden and Taurus's black-lotus answer to the lions |
| `TT-08` | 170-188 | `They glided through` | `steeped in the deadly wine` | Rope cast and the silent lion's attack |
| `TT-09` | 190-202 | `The Nemedian gripped` | `seemed empty of life` | Ascent, jeweled rim, and roof chamber |
| `TT-10` | 204-216 | `Before we cut off` | `retreated by the same way` | Taurus enters alone, dies, and is examined |
| `TT-11` | 218-232 | `Closing the door` | `twinkling gems` | The spider reveals itself and Conan kills it |
| `TT-12` | 234-243 | `Conan glared about` | `white tusks tipped` | Conan presses inward and finds the strange being |
| `TT-13` | 245-269 | `This then, was the reason` | `magic of deliverance` | Yag-kosha wakes; horror gives way to pity |
| `TT-14` | 271-291 | `Again tears fell` | `Blood and the Jewel` | Cosmic history, Yara's betrayal, and captivity |
| `TT-15` | 293-301 | `For I feel the end` | `absorbed by a sponge` | The Heart, Yag-kosha's request, and mercy ritual |
| `TT-16` | 303-315 | `Holding the jewel` | `last gift and a last enchantment` | Descent to Yara and delivery of the Heart |
| `TT-17` | 317-325 | `Yara recoiled` | `Yag-kosha and Yogah had lain` | Yara shrinks and vanishes into the avenger's realm |
| `TT-18` | 327-329 | `The Cimmerian turned` | `crash into shining shards` | Cleared escape, dawn, and the tower's collapse |

For every catalogue row, add compact columns after `Scene` for:

- invariant or supporting canonical function;
- natural decision seam;
- elastic method, route, or consequence;
- counterfactual boundary;
- hazard or information transition; and
- relationship change.

Use `—` where the source supplies no evidence for a category. Do not force
every classification onto every node.

- [ ] **Step 3: Record the adaptation overlay and whole-story constraints**

Under the sections following the catalogue, record:

- the defining invariants: Conan as young seasoned outsider; the Heart and
  tower; the theft motive; Taurus as capable peer and doomed ally; the tower's
  silent unnatural dangers; Yag-kosha as captive person rather than idol or
  monster; pity replacing horror; Yara's enslavement and punishment; and the
  tower's destruction at dawn;
- the strongest seams: how Conan obtains and acts on information, enters the
  precinct, handles the corpse, approaches Taurus, crosses the gardens,
  responds to Taurus's death, fights the spider, responds to Yag-kosha, answers
  the mercy request, and confronts or avoids Yara;
- elastic intervals that can vary without breaking the source: preparation,
  route details, tactical methods, resource costs, discoveries, evidence left
  behind, and the manner of withdrawal or escape;
- boundaries that end or transform the adaptation rather than support a long
  invented branch: Conan abandons the theft, kills or permanently rejects
  Taurus, strips the rim and leaves, refuses all contact with Yag-kosha,
  assists Yara, or prevents the central captivity-and-revenge revelation;
- every source-backed hazard, information transition, and relationship change;
- the nonlocal dependencies that later passages must preserve: the tavern
  killing is sensed by Yag-kosha; Taurus supplies the garden method and upper
  route before his loss changes Conan's position; the lion, spider, and
  Taurus's death are recounted to Yag-kosha; the Heart, blood ritual, and
  spoken formula jointly cause Yara's destruction; and that destruction
  clears Conan's escape;
- candidate possessions and story marks only where a later mapped scene could
  consume them;
- the absence of plausible Stamina or Fortune recovery during the selected
  infiltration slice; and
- `Exposure` as the selected Pressure model because the source repeatedly
  connects delay, noise, bodies, patrols, soldiers, and signs of intrusion to
  the risk that the theft is discovered.

Compare `Exposure` explicitly with two rejected candidates:

- `Entrapment`: source-backed as retreat narrows inside the upper tower, but it
  does little work during the outer-wall and garden slice;
- `Dread`: source-backed in the upper tower, but it makes Conan's emotional
  state carry an external-pressure job more cleanly performed by discovery.

Conclude that source lines 72-188—the outer-wall beat at the end of `TT-04`
through `TT-08`—form the first slice because they have:

- a clean entry at Conan's final hesitation outside the wall;
- information gathering and direct choice;
- a relationship seam with Taurus;
- a source-backed possession at the dead guard;
- escalating external pressure;
- a minor tactical exchange with the silent lion; and
- a clean exit once Taurus's rope is secured and the ascent begins.

State that `TT-09` through `TT-11` is the strongest second slice, not part of
this increment.

- [ ] **Step 4: Verify map coverage and source anchors**

Run:

```bash
map_file=stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md
source_file=stories/public_domain/howard/tower_of_the_elephant/source.md

test "$(rg -c '^\| `TT-[0-9]{2}` \|' "$map_file")" -eq 18
test "$(rg -o '^\| `TT-[0-9]{2}` \|' "$map_file" \
  | sort -u | wc -l | tr -d ' ')" -eq 18

for edge_number in $(jot - 1 17); do
  from=$(printf 'TT-%02d' "$edge_number")
  to=$(printf 'TT-%02d' "$((edge_number + 1))")
  rg -q "${from} --> ${to}" "$map_file"
done

rg -q 'TORCHES flared murkily' "$source_file"
rg -q 'desire be coupled with courage' "$source_file"
rg -q 'choked out the soldier.s life' "$source_file"
rg -q 'steeped in the deadly wine' "$source_file"
rg -q 'Yag-kosha and Yogah had lain' "$source_file"
rg -q 'crash into shining shards' "$source_file"

rg -q '^## Narrative invariants$' "$map_file"
rg -q '^## Decision seams and elastic intervals$' "$map_file"
rg -q '^## Counterfactual boundaries$' "$map_file"
rg -q '^## Pressure candidates$' "$map_file"
rg -q '^## Representative slice$' "$map_file"
git diff --check
```

Expected: every command exits 0; the table contains 18 unique node rows; the
Mermaid source contains all 17 canonical edges; and `git diff --check`
produces no output.

- [ ] **Step 5: Commit the map**

```bash
git add \
  docs/superpowers/plans/2026-07-30-tower-source-map-and-paper-slice.md \
  stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md
git diff --cached --check
git commit -m "docs: map Tower adaptation seams"
```

### Task 2: Lock the story profile and playable slice graph

**Files:**

- Create: `stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md`
- Read: `stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md`
- Read: `docs/superpowers/specs/2026-07-30-authored-sinew-steel-solo-core-design.md`

**Interfaces:**

- Consumes: source lines 72-188, spanning the outer-wall beat at the end of
  `TT-04` through `TT-08`, the selected `Exposure` model, and the approved
  solo core.
- Produces: the exact reader-facing resource rules, sparse state contract,
  passage IDs, transitions, tests, and endings used by the paper slice.

- [ ] **Step 1: Create the story-profile document**

Create `adaptation/story-profile.md` with these sections:

```markdown
# *The Tower of the Elephant* Story Profile

## Scope
## Conan
## Lethality
## Exposure
## Recovery
## Slice boundary
## Sparse state
## Passage graph
## Passage blueprint
## Canonical route and earned alternatives
## Source-fidelity constraints
## Deferred decisions
```

Record the fixed profile and its 20-point provenance exactly as approved.
State that the slice begins outside the outer wall at source line 72, includes
the final outer-wall beat of `TT-04` and all events mapped as `TT-05` through
`TT-08`, and ends after the silent lion when Taurus's rope is ready for the
ascent at line 188.

- [ ] **Step 2: Define `Exposure` completely**

Define `Exposure` as visible evidence, delay, or disturbance that makes the
intrusion more likely to be discovered. Start it at 0 and cap it at 5.

Use these exact bands:

| Exposure | Fictional state | Passage effect |
| ---: | --- | --- |
| 0-2 | The intruders remain unconfirmed. | All listed choices remain available. |
| 3 | The watch has reason for unease. | Passages acknowledge movement or attention below; lingering choices close. |
| 4 | A search is beginning. | Only immediate advance or withdrawal choices remain legal. |
| 5 | The breach is discovered. | Resolve the contextual `E02` crisis; do not reduce the track to preserve the route. |

Author increments only for these slice events:

- `+1` when Conan deliberately waits through another patrol interval;
- `+1` when he calls loudly or creates an avoidable disturbance;
- `+1` for an ordinary failed standoff with Taurus;
- `+2` for a natural 20 during that standoff;
- the amount printed by the selected lion tactic on a costly result.

No ordinary event lowers `Exposure` in this slice. Record the whole-story
release already supported by the source: Yag-kosha's final act stills the
soldiers and clears Conan's escape. Its exact full-adventure passage remains
deferred.

- [ ] **Step 3: Define the sparse state and its consumers**

The slice starts with:

```text
Sword
Fortune 10/10
Stamina 6/6
Exposure 0/5
```

At `S04`, allow exactly one of these mutually exclusive discoveries:

- possession `Guard's spear`;
- story mark `Read the strangling`.

Define their consumers:

- `Guard's spear` unlocks the spear method at `S11` and is crossed off when
  used;
- `Read the strangling` unlocks the quiet recognition choice at `S05`, then is
  crossed off.

No other possession or story mark is recorded in the slice. Taurus's rope and
black-lotus powder remain his equipment and never enter Conan's sheet.

- [ ] **Step 4: Add the exact passage graph and blueprint**

Add a Mermaid `flowchart TD` using these defined nodes:

| ID | Purpose |
| --- | --- |
| `S01` | Conan judges the outer wall |
| `S02` | He listens through another patrol interval |
| `S03` | He finds the dead guard and nearby movement |
| `S04` | He takes one discovery from the corpse |
| `S05` | He chooses how to confront the hidden stranger |
| `S06` | Taurus is revealed and recognises a fellow thief |
| `S07` | Taurus offers an alliance |
| `S08` | They cross the inner wall |
| `S09` | The garden lions close in |
| `S10` | Black-lotus powder clears the visible pride |
| `S11` | The silent lion attacks at the tower foot |
| `S12` | Conan wins cleanly |
| `S13` | Conan wins at an authored cost |
| `S14` | Taurus's rope is secured; the slice is complete |
| `E01` | Conan withdraws alive and abandons this theft |
| `E02` | Exposure 5: the watch discovers the breach |
| `E03` | Conan dies during the breach attempt |

Use these transitions and conditions:

```text
S01 -> S02: wait and listen; Exposure +1
S01 -> S03: climb at once
S02 -> S03: climb after the patrol interval
S03 -> S04: examine the corpse before following the movement
S03 -> S05: pursue the movement immediately
S04 -> S05: take Guard's spear or record Read the strangling
S05 -> S06: consume Read the strangling and identify a human ambusher
S05 -> S06: call out without the mark; Exposure +1
S05 -> S06: stalk the stranger; consequential CUN test
S06 -> S07: recognise Taurus
S07 -> S08: accept the alliance
S07 -> E01: withdraw
S08 -> S09: cross the inner wall
S09 -> S10: trust Taurus's instruction
S10 -> S11: advance after the powder disperses
S11 -> S12: clean tactical success
S11 -> S13: ordinary costly tactical success
S11 -> E03: locked natural 20
S12 -> S14: clean the blade and continue
S13 -> S14: continue if Stamina remains above 0 and Exposure below 5
any non-terminal node -> E02: an authored update reaches Exposure 5
any damaging result -> E03: Stamina reaches 0
```

Define the `S05` Cunning test:

- target captured at `CUN 12`;
- state the stakes before rolling;
- success reaches `S06` without cost;
- ordinary failure reaches `S06`, loses 1 Stamina, and adds 1 Exposure;
- natural 1 reaches `S06` with prose showing Conan takes the superior position;
- natural 20 reaches `S06`, loses 2 Stamina, and adds 2 Exposure;
- post-roll Fortune may alter an ordinary result but never a natural 1 or 20.

Define the `S11` tactical methods:

| Method | Availability | Roll | Clean success | Ordinary failure | Natural 1 | Natural 20 |
| --- | --- | --- | --- | --- | --- | --- |
| Brace the guard's spear | Requires and consumes `Guard's spear` | BRN 13 with Advantage | `S12` | lose 2 Stamina, Exposure +1, then `S13` | kill before it can make a sound, then `S12` | `E03` |
| Wheel beneath the leap | Always available | BRN 13 | `S12` | lose 2 Stamina, Exposure +1, then `S13` | split the skull cleanly, then `S12` | `E03` |
| Slip aside and cut as it passes | Always available | AGI 12 | `S12` | lose 1 Stamina, Exposure +2, then `S13` | turn its own speed against it, then `S12` | `E03` |

State the fatal natural-20 stake before the player chooses a method. Permit
post-roll Fortune on ordinary dice only.

- [ ] **Step 5: Record route and fidelity policy**

Identify the canonical route as:

```text
S01 -> S03 -> S04 -> S05 -> S06 -> S07 -> S08 -> S09 -> S10
-> S11 -> S12 -> S14
```

Both `Guard's spear` and `Read the strangling` routes may reach `S14`; their
different options and resource histories make the reconvergence stateful.
`E01` is a credible refusal ending, while `E02` and `E03` enforce external and
mortal consequences.

Record these prose boundaries:

- Conan can be cautious, suspicious, curious, proud, violent, compassionate,
  and practical; he cannot become a timid modern moral commentator.
- Taurus remains formidable, confident, and more prepared than Conan.
- The black lotus, visible lions, lone silent lion, rope, hook, and tower
  remain source-grounded facts.
- The slice may alter Conan's method and cost; it may not remove Taurus,
  relocate the tower, turn the lions into routine opponents, or reveal
  Yag-kosha early.

Under `## Deferred decisions`, list only later increments already deferred by
the approved design: upper-tower passage design, full-adventure state,
machine-readable representation, validators, deterministic harness, and AI
facilitator.

- [ ] **Step 6: Verify profile completeness and graph references**

Run:

```bash
profile=stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md

rg -q 'BRN 13 . AGI 12 . CUN 12 . WIL 12 . FOR 10/10 . STM 6/6' "$profile"
rg -q '^## Exposure$' "$profile"
rg -q '^## Sparse state$' "$profile"
rg -q '^## Passage graph$' "$profile"
rg -q '^## Canonical route and earned alternatives$' "$profile"

test "$(rg -c '^\| `S[0-9]{2}` \|' "$profile")" -eq 14
test "$(rg -c '^\| `E[0-9]{2}` \|' "$profile")" -eq 3

rg -q 'Guard.s spear.*S11' "$profile"
rg -q 'Read the strangling.*S05' "$profile"
rg -q 'Exposure 5.*E02' "$profile"
rg -q 'Stamina reaches 0.*E03' "$profile"
rg -q 'natural 20.*E03' "$profile"
git diff --check
```

Expected: all commands exit 0 and `git diff --check` produces no output.

- [ ] **Step 7: Commit the story profile**

```bash
git add \
  stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md
git diff --cached --check
git commit -m "docs: define Tower infiltration slice"
```

### Task 3: Create the paper-play reader kit

**Files:**

- Create: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`
- Create: `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`
- Read: `stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md`
- Read: `docs/superpowers/specs/2026-07-30-authored-sinew-steel-solo-core-design.md`

**Interfaces:**

- Consumes: the approved stable mechanics and the slice-specific `Exposure`
  rules.
- Produces: a complete reader reference and one-sheet record surface requiring
  only paper, pen, and d20s.

- [ ] **Step 1: Write the quick rules**

Create `playtest/quick-rules.md` with these sections:

```markdown
# *The Tower of the Elephant* Playtest Rules

## What you need
## Conan
## Choices and tests
## Advantage and Disadvantage
## Natural 1 and natural 20
## Fortune
## Stamina
## Exposure
## Tactical exchanges
## Endings
```

Write for a first-time gamebook reader. Include:

- paper, pen, and one d20, with two d20s convenient for Advantage or
  Disadvantage;
- Conan's exact fixed profile and no character creation;
- the test sequence `state stakes -> choose method -> roll -> select die ->
  compute margin -> optionally spend Fortune -> apply authored result`;
- success on a result equal to or below the captured attribute;
- Advantage keeps the lower of two d20s and Disadvantage keeps the higher;
- locked natural 1 and natural 20;
- Fortune cost equal to the number of points by which the selected die is
  lowered, deducted after the captured test resolves;
- direct Stamina loss and death at 0;
- `Exposure` bands and crisis exactly matching the story profile;
- no enemy statistics or repeated combat rounds; and
- explicit terminal endings.

State that no recovery occurs within this slice. Keep the complete quick rules
between 800 and 1,400 words.

- [ ] **Step 2: Create the adventure sheet**

Create `playtest/adventure-sheet.md` with:

- Conan's six fixed values;
- ten visible Fortune boxes, initially all available;
- six visible Stamina boxes, initially all available;
- an `Exposure` track labelled 0 through 5, initially 0;
- `Sword` pre-recorded under possessions;
- two blank possession lines;
- two blank story-mark lines; and
- a short instruction to cross off consumed state.

Do not add armour, money, experience, provisions, initiative, enemy health,
carry slots, spell fields, or character-creation controls.

- [ ] **Step 3: Verify the reader kit against the profile**

Run:

```bash
rules=stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
sheet=stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md

for heading in \
  'What you need' Conan 'Choices and tests' \
  'Advantage and Disadvantage' 'Natural 1 and natural 20' \
  Fortune Stamina Exposure 'Tactical exchanges' Endings
do
  rg -q "^## ${heading}$" "$rules"
done

rg -q 'equal to or below' "$rules"
rg -q 'keeps the lower' "$rules"
rg -q 'keeps the higher' "$rules"
rg -q 'Neither.*Fortune|cannot.*Fortune' "$rules"
rg -q '0 Stamina|zero Stamina' "$rules"
rg -q 'BRN 13 . AGI 12 . CUN 12 . WIL 12 . FOR 10/10 . STM 6/6' \
  "$rules" "$sheet"

test "$(wc -w < "$rules" | tr -d ' ')" -ge 800
test "$(wc -w < "$rules" | tr -d ' ')" -le 1400

if rg -ni 'armour|experience|provisions|initiative|enemy health|spell slot' \
  "$rules" "$sheet"
then
  exit 1
fi

git diff --check
```

Expected: all positive checks succeed; the excluded-residue scan produces no
matches; and `git diff --check` produces no output.

- [ ] **Step 4: Commit the reader kit**

```bash
git add \
  stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md
git diff --cached --check
git commit -m "docs: add Tower paper playtest rules"
```

### Task 4: Draft the playable outer-wall and garden slice

**Files:**

- Create: `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`
- Read: `stories/public_domain/howard/tower_of_the_elephant/source.md:72`
- Read: `stories/public_domain/howard/tower_of_the_elephant/source.md:188`
- Read: `stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md`
- Read: `stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md`
- Read: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`

**Interfaces:**

- Consumes: passage IDs and mechanics from the story profile plus source lines
  72-188.
- Produces: one complete, navigable Markdown gamebook slice with 14 playable
  passages and three explicit endings.

- [ ] **Step 1: Establish the reader-facing passage format**

Start `playtest/slice-01.md` with:

```markdown
# *The Tower of the Elephant*: Outer Wall Playtest

Read the [quick rules](quick-rules.md), copy or print the
[adventure sheet](adventure-sheet.md), and begin at **S01**.
```

Use headings in this exact form:

```markdown
## S01 — The Outer Wall
```

Every choice must end with either:

```markdown
Turn to **S02**.
```

or an explicit inline state update followed by a turn instruction. Every test
must display, before the roll:

- the method;
- attribute and roll mode;
- success consequence;
- ordinary failure consequence;
- natural-1 consequence;
- natural-20 consequence; and
- whether ordinary dice permit Fortune.

Terminal passages `E01`, `E02`, and `E03` must contain the visible label
`**Ending:**` and no turn instruction.

- [ ] **Step 2: Draft `S01` through `S07`**

Adapt source lines 72-134 into second-person present tense while preserving
Howard's concrete setting, Conan's voice, the fresh strangled corpse, Taurus's
competence, and the mutual recognition between thieves.

Implement exactly:

- `S01`: direct choice to climb now or wait; waiting adds 1 Exposure;
- `S02`: the measured tread stops and the next patrol interval approaches;
- `S03`: direct choice between immediate pursuit and one examination;
- `S04`: mutually exclusive `Guard's spear` or `Read the strangling`;
- `S05`: marked recognition, noisy call, or consequential CUN test;
- `S06`: Taurus's identity and Conan's correction about the exposed corpse;
- `S07`: accept Taurus's alliance or withdraw to `E01`.

Do not invent another guard, treasure, helper, weapon, route, or supernatural
explanation.

- [ ] **Step 3: Draft `S08` through `S10`**

Adapt source lines 134-168. Preserve:

- removal of Conan's sandals;
- the inner wall;
- the lions' eyes and silent threat;
- Taurus's instruction to remain behind him;
- the black-lotus cloud and its lethal inhalation stakes;
- five dead lions; and
- the fact that Taurus has no powder left.

Resolve competent compliance directly. Do not roll to climb the ordinary wall,
follow clear instructions, or wait for the visible poison cloud to disperse.
At Exposure 3 or 4, acknowledge signs that the watch is stirring and remove
any lingering option; at 5, turn immediately to `E02`.

- [ ] **Step 4: Draft `S11` through `S14`**

Adapt source lines 170-188. `S11` must present the three tactical methods from
the story profile, their state requirements, and their complete announced
stakes.

Write:

- `S12` as the source-faithful clean kill and Taurus's astonishment;
- `S13` as victory with the selected Stamina and Exposure cost, including a
  check for 0 Stamina or Exposure 5 before continuation; and
- `S14` as a non-terminal slice-complete result: Taurus's hook catches, the
  rope is secure, and the full adventure would continue upward.

`S14` must state the final Fortune, Stamina, Exposure, possession, and mark
state should be retained for a later continuation, without inventing that
continuation.

- [ ] **Step 5: Draft the three endings**

Write:

- `E01`: Conan chooses survival over this attempt; alive, but without the
  Heart and outside the canonical story;
- `E02`: the watch discovers the intrusion after Exposure reaches 5; the
  upper route is lost and the attempt ends with a hard source-plausible
  consequence rather than a reset; and
- `E03`: Conan dies from 0 Stamina during the breach attempt or from the
  silent lion's locked natural-20 result.

Keep `E02` and `E03` concise. Do not redirect the reader to retry.

- [ ] **Step 6: Run structural and content checks**

Run:

```bash
slice=stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md

defined_ids=$(rg -o '^## (S|E)[0-9]{2}' "$slice" \
  | awk '{print $2}' | sort -u)
referenced_ids=$(rg -o 'Turn to \\*\\*(S|E)[0-9]{2}\\*\\*' "$slice" \
  | rg -o '(S|E)[0-9]{2}' | sort -u)

test "$(printf '%s\n' "$defined_ids" | rg -c '^S[0-9]{2}$')" -eq 14
test "$(printf '%s\n' "$defined_ids" | rg -c '^E[0-9]{2}$')" -eq 3
test -z "$(comm -23 \
  <(printf '%s\n' "$referenced_ids") \
  <(printf '%s\n' "$defined_ids"))"

test "$(rg -c '^\\*\\*Ending:\\*\\*' "$slice")" -eq 3
rg -q 'Guard.s spear' "$slice"
rg -q 'Read the strangling' "$slice"
rg -q 'CUN 12' "$slice"
rg -q 'BRN 13 with Advantage' "$slice"
rg -q 'AGI 12' "$slice"
rg -q 'Fortune' "$slice"
rg -q 'Exposure' "$slice"
rg -q 'Stamina' "$slice"

test "$(wc -w < "$slice" | tr -d ' ')" -ge 2500
test "$(wc -w < "$slice" | tr -d ' ')" -le 4500
git diff --check
```

Expected: 14 unique `S` passages and three unique `E` passages are defined;
every referenced destination exists; all three endings are explicit; the
required mechanics appear; the slice is between 2,500 and 4,500 words; and
`git diff --check` produces no output.

- [ ] **Step 7: Commit the playable draft**

```bash
git add \
  stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md
git diff --cached --check
git commit -m "feat: draft Tower outer-wall slice"
```

### Task 5: Audit, paper-play, revise once, and index the increment

**Files:**

- Create: `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01-audit.md`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md`
- Modify: `stories/public_domain/howard/tower_of_the_elephant/README.md`
- Modify: `README.md`

**Interfaces:**

- Consumes: the complete paper kit and passage graph.
- Produces: verified link/state coverage, five reproducible route rehearsals,
  one reader-only paper-procedure play record, one focused repair pass, and
  indexed reader/author entry points.

- [ ] **Step 1: Create the source and state audit**

Create `playtest/slice-01-audit.md` with:

```markdown
# Outer Wall Slice Audit

## Scope
## Source crosswalk
## Passage and edge inventory
## State producer-consumer audit
## Mechanical coverage
## Deterministic route rehearsals
## Paper-procedure play record
## Focused revision
## Residual questions
```

The source crosswalk must map every `S` and `E` passage to one or more source
lines within 72-188 or label it as an authored consequence of a listed
decision. It must not cite material from later chapters as foreknowledge.

The state audit must show:

| State | Producer | Consumer | Removal |
| --- | --- | --- | --- |
| `Guard's spear` | `S04` | spear method at `S11` | crossed off before rolling |
| `Read the strangling` | `S04` | quiet recognition at `S05` | crossed off on use |
| Fortune | starts at 10 | ordinary rolls at `S05` and `S11` | spend after selected die |
| Stamina | starts at 6 | failures at `S05` and `S11` | death at 0 via `E03` |
| Exposure | starts at 0 | thresholds in `S03`, `S08`, `S10`, `S13` | crisis at 5 via `E02` |

Confirm that no written state lacks a future consumer and no conditional choice
lacks a prior producer.

- [ ] **Step 2: Rehearse five exact routes**

Record each choice, raw die or dice, selected die, margin, Fortune spend, state
update, and destination.

Use these routes:

1. **Canonical clean route:** climb immediately; examine the strangling;
   consume the mark at `S05`; accept Taurus; use the sword at `S11`; roll 8
   against BRN 13; finish at `S14` with Fortune 10, Stamina 6, Exposure 0.
2. **Prepared Fortune route:** wait; take the spear; stalk Taurus; roll 15
   against CUN 12 and spend 3 Fortune; accept; brace the spear; roll 17 and 9
   with Advantage and keep 9; finish at `S14` with Fortune 7, Stamina 6,
   Exposure 1, and the spear consumed.
3. **Costly agility route:** climb; pursue movement; call out without the
   mark; accept; slip aside at `S11`; roll 14 against AGI 12 and decline
   Fortune; apply 1 Stamina loss and 2 Exposure; finish at `S14` with Fortune
   10, Stamina 5, Exposure 3.
4. **Locked exceptional success:** reach `S11`, use any legal method, roll a
   natural 1, spend no Fortune, and reach `S12` then `S14` through the
   exceptional prose.
5. **Locked fatal result:** reach `S11`, roll a natural 20, confirm Fortune is
   forbidden, and terminate at `E03`.

Stop and repair the responsible passage before continuing if a recorded state
or destination differs from these expected outcomes.

- [ ] **Step 3: Conduct one reader-only paper-procedure play**

Use only `quick-rules.md`, `adventure-sheet.md`, and `slice-01.md`. Copy the
starting sheet to paper or a plain scratch record and do not inspect the
author-facing graph or profile while playing. Use physical d20s when a human
implementer has them; otherwise generate each independent d20 with:

```bash
jot -r 1 1 20
```

Do not write or use a play harness. In `## Paper-procedure play record`,
record:

- date and player;
- chosen route;
- raw rolls and Fortune decisions;
- ending or slice-complete state;
- every rules lookup;
- every moment when required bookkeeping was unclear;
- every choice whose stakes were unclear before commitment;
- every transition that felt cosmetic or forced; and
- elapsed play time.

Do not report a physical-paper or blind-reader test unless it actually occurs.

- [ ] **Step 4: Perform one focused repair pass**

Review the map, profile, rules, sheet, slice, and audit once. Repair only
material defects found in:

- source fidelity;
- Conan's character;
- missing or misleading stakes;
- Fortune timing;
- natural-result handling;
- state production or consumption;
- `Exposure` thresholds;
- passage links;
- repetitive or non-tactical conflict;
- cosmetic reconvergence; or
- reader-facing clarity.

Record each material change under `## Focused revision` with its reason and
verification route. Record remaining questions under `## Residual questions`
without expanding into the upper-tower slice, schema, harness, or AI work.

- [ ] **Step 5: Update the repository indexes**

In the story `README.md`:

- preserve the full source, conversion, and rights sections unchanged;
- replace the final scope paragraph with an indexed `## Adaptation work`
  section;
- link to `adaptation/map.md`, `adaptation/story-profile.md`,
  `playtest/quick-rules.md`, `playtest/adventure-sheet.md`,
  `playtest/slice-01.md`, and `playtest/slice-01-audit.md`; and
- identify the slice as a development playtest rather than a complete
  adaptation.

In the root `README.md`:

- replace `The repository is being established` with a concise current status;
- link to the approved solo-core specification;
- link to the Tower adaptation map and paper slice; and
- state that passage schema, deterministic tooling, and AI facilitation remain
  later increments.

- [ ] **Step 6: Run final increment verification**

Run:

```bash
set -e

source_file=stories/public_domain/howard/tower_of_the_elephant/source.md
map_file=stories/public_domain/howard/tower_of_the_elephant/adaptation/map.md
profile=stories/public_domain/howard/tower_of_the_elephant/adaptation/story-profile.md
rules=stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md
sheet=stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md
slice=stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md
audit=stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01-audit.md

test "$(shasum -a 256 "$source_file" | awk '{print $1}')" = \
  416115fed82458a855d2c2c7f37f29c3b4c8b2747618ef18bcbed2d821d0df1f

for file in "$map_file" "$profile" "$rules" "$sheet" "$slice" "$audit"
do
  test -s "$file"
done

defined_ids=$(rg -o '^## (S|E)[0-9]{2}' "$slice" \
  | awk '{print $2}' | sort -u)
referenced_ids=$(rg -o 'Turn to \\*\\*(S|E)[0-9]{2}\\*\\*' "$slice" \
  | rg -o '(S|E)[0-9]{2}' | sort -u)
test -z "$(comm -23 \
  <(printf '%s\n' "$referenced_ids") \
  <(printf '%s\n' "$defined_ids"))"

for state_name in \
  "Guard's spear" 'Read the strangling' Fortune Stamina Exposure
do
  rg -q "$state_name" "$profile"
  rg -q "$state_name" "$slice"
  rg -q "$state_name" "$audit"
done

rg -q 'Canonical clean route' "$audit"
rg -q 'Prepared Fortune route' "$audit"
rg -q 'Costly agility route' "$audit"
rg -q 'Locked exceptional success' "$audit"
rg -q 'Locked fatal result' "$audit"
rg -q '^## Paper-procedure play record$' "$audit"
rg -q '^## Focused revision$' "$audit"

rg -q 'adaptation/map.md' \
  stories/public_domain/howard/tower_of_the_elephant/README.md
rg -q 'playtest/slice-01.md' \
  stories/public_domain/howard/tower_of_the_elephant/README.md
rg -q 'authored-sinew-steel-solo-core-design.md' README.md

if rg -n 'TBD|TODO|FIXME|XXX|PLACEHOLDER' \
  "$map_file" "$profile" "$rules" "$sheet" "$slice" "$audit"
then
  exit 1
fi

git diff --check
```

Expected: every command exits 0, the source checksum remains unchanged, all
six deliverables are non-empty, no destination or state reference is missing,
all five route rehearsals and the paper-procedure play record exist, both
indexes point to the increment, the placeholder scan produces no matches, and
`git diff --check` produces no output.

- [ ] **Step 7: Commit the reviewed increment**

Stage only the audit, focused repairs, and index changes:

```bash
git add \
  README.md \
  stories/public_domain/howard/tower_of_the_elephant/README.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/quick-rules.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/adventure-sheet.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md \
  stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01-audit.md
git diff --cached --check
git commit -m "docs: record Tower slice playtest"
git status --short --branch
```

Expected: the commit succeeds and the worktree is clean. Do not push until the
user has reviewed the implemented increment.

## Increment completion gate

Stop after Task 5. Present the map, story profile, quick rules, adventure sheet,
playable slice, audit, route results, and residual questions for user review.

Do not begin:

- the roof, Taurus-death, or spider slice;
- full-story passage authoring;
- a machine-readable passage/state format;
- automated validators;
- deterministic play tools;
- PDF, web, or application build work; or
- AI-facilitator design.

Those are separate increments informed by actual review of this paper slice.
