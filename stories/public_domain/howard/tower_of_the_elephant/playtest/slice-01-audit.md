# Outer Wall Slice Audit

## Scope

This audit covers the paper-playable infiltration slice in
[`slice-01.md`](slice-01.md), its
[`quick-rules.md`](quick-rules.md), and its
[`adventure-sheet.md`](adventure-sheet.md). It checks the fourteen `S`
passages and three `E` endings against the approved
[`map.md`](../adaptation/map.md) and
[`story-profile.md`](../adaptation/story-profile.md). The source is
[`source.md`](../source.md), SHA-256
`416115fed82458a855d2c2c7f37f29c3b4c8b2747618ef18bcbed2d821d0df1f`.

The slice begins with Conan outside the outer wall at source line 72 and stops
when Taurus's rope is secured at line 188. It does not audit or imply any
upper-tower continuation. The procedure evidence comprises five deterministic
route rehearsals and one context-isolated digital reader-only play on 31 July
2026. The latter was not a human, physical-paper, physical-dice, or blind-reader
test.

## Source crosswalk

Every passage below is anchored within source lines 72-188 or is identified as
an authored consequence of a decision drawn from those lines. No later chapter
or source line is used as foreknowledge.

| Passage | Source line or authored-consequence basis | Treatment |
| --- | --- | --- |
| `S01` | Lines 72-78 | Conan measures the wall, remembers Yara's dangers, and hears the measured guard. Climbing now or waiting transfers the hesitation to the reader. |
| `S02` | Lines 78-80; authored consequence of waiting | The missing return patrol is direct. The added Exposure is the authored cost of spending another patrol interval outside. |
| `S03` | Lines 80-86 | Conan crosses, finds the fresh strangled guard, sees the spear, and detects movement. |
| `S04` | Lines 84-86; authored discovery branch | The spear and strangling evidence are direct. Taking exactly one discovery is an authored cost for delaying pursuit. |
| `S05` | Lines 86-88 and 110-124; authored approach results | Conan stalks a human ambusher and later reads Taurus's handling of the corpse. The quiet recognition, call, Cunning test, harm, and Exposure costs author the approach seam. |
| `S06` | Lines 86-134 | The standoff, Taurus's identity and reputation, the guard discussion, and the prepared upper route are direct adaptations. |
| `S07` | Lines 104-134; authored refusal boundary | Taurus proposes an alliance and Conan accepts in the source. Acceptance remains canonical; withdrawal is the declared counterfactual. |
| `S08` | Lines 132-142 | Conan removes his sandals, follows Taurus over the inner wall, and learns about the sealed lower tower. |
| `S09` | Lines 140-150 | The garden's hunting menace, Taurus's copper tube, and the visible lions are direct. |
| `S10` | Lines 150-168 | Taurus uses the black lotus, waits for the still-air cloud to disperse, finds five dead lions, and confirms that the powder is spent. |
| `S11` | Lines 170-184; authored tactical methods and costs | The rope cast, sixth silent lion, Conan's response, possible noise, and mortal danger are direct. Spear, sword, and agility methods transfer Conan's response to the reader. |
| `S12` | Lines 176-188 | Conan kills the lion, Taurus helps and marvels, Conan cleans his sword, and the rope is ready. Method-specific acknowledgement is authored. |
| `S13` | Authored costly consequence of lines 176-184 | Injury and disturbance make a non-clean victory concrete while preserving the lion's death and continued ascent. |
| `S14` | Lines 170-188 | Taurus casts and tests the hooked rope; its security marks the selected slice boundary. |
| `E01` | Authored consequence of refusing the alliance in lines 104-134 | Conan survives but abandons Taurus, the upper route, and the defining theft. |
| `E02` | Authored consequence of delay, an exposed body, search logic, and possible noise in lines 78-84, 122-130, and 170-184 | Accumulated Exposure turns the quiet breach into a discovered, failed attempt. |
| `E03` | Authored fatal consequence of the standoff and silent-lion hazards in lines 86-88 and 176-184 | Zero Stamina or the lion's locked natural 20 ends the attempt in death. |

## Passage and edge inventory

The slice contains 17 unique defined IDs: `S01`-`S14` and `E01`-`E03`, with no
duplicate heading. Its 47 printed destination instructions collapse to 27
unique directed edges. The entry instruction to begin at `S01` is not an edge.

