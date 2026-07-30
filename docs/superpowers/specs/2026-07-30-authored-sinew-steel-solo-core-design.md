# Authored S&S Solo Core and *Tower of the Elephant* Design

## Status

Approved in collaborative design on 30 July 2026. This document records the
approved system direction and the first story profile. It awaits Barry W.
Brook's review as a written specification before implementation planning.

## Purpose

Create a compact, GM-less gamebook system derived from *Sinew & Steel*. The
system must support a complete book playable with paper, a record sheet, a pen,
and one or two d20s. Its first development and playtest vehicle is Robert E.
Howard's *The Tower of the Elephant*, with the reader playing a mechanically
fixed Conan.

The repository will ultimately support two modes of play from one authored
work:

1. a published Markdown, online, or print gamebook; and
2. an optional repository companion comprising deterministic Python tools and
   a bounded AI facilitator.

The book remains complete and authoritative. The companion improves
bookkeeping, accessibility, authoring validation, and conversational play
without becoming a second source of story truth.

## Design goals

- Preserve the decision grammar and recognisable core of *Sinew & Steel*.
- Let authored passages perform the judgement formerly supplied by the
  Custodian.
- Keep dice sparse, consequential, visible, and honest.
- Make Conan exceptional across several domains while keeping him mortal.
- Treat combat as a changing narrative problem rather than a repeated attack
  loop.
- Preserve the source's causal, character, thematic, tonal, linguistic, and
  historical identity.
- Give player choices material consequences even when branches later
  reconverge.
- Track only state that a later passage consumes.
- Keep the source representation independent of final presentation.
- Make the eventual companion optional and provider-neutral.
- Maintain an auditable line from every retained rule to both its parent RPG
  function and its story function.

## Non-goals

The first design does not provide:

- reader character creation or point-buy;
- enemy stat blocks or opposed rolls;
- a universal round-by-round combat subsystem;
- dynamic armour soak or weapon-edge arithmetic;
- a general six-item carry limit or Wealth ledger;
- milestones or advancement during *Tower*;
- player-facing Iron & Ruin sorcery rules;
- a complete open-world or campaign-persistence system;
- a passage file schema selected before a real passage slice exists;
- a mandatory application, hosted service, model provider, or API integration;
- AI authority to invent canon, passages, choices, or consequences; or
- a guarantee that failed characters survive.

## Approaches considered

### Quickstart minus the Custodian

This approach would retain most tabletop procedures and replace Custodian
instructions with passage text. It offers strong RPG compatibility but carries
opposed rolls, enemy statistics, repeated combat, edge, soak, and excess
bookkeeping into a form where authored prose can do the same work more cleanly.

### Mostly diceless capability gates

This approach would reduce the game to choices, tags, items, and deterministic
conditions. It offers very low overhead and strong source control but discards
too much of *Sinew & Steel*'s identity, especially transparent ability,
Fortune, and the tension of consequential uncertainty.

### Authored S&S solo core

This is the approved approach. It retains roll-under resolution,
Advantage/Disadvantage, functional margin, Fortune, Stamina, and a
source-responsive Pressure interface. It replaces open-ended adjudication and
opposition procedures with player-facing rolls and authored consequence
passages.

## Architecture

The system has three logical layers.

### Authored S&S solo core

The stable layer shared by adaptations defines:

- d20 roll-under resolution;
- natural 1 and natural 20;
- Advantage and Disadvantage;
- functional margin;
- post-roll Fortune expenditure;
- authored Stamina loss and recovery;
- the interface for one visible 0-5 Pressure track;
- fiction-first lethality;
- sparse semantic state; and
- authored tactical exchanges.

### Story profile

Each adaptation defines:

- the playable protagonist and fixed or selectable profile;
- the lethality level;
- the meaning, triggers, thresholds, crisis, and release of Pressure;
- plausible Fortune and Stamina recovery;
- important possessions and story marks;
- narrative invariants, decision seams, elastic intervals, and
  counterfactual boundaries;
- combat and hazard traits; and
- canonical and alternative ending policy.

A fixed protagonist is therefore a *Tower* decision rather than a mandatory
rule for every later adaptation.

### Passage graph

The passage graph contains the authored scenes, choices, conditions,
resolutions, state effects, and endings. It is a directed graph coupled to a
small state machine.

The standard passage flow is:

`current state -> informed choice -> direct result or consequential roll -> optional Fortune spend -> authored consequence -> state update -> next passage`

The prose performs the work formerly handled by the Custodian: stating stakes,
interpreting position, applying Advantage or Disadvantage, resolving
opposition, and selecting consequences.

## Reader-facing resolution

### When to roll

A choice resolves without dice when Conan's success follows from established
competence, preparation, or circumstances. A consequential roll occurs only
when:

1. execution remains genuinely uncertain; and
2. success and failure both produce meaningful authored results.