| Passage | Unique outgoing edges | Condition or purpose |
| --- | --- | --- |
| `S01` | `S01 -> S02`; `S01 -> S03` | Wait with Exposure +1, or climb now. |
| `S02` | `S02 -> S03` | End the extra patrol interval and climb. |
| `S03` | `S03 -> S04`; `S03 -> S05` | Examine the corpse, or pursue immediately. |
| `S04` | `S04 -> S05` | Record exactly one discovery, then confront the mover. |
| `S05` | `S05 -> S06`; `S05 -> E02`; `S05 -> E03` | Resolve recognition, calling, or stalking; crisis exits follow applied state. |
| `S06` | `S06 -> S07` | Reveal Taurus and hear his offer. |
| `S07` | `S07 -> S08`; `S07 -> E01`; `S07 -> E02` | Accept, withdraw, or obey an already-triggered Exposure crisis. |
| `S08` | `S08 -> S09`; `S08 -> E02` | Cross the inner wall unless discovery has ended the breach. |
| `S09` | `S09 -> S10`; `S09 -> E02` | Trust Taurus unless discovery has ended the breach. |
| `S10` | `S10 -> S11`; `S10 -> E02` | Wait for the lotus cloud, then advance unless discovery intervenes. |
| `S11` | `S11 -> S12`; `S11 -> S13`; `S11 -> E02`; `S11 -> E03` | Resolve a clean, costly, discovered, or fatal lion result. |
| `S12` | `S12 -> S14` | Acknowledge a clean kill and resume the rope cast. |
| `S13` | `S13 -> S14`; `S13 -> E02`; `S13 -> E03` | Confirm previously applied costs before continuing. |
| `S14` | None | Successful slice boundary. |
| `E01` | None | Withdrawal ending. |
| `E02` | None | Exposure ending. |
| `E03` | None | Death ending. |

All 27 destinations are defined. Each non-terminal passage has at least one
continuation. All four terminal outcomes are reachable:

- `S14` is reached by the successful routes rehearsed below.
- `E01` is reached by withdrawing at `S07`.
- `E02` is reached, for example, by waiting at `S01` (Exposure 1), taking a
  natural 20 while stalking at `S05` (Exposure 3), then failing the agility
  method at `S11` (Exposure 5).
- `E03` is reached by any selected natural 20 at `S11`.

## State producer-consumer audit

| State | Producer | Consumer | Removal or terminal handling |
| --- | --- | --- | --- |
| Sword | Starting possession | Sword methods at `S11`; retained-state instruction at `S14` | Not consumed in this slice. |
| `Guard's spear` | Take it at `S04` | Spear method at `S11`; retained-state instruction at `S14` if unused | Crossed off before the `S11` roll. |
| `Read the strangling` | Read the corpse at `S04` | Quiet recognition at `S05` | Crossed off when recognition is used. |
| Fortune | Starts at 10 | Optional post-selection spend on ordinary dice at `S05` and `S11`; final state at `S14` | Deduct the spend after the captured test resolves. Locked natural results forbid a spend. |
| Stamina | Starts at 6; losses occur at `S05` and `S11` | Damage and crisis checks at `S05`, `S11`, and `S13`; final state at `S14` | A damaging result that reaches 0 goes to `E03`; no recovery occurs. |
| Exposure | Starts at 0; increases at `S01`, `S05`, and `S11` | Update/crisis checks at `S05` and `S11`; threshold or urgency text at `S07`, `S08`, `S09`, `S10`, and `S13`; final state at `S14` | Exposure 5 goes to `E02`; it is not reduced in the slice. |

The two conditional S04 states each have a reachable prior producer and a
future consumer. They are mutually exclusive. The static attributes have a
starting value before either test. Every resource update is applied before the
destination reads the new value. No written possession, story mark, or resource
lacks a later read or retained-state instruction, and no conditional method
lacks a prior producer.

The Task 5 brief's state-table sketch names Exposure thresholds in `S03`,
`S08`, `S10`, and `S13`. `S03` is inconsistent with legal reachability:
incoming Exposure there can only be 0 after an immediate climb or 1 after
waiting, and `S03` neither raises Exposure nor contains a choice that a 3 or 4
threshold could close. Adding an `S03` threshold would therefore be unreachable
boilerplate. The accepted reader file instead checks the updates where they
occur and carries reachable urgency acknowledgement through `S07`-`S10` and
`S13`. The required `S08`, `S10`, and `S13` acknowledgement remains present;
no profile or edge has been changed to manufacture an `S03` consumer.

## Mechanical coverage

| Feature | Evidence in the slice | Rehearsal or reachability evidence |
| --- | --- | --- |
| Fixed Conan and starting state | Rules and sheet print BRN 13, AGI 12, CUN 12, WIL 12, Fortune 10, Stamina 6, Exposure 0, and Sword | Every rehearsal begins from the same state. |
| Informed direct choices | `S01`, `S03`, `S04`, `S05`, `S07`, and `S11` state route or method consequences | All five rehearsals record each commitment. |
| Standard roll-under | CUN 12 at `S05`; BRN 13 or AGI 12 at `S11` | Routes 1-3 cover success, Fortune conversion, and ordinary failure. |
| Advantage selection | Spear method rolls two dice and keeps the lower | Route 2 keeps 9 from 17 and 9; the reader-only run keeps 6 from 6 and 20. |
| Margin | Attribute minus selected die, recomputed after Fortune | Routes 1-3 record positive, zero after spend, and negative margins. |
| Fortune timing | Spend only after selecting an ordinary die; deduct after the captured test | Route 2 spends 3 after raw 15; route 3 declines; routes 4-5 confirm locked dice. |
| Natural 1 | Exceptional authored result at `S11` | Route 4 goes through the exceptional kill to `S12`. |
| Natural 20 | Worst credible result; mortal at `S11`; Fortune forbidden | Route 5 goes directly to `E03`. |
| Stamina | Authored losses at `S05` and `S11`; death at 0 | Route 3 loses 1. A direct natural-20 death covers the slice's reachable fatal result. |
| Exposure | Delay, noise, standoff, and lion costs; crisis at 5 | Routes 2-3 retain Exposure 1 and 3. The reachability example above reaches `E02`. |
| Sparse state | S04 produces one of two states and later prose consumes it | Route 1 consumes the mark; route 2 consumes the spear. |
| Tactical exchange | Three distinct `S11` methods, one test each, with method-specific costs | Routes 1-5 cover sword, spear, agility, ordinary success/failure, and both locked naturals. |
| Terminal handling | `S14`, `E01`, `E02`, and `E03` explicitly stop their route | Successful and fatal terminals are rehearsed; refusal and discovery are structurally reachable. |

Disadvantage, WIL tests, Fortune tests, passage-specific margin bands, and
recovery are not used in this representative slice. The profile deliberately
provides no recovery here. A Stamina-zero transition is printed consistently
but cannot be reached from Stamina 6 using only the two non-fatal damaging
events in this slice; `E03` remains reachable through the lion's selected
natural 20.

## Deterministic route rehearsals

Each rehearsal resets to Fortune 10, Stamina 6, Exposure 0, Sword, and no story
marks. In the tables, `F/S/X` means current Fortune/Stamina/Exposure. A dash in
the die column means that the passage calls for no roll. Every destination is
the instruction followed from the named passage.

### Canonical clean route

| From | Choice or procedure | Raw and selected die; margin; Fortune | State update and resulting state | Destination |
| --- | --- | --- | --- | --- |
| `S01` | Climb immediately while the guard's position is known. | — | None; `F/S/X 10/6/0`, Sword, no mark | `S03` |
| `S03` | Examine the corpse. | — | None; `10/6/0`, Sword, no mark | `S04` |
| `S04` | Read the strangling rather than take the spear. | — | Add `Read the strangling`; `10/6/0`, Sword, mark recorded | `S05` |
| `S05` | Use the mark for quiet recognition. | — | Cross off `Read the strangling`; `10/6/0`, Sword, no active mark | `S06` |
| `S06` | Hear Taurus's mandatory alliance offer. | — | None; `10/6/0`, Sword | `S07` |
| `S07` | Accept Taurus as an ally. | — | None; `10/6/0`, Sword | `S08` |
| `S08` | Cross the inner wall with Taurus. | — | None; `10/6/0`, Sword | `S09` |
| `S09` | Trust Taurus and give him room. | — | None; `10/6/0`, Sword | `S10` |
| `S10` | Wait for the lotus cloud to disperse, then advance. | — | No recovery; `10/6/0`, Sword | `S11` |
| `S11` | Wheel beneath the leap with the Sword; test BRN 13. | Raw 8; selected 8; provisional and final margin `13 - 8 = +5`; spend 0 Fortune | Clean success, no cost; `10/6/0`, Sword | `S12` |
| `S12` | Acknowledge the clean kill and continue. | — | None; `10/6/0`, Sword | `S14` |
| `S14` | Stop at the successful slice boundary. | — | Recover nothing; final `F/S/X 10/6/0`, Sword, no mark | Slice complete |