Dice do not grant permission to perform routine actions. Informed player
choices establish Conan's method and fictional position before a roll.

### Basic test

1. Roll one d20.
2. The test succeeds when the result is equal to or below the named attribute.
3. Margin equals `attribute - roll`.
4. Apply any optional Fortune spend.
5. Follow the passage instruction for the final result.

The choice or passage identifies the tested attribute and states the stakes
before the roll.

### Advantage and Disadvantage

- With Advantage, roll two d20s and keep the lower result.
- With Disadvantage, roll two d20s and keep the higher result.

Prior preparation, a fitting method, useful equipment, knowledge, or strong
position can grant Advantage. Compromised position, hubris, injury, or a badly
suited method can impose Disadvantage. Additive situational modifiers remain
outside the core.

### Natural results

- A natural 1 receives an exceptional authored outcome.
- A natural 20 receives the worst credible authored outcome.
- Neither result can be changed with Fortune.

The natural 20 consequence follows the stated stakes. A mortal hazard may
therefore make it fatal.

### Functional margin

Margin always shows how far the roll succeeded or failed and prices a Fortune
intervention. The system does not impose universal strong-success,
partial-success, or severe-failure bands.

An individual passage may read a specified success margin when degree has a
concrete story function. Such thresholds are exceptional and must earn their
additional branch.

## Fortune

Fortune retains its central *Sinew & Steel* function.

- Current Fortune is both a spendable pool and the target for a pure-chance
  Fortune test.
- After seeing a roll, the reader may spend one Fortune for each point by which
  the chosen die is adjusted.
- The attribute target is captured when the roll is made; any Fortune cost is
  deducted after that roll resolves.
- Natural 1 and natural 20 are locked.
- Spending Fortune now weakens later tests of pure fate.
- Recovery is scarce, explicitly authored, and never assumed.

For the normal roll-under procedure, useful expenditure lowers a result toward
or below the target. A passage may also allow Fortune to deepen a successful
margin when it explicitly consumes that margin.

## *Tower of the Elephant* protagonist profile

The reader plays the young but already seasoned Conan depicted in the story:

`BRN 13 | AGI 12 | CUN 12 | WIL 12 | FOR 10/10 | STM 6/6`

The profile uses exact *Sinew & Steel* accounting:

- Iron & Ruin pulp starting budget: 12 build points;
- four prior milestones: 8 build points;
- total: 20 build points.

The allocation is:

| Score | Increase from baseline | Cost |
| --- | ---: | ---: |
| Brawn 13 | +3 | 6 |
| Agility 12 | +2 | 4 |
| Cunning 12 | +2 | 4 |
| Will 12 | +2 | 4 |
| Fortune 10 | +0 | 0 |
| Stamina 6 | +1 | 2 |
| **Total** |  | **20** |

The four milestones abstract decisive development through Conan's Cimmerian
upbringing and early adventures. They need not correspond one-to-one with four
complete stories.

Conan's exceptional quality is breadth. Every active attribute is above
baseline and he has increased Stamina, yet none of his active abilities makes
success automatic. Fortune depletion, harm, Pressure, Disadvantage, natural
20s, and lethal choices preserve his mortality.

## Harm, recovery, and lethality

### Authored Stamina loss

Passages assign harm directly:

- 1 Stamina for an ordinary injury;
- 2 Stamina for a serious injury;
- 3 Stamina for a devastating injury; or
- immediate death when a failed hazard is credibly fatal.

Zero Stamina ends the adventure. There are no death saves, emergency rebound
rules, or automatic recovery from zero.

### Recovery

Recovery requires a specific, plausible opportunity in the fiction:

- normally restore 1 Stamina;
- exceptionally restore 2 with meaningful treatment, safety, and time;
- never exceed the maximum; and
- never refill all Stamina merely because Conan rests.

The same scarcity principle applies to Fortune recovery.

### Fiction-first lethality

*Tower* sits between mixed consequences and hard pulp.

- Stakes are stated before consequential rolls.
- A credibly mortal risk may send a failed result directly to a death ending.
- Other failures may cause harm, lost position, increased Pressure, a lost
  opportunity, resource loss, or a more dangerous route.
- The author has no obligation to preserve every route or rescue every failed
  character.

The reusable core permits other story profiles to choose a different
lethality level.

## Story-defined Pressure

Every story profile defines one visible 0-5 Pressure track. *Tower* will not
reuse Iron & Ruin's spellcaster-facing Doom unchanged because Conan abhors and
does not practise sorcery.

The *Tower* source map will determine:

- the track's name;
- what accumulating pressure means;
- which authored events increase or reduce it;
- what its thresholds change;
- what crisis occurs at 5; and
- what, if anything, can release and reset it.