Outcome: `S14` with Fortune 10, Stamina 6, and Exposure 0, exactly as
specified.

### Prepared Fortune route

| From | Choice or procedure | Raw and selected die; margin; Fortune | State update and resulting state | Destination |
| --- | --- | --- | --- | --- |
| `S01` | Wait through another patrol interval. | — | Exposure +1; `F/S/X 10/6/1`, Sword | `S02` |
| `S02` | Climb after the broken interval. | — | None; `10/6/1`, Sword | `S03` |
| `S03` | Examine the corpse. | — | None; `10/6/1`, Sword | `S04` |
| `S04` | Take the guard's spear. | — | Add `Guard's spear`; `10/6/1`, Sword and spear | `S05` |
| `S05` | Stalk the stranger; test CUN 12. | Raw 15; selected 15; provisional margin `12 - 15 = -3`; spend 3 Fortune to make final die 12 and final margin 0 | Deduct Fortune after resolution; no harm or Exposure; `7/6/1`, Sword and spear | `S06` |
| `S06` | Hear Taurus's mandatory alliance offer. | — | None; `7/6/1`, Sword and spear | `S07` |
| `S07` | Accept Taurus as an ally. | — | None; `7/6/1`, Sword and spear | `S08` |
| `S08` | Cross the inner wall with Taurus. | — | None; `7/6/1`, Sword and spear | `S09` |
| `S09` | Trust Taurus and give him room. | — | None; `7/6/1`, Sword and spear | `S10` |
| `S10` | Wait for the lotus cloud to disperse, then advance. | — | No recovery; `7/6/1`, Sword and spear | `S11` |
| `S11` | Brace the spear; cross it off before rolling BRN 13 with Advantage. | Raw 17 and 9; selected 9; provisional and final margin `13 - 9 = +4`; spend 0 Fortune | Spear consumed before the roll; clean success; `7/6/1`, Sword, spear crossed off | `S12` |
| `S12` | Leave the broken or buried spear and continue. | — | None; `7/6/1`, Sword, spear crossed off | `S14` |
| `S14` | Stop at the successful slice boundary. | — | Recover nothing; final `F/S/X 7/6/1`, Sword, spear consumed, no mark | Slice complete |

Outcome: `S14` with Fortune 7, Stamina 6, Exposure 1, and the spear consumed,
exactly as specified.

### Costly agility route

| From | Choice or procedure | Raw and selected die; margin; Fortune | State update and resulting state | Destination |
| --- | --- | --- | --- | --- |
| `S01` | Climb immediately. | — | None; `F/S/X 10/6/0`, Sword | `S03` |
| `S03` | Pursue the movement and leave the corpse unread. | — | No discovery; `10/6/0`, Sword | `S05` |
| `S05` | Call out without the mark. | — | Exposure +1; `10/6/1`, Sword | `S06` |
| `S06` | Hear Taurus's mandatory alliance offer. | — | None; `10/6/1`, Sword | `S07` |
| `S07` | Accept Taurus as an ally. | — | None; `10/6/1`, Sword | `S08` |
| `S08` | Cross the inner wall with Taurus. | — | None; `10/6/1`, Sword | `S09` |
| `S09` | Trust Taurus and give him room. | — | None; `10/6/1`, Sword | `S10` |
| `S10` | Wait for the lotus cloud to disperse, then advance. | — | No recovery; `10/6/1`, Sword | `S11` |
| `S11` | Slip aside and cut; test AGI 12. | Raw 14; selected 14; provisional and final margin `12 - 14 = -2`; decline Fortune and spend 0 | Ordinary failure: Stamina -1 and Exposure +2; `10/5/3`, Sword | `S13` |
| `S13` | Confirm the already-applied cost and advance. | — | Do not apply the cost twice; `10/5/3`, Sword | `S14` |
| `S14` | Stop at the successful slice boundary. | — | Recover nothing; final `F/S/X 10/5/3`, Sword, no mark | Slice complete |

Outcome: `S14` with Fortune 10, Stamina 5, and Exposure 3, exactly as
specified.

### Locked exceptional success

This rehearsal uses the canonical `Read the strangling` prelude and the
always-available Sword method so that only the natural result differs from the
clean route.

| From | Choice or procedure | Raw and selected die; margin; Fortune | State update and resulting state | Destination |
| --- | --- | --- | --- | --- |
| `S01` | Climb immediately. | — | None; `F/S/X 10/6/0`, Sword | `S03` |
| `S03` | Examine the corpse. | — | None; `10/6/0`, Sword | `S04` |
| `S04` | Record `Read the strangling`. | — | Add mark; `10/6/0`, Sword, mark recorded | `S05` |
| `S05` | Consume the mark for quiet recognition. | — | Cross off mark; `10/6/0`, Sword | `S06` |
| `S06` | Hear Taurus's offer. | — | None; `10/6/0`, Sword | `S07` |
| `S07` | Accept Taurus. | — | None; `10/6/0`, Sword | `S08` |
| `S08` | Cross with Taurus. | — | None; `10/6/0`, Sword | `S09` |
| `S09` | Trust Taurus. | — | None; `10/6/0`, Sword | `S10` |
| `S10` | Wait for the cloud and advance. | — | No recovery; `10/6/0`, Sword | `S11` |
| `S11` | Wheel beneath the leap with the Sword; test BRN 13. | Raw 1; selected natural 1; arithmetic margin `13 - 1 = +12`, resolution-inert because the natural 1 is locked; spend 0 Fortune | Exceptional clean kill with no cost; `10/6/0`, Sword | `S12` |
| `S12` | Follow the exceptional kill prose and continue. | — | None; `10/6/0`, Sword | `S14` |
| `S14` | Stop at the successful slice boundary. | — | Recover nothing; final `F/S/X 10/6/0`, Sword | Slice complete |

Outcome: the locked natural 1 spends no Fortune, reaches `S12` through the
exceptional result, and then reaches `S14`, exactly as specified.

### Locked fatal result

This rehearsal repeats the same legal prelude and Sword method, isolating the
selected natural 20.

| From | Choice or procedure | Raw and selected die; margin; Fortune | State update and resulting state | Destination |
| --- | --- | --- | --- | --- |
| `S01` | Climb immediately. | — | None; `F/S/X 10/6/0`, Sword | `S03` |
| `S03` | Examine the corpse. | — | None; `10/6/0`, Sword | `S04` |
| `S04` | Record `Read the strangling`. | — | Add mark; `10/6/0`, Sword, mark recorded | `S05` |
| `S05` | Consume the mark for quiet recognition. | — | Cross off mark; `10/6/0`, Sword | `S06` |
| `S06` | Hear Taurus's offer. | — | None; `10/6/0`, Sword | `S07` |
| `S07` | Accept Taurus. | — | None; `10/6/0`, Sword | `S08` |
| `S08` | Cross with Taurus. | — | None; `10/6/0`, Sword | `S09` |
| `S09` | Trust Taurus. | — | None; `10/6/0`, Sword | `S10` |
| `S10` | Wait for the cloud and advance. | — | No recovery; `10/6/0`, Sword | `S11` |
| `S11` | Wheel beneath the leap with the Sword; test BRN 13. | Raw 20; selected natural 20; arithmetic margin `13 - 20 = -7`, resolution-inert because the natural 20 is locked; Fortune is forbidden and spend is 0 | Direct fatal result; no Stamina arithmetic or rescue; `10/6/0` at death | `E03` |
| `E03` | Stop at the death ending. | — | Conan is dead; no recovery or continuation | Terminal |

Outcome: the locked natural 20 cannot be changed with Fortune and terminates
at `E03`, exactly as specified.

## Paper-procedure play record

### Session and evidence limits

- Date and zone: 31 July 2026, Australia/Hobart (AEST, UTC+10).
- Captured interval: 12:06:36 to 12:07:10 AEST, approximately 34 seconds of
  wall-clock time.
- Player: context-isolated Codex playtester
  `reader_only_playtest_slice_01`.
- Medium: plain digital scratch record.
- Dice: a separate `jot -r 1 1 20` invocation generated every required d20.
- Reader material: only `quick-rules.md`, `adventure-sheet.md`, and
  `slice-01.md`.

This was a digital procedure rehearsal, not a human, physical-paper,
physical-dice, or blind-reader test. The complete slice was loaded in one
line-numbered terminal output, so future passage text was technically present
before the choices were made. The player deliberately used only the current
passage's prose and announced stakes. The 34-second capture therefore does not
represent human reading, decision, or physical bookkeeping time. The run used
the accepted pre-repair reader files at commit `fcc4a42`; the later focused
revision below changes only information disclosed before two choices.

### Complete played route

| From | Choice or procedure | Roll, Fortune, and state | Destination |
| --- | --- | --- | --- |
| `S01` | Climb now; known guard position was preferable to certain Exposure. | No roll or update; `F/S/X 10/6/0`, Sword | `S03` |
| `S03` | Examine the warm, silently killed guard for useful evidence. | No roll or update; `10/6/0`, Sword | `S04` |
| `S04` | Take `Guard's spear`; its stated brace against a charging beast was the clearest announced utility. | Add spear; `10/6/0`, Sword and spear | `S05` |
| `S05` | Stalk the stranger rather than accept certain disturbance from calling. | CUN 12; raw and selected die 15; provisional margin -3; spend 3 Fortune; final die 12 and margin 0. Deduct after resolution; `7/6/0`, Sword and spear | `S06` |
| `S06` | Hear the mandatory alliance conversation. | No roll or update; `7/6/0`, Sword and spear | `S07` |
| `S07` | Accept Taurus; Conan still seeks the Heart and Exposure is 0. | No roll or update; `7/6/0`, Sword and spear | `S08` |
| `S08` | Cross the inner wall with Taurus. | No roll; no ordinary-climb test; `7/6/0`, Sword and spear | `S09` |
| `S09` | Trust Taurus's command and give him room for the copper tube. | No roll or update; `7/6/0`, Sword and spear | `S10` |
| `S10` | Wait for the poison to disperse, then advance. | No roll and no recovery; `7/6/0`, Sword and spear | `S11` |
| `S11` | Brace the spear; cross it off before rolling BRN 13 with Advantage. | Separate raw `jot` results 6 and 20; select 6. The unselected 20 has no natural effect. Provisional and final margin `13 - 6 = +7`; spend 0 Fortune. Clean success; `7/6/0`, Sword, spear consumed | `S12` |
| `S12` | Confirm the clean kill and leave the consumed spear. | No roll or update; `7/6/0`, Sword | `S14` |
| `S14` | Stop at the successful slice boundary. | Recover nothing; final `F/S/X 7/6/0`, Sword, spear consumed, no marks | Slice complete |

The run finished successfully at `S14` with Fortune 7, Stamina 6, Exposure 0,
Sword retained, `Guard's spear` consumed, and no story marks. It did not
restart or manipulate a roll.

### Rules lookups

The player read the full quick rules once before `S01`, then applied or
specifically checked every one of these lookup groups:

1. required materials, passage procedure, and recording changes;
2. the fixed profile and printed initial state;
3. test order, captured target, roll-under success, and margin at `S05` and
   `S11`;
4. Advantage selection before natural-result handling at `S11`;
5. the locks on a selected natural 1 or natural 20;
6. Fortune cost and post-resolution deduction at `S05`, checked again at
   `S11`;
7. Stamina loss, zero-Stamina death, and the lack of recovery;
8. Exposure updates, the cap, and the `E02` crisis;
9. the one-test tactical exchange and pre-roll possession consumption; and
10. terminal meanings and the stop instruction at `S14`.

No author-facing source, map, profile, plan, history, or report was used to
resolve a rule.

### Clarity and transition observations

No bookkeeping operation on the played route was unclear. The player deducted
the 3 Fortune after resolving the captured CUN 12 test, changed neither
Stamina nor Exposure on the two successes, crossed off the spear before the
`S11` roll, recorded no story mark, and retained the final state without
recovery at `S14`.