Pressure does not advance through a generic timer or arbitrary die result. At
5 it triggers a contextual authored escalation. It resets only when the
fiction genuinely releases that pressure.

Deferring the exact name and crisis until source mapping is deliberate: the
mechanic must arise from recurring pressures in the story rather than precede
their analysis.

## Authored tactical exchanges

Combat remains part of the passage graph instead of entering a separate
minigame.

### Minor conflicts

A minor or incidental conflict normally resolves through one informed choice
and, where needed, one consequential player-facing roll.

### Major conflicts

A major set piece normally uses two to four authored tactical exchanges. Each
exchange:

- presents a changed tactical situation;
- offers materially different methods, objectives, risks, or sacrifices;
- may read relevant possessions, marks, Stamina, Fortune, or Pressure;
- uses at most one player-facing roll;
- authors both Conan's effect and the opponent's response; and
- changes the next situation rather than repeating the same attack.

Success may end the fight, improve position, expose an opportunity, protect an
ally, or secure another objective. Failure may inflict authored harm, worsen
position, remove an option, raise Pressure, permit escape at a cost, or kill
Conan when the stakes are mortal.

Enemies have author-facing traits, motives, dangers, and fictional
capabilities. They do not have reader-facing attributes, attack rolls, armour,
or hit-point ledgers.

## Sparse semantic state

The adventure sheet contains:

- Conan's fixed profile;
- current and maximum Fortune;
- current and maximum Stamina;
- the current story Pressure value;
- a short possessions area; and
- a short story-marks area.

Possessions, knowledge, relationships, injuries, and conditions are recorded
only when later passages read them. Marks use meaningful player-facing
language rather than opaque codes wherever revealing the condition does not
spoil discovery.

There is no general carry limit. A passage may still force a concrete choice
between bulky or mutually exclusive possessions when the fiction warrants it.

Every recorded state needs at least one future consumer. Every state
requirement needs at least one prior producer on a reachable route.

## Adaptation method

### Source mapping

Before passage design, annotate the source for:

- **narrative invariants:** defining events, revelations, relationships, and
  images;
- **decision seams:** moments where agency can naturally transfer to the
  reader;
- **elastic intervals:** scenes whose method, route, or consequence can vary;
  and
- **counterfactual boundaries:** departures beyond which the result ceases to
  represent the source work.

The map also identifies hazards, information transitions, relationships,
potential state, recovery opportunities, and recurring pressures.

### Canonical centre with earned alternatives

Howard's ending is the richest complete resolution of *Tower*. Credible player
choices may produce other endings, including escape, refusal, partial victory,
failure, and death.

Branches may reconverge where a defining event exerts canonical pressure.
When they do, earlier choices remain material through changed cost, knowledge,
possessions, relationships, position, available choices, or prose
acknowledgement.

The adaptation protects causal, character, thematic, tonal, linguistic, and
historical fidelity. Available choices must remain credible actions for Conan,
and the mechanics must reinforce the story's actual pressures rather than
turning it into a generic dungeon adventure.

## Passage contract

This design does not yet select a storage schema. Conceptually, every passage
must supply enough information to determine:

- its stable identifier;
- its player-facing prose;
- which choices are visible and legal;
- what state each conditional choice reads;
- whether a choice resolves directly or calls for a consequential test;
- the tested attribute, roll mode, and stated stakes when a test occurs;
- any permitted margin threshold;
- the result-specific state changes;
- the next passage or terminal ending; and
- the provenance of any retained or adapted source wording where required.

A choice never hides an unannounced universal rule. A terminal result is
explicit. State updates occur before the next passage reads them.

The eventual representation must support Markdown or print output and
deterministic tooling without making either presentation the source of truth.

## Publication and companion architecture

### Published gamebook

The book is wholly playable without Python, a repository, an account, a hosted
service, or AI. It contains the complete reader-facing rules, record sheet,
passage text, conditions, state updates, rolls, and endings.

### Deterministic Python harness

After a paper-playable passage slice stabilises the passage contract, local
tools may:

- display the current passage and legal choices;
- accept a physical roll or generate and display an auditable roll;
- calculate margin and Fortune costs;
- apply Fortune, Stamina, Pressure, possessions, and story marks;
- enforce conditions and terminal results;
- save and resume a playthrough;
- produce a reproducible play log;
- expose machine-readable operations for agents; and
- support structural and probabilistic validation.

Invalid choices, malformed state, and impossible transitions fail with a clear
diagnostic. The harness does not guess outcomes or silently repair state.
Runtime play state remains local and untracked by default.

### Bounded AI facilitator

A provider-neutral agent guide may support Codex, Claude Code, and comparable
tools without initially requiring a model API integration.

The facilitator may:

- present reached authored prose and legal choices;
- accept natural-language intent and map it to an authored choice;
- ask for confirmation when that mapping is ambiguous;
- answer spoiler-safe rules questions;
- explain Conan's currently known situation and recorded state;
- provide concise recaps of reached material;
- accept physical rolls or call deterministic roll tools; and
- apply state only through deterministic operations.