Two choice stakes were unclear before commitment in the pre-repair text:

1. `S03` said that examining the corpse would spend time but did not state a
   concrete discovery before the reader committed.
2. `S04` advertised the spear's future brace against a charging beast, while
   `Read the strangling` named a mark without stating that it enabled quiet
   recognition.

The run also identified two mechanically dominated early choices:

1. waiting at `S01` adds Exposure and reaches the same `S03` as climbing now,
   with no printed benefit; and
2. pursuing at `S03` reaches `S05` without a discovery, while examining passes
   through `S04`, grants a possession or mark at no state cost, and then reaches
   the same standoff.

The played route had forced transitions from `S06` to `S07`, `S08` to `S09`,
`S09` to `S10`, `S10` to `S11`, and `S12` to `S14`. They carry source event,
instruction, state acknowledgement, or boundary work, but offer no choice.
The two dominated branches are the material cosmetic-convergence concerns.

## Focused revision

One focused review covered the map, locked profile, rules, sheet, slice,
source crosswalk, deterministic routes, and reader-only record.

The required advisory narrative scan before revision reported **high surface
risk** over 3,096 words. Its 114 non-weak hits were dominated by 107 required
Markdown/navigation hits: 15 passage-title-like lines, 91 bold spans, the
heading structure, and the method table. The genuine language signals were
sparse: three `shape` hits, two ornate-verb hits, and two parallelism hits. A
manual narrative audit found concrete action, Howard-grounded tower, corpse,
Taurus, lion, black-lotus, and Zamorian anchors; Conan's suspicion, pride, and
practicality; Taurus's independent competence and vanity; no explanatory
moral; and no dialogue announcing a theme. The two bodily cues concerning
Conan's neck hair are direct source-grounded instinct details paired with
action, not substitutes for it.

No scanner-driven synonym swap was made. `shape` is concrete concealment
language, `marks` is literal evidence or state language, the method
acknowledgements distinguish real branches, and the Markdown headings and bold
stakes are required navigation. After revision the scanner still reported
**high surface risk** over 3,126 words, with the same 107 formatting hits,
three `shape` hits, and two parallelism hits; it also flagged the newly explicit
mechanical word `mark`. The score therefore caused no narrative rewrite.

Three reader-facing clarity changes were made in `slice-01.md`:

1. the `S03` pursuit choice now says that Conan leaves the corpse unread and
   the spear behind;
2. the `S03` examination choice now says that it yields one useful discovery;
   and
3. the `S04` strangling choice now states that its existing mark enables quiet
   identification of a human ambusher.

These changes disclose the accepted consequences before commitment. They add
no benefit, cost, state, test, passage, or edge. The canonical mark routes,
prepared spear route, costly pursuit route, both locked-result routes, and the
reader-only spear route reproduce their recorded destinations and final
states. The edge inventory remains 27. No material defect was found in
Fortune timing, natural-result handling, state production or consumption,
Exposure updates, passage links, the single tactical exchange, the quick
rules, or the adventure sheet, so those two reader files were left unchanged.

## Residual questions

1. **`S01` waiting remains dominated.** Its required +1 Exposure and
   reconvergence at `S03` are locked by the approved profile and the prepared
   route. A future profile-level review must decide whether waiting earns
   information or position, or whether the branch should be removed. This task
   adds neither hidden benefit nor new state.
2. **`S03` pursuit remains dominated.** The revision makes the foregone
   discovery explicit, but does not make immediate pursuit mechanically useful.
   Any payoff, cost for examination, or changed Taurus position would alter the
   approved graph or mechanics and needs a later design decision.
3. **The `S03` Exposure-threshold reference in the Task 5 sketch is not
   reachable.** The audit follows the accepted profile and actual reachable
   readers rather than adding dead threshold text. The plan wording can be
   corrected in a later planning record without changing this slice.
4. **Human evidence is still absent.** A human paper-and-dice session and blind
   readers both familiar and unfamiliar with Howard remain the highest-value
   tests. The 34-second Codex run supports procedure consistency only.
5. **Coverage remains deliberately partial.** Disadvantage, WIL and Fortune
   tests, margin-specific branches, recovery, and a Stamina-zero route are not
   exercised here. Expanding solely to cover them would exceed the
   representative slice.
6. **Retained state needs a later consumer.** `S14` deliberately preserves the
   exact sheet for an upper-tower continuation. That continuation, its schema,
   deterministic tooling, and AI facilitation remain separate increments.