The facilitator may not:

- invent plot facts, passages, exits, choices, or consequences;
- rewrite Howard-derived or newly authored canonical prose;
- reveal unread passages, hidden conditions, or unavailable choices;
- select an outcome outside the authored resolution;
- fudge a roll or silently change state;
- rescue a fatal result; or
- treat model memory as the authoritative play state.

Conversational intent routing is the primary initial enhancement. Adaptive
story generation remains an experimental future mode and must not share the
canonical rules contract unless separately designed and approved.

## Validation and playtesting

### Structural validation

Automated checks should identify:

- missing or duplicate passage identifiers;
- invalid links and conditions;
- unintended unreachable passages;
- state read before any reachable producer;
- state written without any future consumer;
- non-terminal passages with no legal continuation;
- illegal or out-of-range resource updates;
- legal and reachable endings; and
- at least one viable canonical route.

Deliberately unreachable authoring notes or test fixtures must be explicitly
classified rather than silently ignored.

### Mechanical validation

Deterministic tests should cover:

- straight, Advantage, and Disadvantage roll selection;
- success and failure boundaries;
- margin calculation;
- locked natural 1 and natural 20;
- Fortune availability, expenditure, and recovery;
- the timing of Fortune tests and post-roll expenditure;
- authored Stamina loss, recovery caps, and zero-Stamina death;
- Pressure bounds and story-defined crisis behaviour;
- conditional possessions and story marks; and
- save/resume equivalence.

Seeded simulations can estimate route survival, check frequency, Fortune
depletion, Stamina attrition, Pressure distribution, ending frequency, and
legal-route viability. Simulation informs balance; it cannot judge prose,
choice quality, source fidelity, tactical interest, or perceived fairness.

### Human playtesting

The first tranche requires:

- paper play with the printed reader-facing rules;
- deterministic harness replay of the same routes once the harness exists;
- blind readers who have and have not read the source;
- checks for arbitrary choices, cosmetic reconvergence, mandatory hidden
  builds, excessive bookkeeping, repetitive combat, and unfair lethal stakes;
  and
- comparison of canonical and alternative endings for thematic completeness.

## Delivery sequence

1. Complete and approve this solo-core specification.
2. Map *The Tower of the Elephant* for invariants, seams, elastic intervals,
   boundaries, hazards, state, recovery, and Pressure candidates.
3. Design and paper-playtest a representative passage slice containing at
   least one direct choice, one consequential roll, one Fortune decision, one
   state dependency, and one authored tactical exchange.
4. Revise the rules and passage contract from real play.
5. Stabilise the smallest technology-neutral passage/state representation.
6. Add graph, state, and mechanical validation.
7. Add deterministic play tools.
8. Add the bounded AI facilitator.
9. Consider adaptive experiments only after canonical book and harness play
   are stable.

## Planning boundary

This document is the umbrella architecture for the dual-mode project, not
authority to implement every layer in one batch.

The next implementation plan should cover only source mapping, design of a
representative paper-playable passage slice, and the focused rule revision
needed to play that slice. It should stop before selecting a passage schema or
building runtime tools.

The structured representation and deterministic harness form a later design
and implementation increment informed by the tested slice. The AI facilitator
forms another later increment informed by the stable deterministic contract.
Each increment requires its own acceptance checks and user approval.

## Deliberate deferrals

The following are later design decisions, not omissions or placeholders:

- *Tower*'s Pressure name, triggers, thresholds, crisis, and possible release
  await source mapping.
- The exact passage and state file format awaits the representative passage
  slice.
- Markdown, PDF, web, or application build tooling awaits a real publication
  artefact.
- Detailed AI prompts and tool interfaces await a stable deterministic
  contract.
- Cross-story character persistence awaits evidence that adapted protagonists
  and chronologies need it.
- Artwork, typography, page layout, and commercial release packaging remain
  outside this system increment.

## Acceptance criteria

The design has been implemented successfully when:

1. a reader can play the representative slice with paper, a record sheet, a
   pen, and d20s;
2. its rules match this specification and contain no tabletop-only residue;
3. Conan's fixed profile and 20-point provenance are explicit;
4. consequential rolls, Fortune, Stamina, Pressure, state, and tactical
   exchanges each perform observable narrative work;
5. lethal stakes are telegraphed and applied without a universal rescue rule;
6. the canonical route and at least one earned alternative are viable;
7. every tracked state has a reachable producer and consumer;
8. structural and mechanical checks pass;
9. later deterministic play reproduces the paper result from the same choices,
   rolls, and state; and
10. the optional AI facilitator can run the deterministic flow without gaining
    authority over prose, rules, hidden information, or outcomes.
